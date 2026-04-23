import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.graph import get_graph

load_dotenv()

_CYAN = "\033[96m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _print_banner():
    print(f"""
{_CYAN}{_BOLD}
 █████╗ ██╗   ██╗████████╗ ██████╗ ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║
███████║██║   ██║   ██║   ██║   ██║███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║
██╔══██║██║   ██║   ██║   ██║   ██║╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
{_RESET}
{_GREEN}Social-to-Lead Agentic Workflow  |  Powered by LangGraph + Ollama{_RESET}
{_YELLOW}Type your message and press Enter.  Type 'exit' to quit.{_RESET}
""")


def run():
    _print_banner()
    graph = get_graph()

    state = {
        "messages": [],
        "intent": "",
        "collecting_lead": False,
        "lead_info": {},
        "lead_captured": False,
        "rag_context": "",
    }

    print(f"{_GREEN}Aria:{_RESET}  Hi there! 👋 I'm Aria, your AutoStream assistant. How can I help you today?\n")

    while True:
        try:
            user_input = input(f"{_CYAN}You:{_RESET}  ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            print(f"\n{_GREEN}Aria:{_RESET}  Thanks for chatting! Have an amazing day. 🎬\n")
            break

        state["messages"] = state["messages"] + [HumanMessage(content=user_input)]

        try:
            state = graph.invoke(state)
        except Exception as e:
            print(f"\n[ERROR] Agent encountered an issue: {e}\n")
            continue

        last_msg = state["messages"][-1]
        content = getattr(last_msg, "content", str(last_msg))

        print(f"\n{_GREEN}Aria:{_RESET}  {content}\n")

        if state.get("lead_captured"):
            print(f"{_YELLOW}[System] Lead capture complete. Starting fresh session...{_RESET}\n")
            state = {
                "messages": [],
                "intent": "",
                "collecting_lead": False,
                "lead_info": {},
                "lead_captured": False,
                "rag_context": "",
            }


if __name__ == "__main__":
    run()