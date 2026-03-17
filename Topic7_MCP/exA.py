import requests, os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("ASTA_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "x-api-key": api_key
}
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}
resp = requests.post(
    "https://asta-tools.allen.ai/mcp/v1",
    headers=headers,
    json=payload
)

print("Status code:", resp.status_code)
print("Raw response:", resp.text)

data = json.loads(resp.text.split("data:")[1].strip())
print(data["result"]["tools"])

for tool in data["result"]["tools"]:
    desc = tool['description'].split('\n')[1].strip()
    inSchema = tool['inputSchema']

    print(inSchema)

    print(f"Tool: {tool['name']} \nDescription: {desc}")
    print(f"Required: ")
    for r in inSchema['required']: print(f"{r} ")#({})")
    print()