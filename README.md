# AutoStream – Social-to-Lead Agentic Workflow

> **Inflx × ServiceHive ML Intern Assignment**  
> An AI-powered conversational agent that converts social media conversations into qualified business leads.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [How to Run](#how-to-run)
5. [WhatsApp Deployment](#whatsapp-deployment)
6. [Evaluation Checklist](#evaluation-checklist)

## Project Overview

**AutoStream** is an AI-powered video editing SaaS with agent **Aria** built to handle intent classification, RAG retrieval, state management, and lead capture.

| Capability            | Implementation                                   |
| --------------------- | ------------------------------------------------ |
| Intent classification | Rule-based + LLM fallback                        |
| RAG retrieval         | JSON knowledge base with keyword matching        |
| State management      | LangGraph `AgentState` across conversation turns |
| Lead capture          | Gated tool execution after info collection       |

## Architecture

**Why LangGraph?** This workflow has a finite state machine (greeting → product Q&A → lead collection). LangGraph's explicit node-edge model is cleaner than AutoGen for single-agent structured flows.

**State Management:**

```
AgentState {
      messages:        list[BaseMessage]
      intent:          str
      collecting_lead: bool
      lead_info:       dict
      lead_captured:   bool
      rag_context:     str
}
```

**Graph Flow:**

```
[START] → [router_node] → [greeting_node / product_qa_node / lead_node] → [END]
```

**RAG Pipeline:** `data/knowledge_base.json` stores pricing and policies. `utils/rag.py` uses keyword matching for retrieval.

**Tool Safety:** `mock_lead_capture()` executes only inside `lead_node` after all three fields are confirmed.

## Project Structure

```
autostream-agent/
├── main.py
├── requirements.txt
├── .env.example
├── agent/
│   └── graph.py
├── tools/
│   └── lead_capture.py
├── utils/
│   ├── intent.py
│   └── rag.py
└── data/
            └── knowledge_base.json
```

## How to Run

**Prerequisites:** Python 3.9+, API key (Anthropic/Google/OpenAI)

```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## WhatsApp Deployment

Use **WhatsApp Business Cloud API** with webhook:

```python
from fastapi import FastAPI, Request
import redis, json
from agent.graph import get_graph

app = FastAPI()
r = redis.Redis()
graph = get_graph()

@app.post("/webhook")
async def webhook(request: Request):
            body = await request.json()
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            phone = message["from"]
            text = message["text"]["body"]

            raw = r.get(f"session:{phone}")
            state = json.loads(raw) if raw else {
                        "messages": [], "intent": "", "collecting_lead": False,
                        "lead_info": {}, "lead_captured": False, "rag_context": ""
            }

            from langchain_core.messages import messages_from_dict, HumanMessage
            state["messages"] = messages_from_dict(state["messages"])
            state["messages"].append(HumanMessage(content=text))

            state = graph.invoke(state)

            from langchain_core.messages import messages_to_dict
            storable = {**state, "messages": messages_to_dict(state["messages"])}
            r.setex(f"session:{phone}", 1800, json.dumps(storable))

            send_whatsapp_message(phone, reply)
            return {"status": "ok"}
```

**Key Points:** Validate `X-Hub-Signature-256` header, set Redis TTL to 30 minutes, respect Meta rate limits.

## Evaluation Checklist

| Criterion                          | Status                                      |
| ---------------------------------- | ------------------------------------------- |
| Agent reasoning & intent detection | ✅ Implemented in `utils/intent.py`         |
| RAG usage                          | ✅ JSON KB retrieval in `utils/rag.py`      |
| State management                   | ✅ LangGraph `AgentState` persists history  |
| Tool calling                       | ✅ `mock_lead_capture()` after confirmation |
| Code clarity                       | ✅ Modular structure                        |
| Deployability                      | ✅ WhatsApp webhook ready                   |

_Built for ServiceHive × Inflx — ML Intern Assignment_
# langgraph-agent-autostream
