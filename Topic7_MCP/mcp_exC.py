import requests
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
asta_key = os.getenv("ASTA_API_KEY")


openai_client = OpenAI(api_key=openai_key)

ASTA_URL = "https://asta-tools.allen.ai/mcp/v1"
asta_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "x-api-key": asta_key
}



def asta_post(method, params):
    payload = {
        "jsonrpc": "2.0", 
        "id": 1, 
        "method": method, 
        "params": params
    }
    resp = requests.post(
        ASTA_URL, 
        headers = asta_headers, 
        json = payload
        )
    return json.loads(resp.text.split("data:")[1].strip())

def get_asta_tools():
    data = asta_post("tools/list", {})
    tools = []
    for tool in data["result"]["tools"]:
        tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }
        })
    return tools

def call_asta_tool(name, arguments):
    print(f"\n[TOOL CALL] {name}")
    print(f"[ARGUMENTS] {json.dumps(arguments, indent=2)}")
    try:
        data = asta_post("tools/call", {"name": name, "arguments": arguments})
        contents = data["result"]["content"]
        results = []
        for item in contents:
            if item["type"] == "text":
                try:
                    parsed = json.loads(item["text"])
                    results.append(json.dumps(parsed, indent=2))
                except json.JSONDecodeError:
                    results.append(item["text"])
        return "\n---\n".join(results)
    except Exception as e:
        return f"Error calling tool {name}: {str(e)}"

def chat(user_message, messages, tools):
    messages.append({"role": "user", "content": user_message})

    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        messages.append(msg)
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = call_asta_tool(name, arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })



SYSTEM_PROMPT = """You are a research assistant with access to Semantic Scholar via the Asta API.
You help users find academic papers, explore authors, trace citations, and summarize research.
Always use the available tools to fetch real data before answering."""

def main():
    tools = get_asta_tools()
    print(f"Loaded {len(tools)} tools: {[t['function']['name'] for t in tools]}\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Research Chatbot ready. Type 'quit' to exit.\n")
    while True:
        query = input("YOU: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        print()
        answer = chat(query, messages, tools)
        print(f"\nASSISTANT: {answer}\n")


if __name__ == "__main__":
    main()