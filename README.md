# AutoStream – Social-to-Lead Agent

This project is a conversational AI agent built for the ServiceHive Inflx ML Intern assignment.  
It simulates a SaaS assistant that answers user queries and converts high-intent users into leads.

## How to Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create a .env file:

GEMINI_API_KEY=your_api_key_here

Run:
python main.py

#Architecture 
I used LangGraph because the agent follows a structured flow: intent detection → response → lead collection → tool execution. LangGraph makes this easy to manage using nodes.

State is stored in a shared object (AgentState) that keeps messages, intent, and lead progress. The CLI loop handles multiple turns, while the graph runs one step per input, which avoids recursion issues and keeps behavior predictable.

# WhatsApp Integration 
This agent can be connected to WhatsApp using webhooks.
When a user sends a message, WhatsApp sends it to a backend server. The server loads the user’s state, runs the agent, stores updated state, and sends the response back. A database like Redis can be used to store conversation state across messages.