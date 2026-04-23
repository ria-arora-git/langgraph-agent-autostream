import os
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from utils.rag import retrieve, get_full_context
from utils.intent import classify_intent
from tools.lead_capture import mock_lead_capture
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str
    collecting_lead: bool
    lead_info: dict
    lead_captured: bool
    rag_context: str

_BASE_SYSTEM = """You are Aria, an AI assistant for AutoStream.

STRICT RULES:
- Be VERY concise (2–3 lines max)
- Answer directly
- Do NOT give long introductions
- Do NOT repeat yourself
- Use bullet points when listing

Knowledge:
{context}
"""

_LEAD_COLLECTION_SYSTEM = """Collect:
1. Name
2. Email
3. Platform

Current: {lead_info}

Ask ONLY for the next missing field.
"""

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def _run_llm(system, messages):
    history = "\n".join([m.content for m in messages])
    prompt = f"{system}\n\nConversation:\n{history}"

    response = model.generate_content(prompt)

    return AIMessage(content=response.text.strip())


def router_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    last_human = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
        ""
    )

    if state.get("collecting_lead") and not state.get("lead_captured"):
        return {**state, "intent": "collecting_lead"}

    intent = classify_intent(last_human)

    rag_ctx = ""
    if intent in ("product_inquiry", "high_intent_lead"):
        rag_ctx = retrieve(last_human)

    if intent == "high_intent_lead":
        return {
            **state,
            "intent": intent,
            "rag_context": rag_ctx,
            "lead_info": state.get("lead_info", {}),
            "collecting_lead": state.get("collecting_lead", False),
            "lead_captured": state.get("lead_captured", False)
        }

    return {**state, "intent": intent, "rag_context": rag_ctx}


def greeting_node(state: AgentState) -> AgentState:
    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content="Hi! I can help with pricing, features, or getting started.")
        ]
    }


def product_qa_node(state: AgentState) -> AgentState:
    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content=state["rag_context"])
        ]
    }


def lead_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    lead_info = dict(state.get("lead_info") or {})

    last = messages[-1].content.strip()

    step = lead_info.get("step", "name")

    if step == "name":
        if "name" not in lead_info:
            lead_info["step"] = "name_asked"
            return {
                **state,
                "messages": messages + [AIMessage(content="What is your name?")],
                "lead_info": lead_info,
                "collecting_lead": True
            }

        else:
            lead_info["step"] = "email"

    if step == "name_asked":
        lead_info["name"] = last
        lead_info["step"] = "email"

    if lead_info.get("step") == "email":
        return {
            **state,
            "messages": messages + [AIMessage(content="What is your email?")],
            "lead_info": {**lead_info, "step": "email_asked"},
            "collecting_lead": True
        }

    if lead_info.get("step") == "email_asked":
        lead_info["email"] = last
        lead_info["step"] = "platform"

    if lead_info.get("step") == "platform":
        return {
            **state,
            "messages": messages + [
                AIMessage(content="Which platform do you create content on? (YouTube/Instagram/TikTok)")
            ],
            "lead_info": {**lead_info, "step": "platform_asked"},
            "collecting_lead": True
        }

    if lead_info.get("step") == "platform_asked":
        lead_info["platform"] = last

    mock_lead_capture(
        name=lead_info["name"],
        email=lead_info["email"],
        platform=lead_info["platform"]
    )

    return {
        **state,
        "messages": messages + [
            AIMessage(content="Thanks! We will reach out to you soon.")
        ],
        "lead_info": {},
        "collecting_lead": False,
        "lead_captured": True
    }

def route_by_intent(state: AgentState):
    if state.get("lead_captured"):
        return "__end__"

    intent = state.get("intent")

    if intent in ("collecting_lead", "high_intent_lead"):
        return "lead"

    if intent == "greeting":
        return "greeting"

    return "product_qa"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("greeting", greeting_node)
    graph.add_node("product_qa", product_qa_node)
    graph.add_node("lead", lead_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "greeting": "greeting",
            "product_qa": "product_qa",
            "lead": "lead",
            "__end__": END,
        }
    )

    graph.add_edge("greeting", END)
    graph.add_edge("product_qa", END)

    graph.add_edge("lead", END)

    return graph.compile()

_compiled_graph = None

def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph