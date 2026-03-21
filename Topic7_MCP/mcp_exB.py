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

drill1_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "search_papers_by_relevance",
        "arguments": {
            "keyword": "large language model agents",
            "fields": "title,abstract,year,authors",
            "limit": 5
        }
    }
}

result = requests.post(
    "https://asta-tools.allen.ai/mcp/v1",
    headers=headers,
    json=drill1_payload
)

#print("Status code:", result.status_code)
#print("Raw response:", result.text)

data = json.loads(result.text.split("data:")[1].strip())

print("================== Drill 1 - Search Papers ====================\n")
for i, paper in enumerate(data['result']['content']):
    info = json.loads(paper['text'])
    print(f"{i + 1}. {info['title']} ({info['year']})\n")
print("\n\n")





drill2_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_citations",
        "arguments": {
            "paper_id": "ARXIV:1810.04805",
            "fields": "title,year,authors",
            "limit": 10,
            "publication_date_range": "2023-01-01:"
        }
    }
}

result = requests.post(
    "https://asta-tools.allen.ai/mcp/v1",
    headers=headers,
    json=drill2_payload
)

#print("Status code:", result.status_code)
#print("Raw response:", result.text)

data = json.loads(result.text.split("data:")[1].strip())

print("================== Drill 2 - Get Citations ====================\n")
print(f"Result Count: {len(data['result']['content'])}\n")
for i, paper in enumerate(data['result']['content']):
    info = json.loads(paper['text'])
    print(f"{i + 1}. {info['citingPaper']['title']} ({info['citingPaper']['year']})\n")
print("\n\n")





drill3_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_paper",
        "arguments": {
            "paper_id": "ARXIV:2210.03629",
            "fields": "title,year,authors,references",
        }
    }
}

drill3_batchPayload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_paper_batch",
        "arguments": {
            "paper_id": "",
            "fields": "title,year,authors,references",
        }
    }
}

result = requests.post(
    "https://asta-tools.allen.ai/mcp/v1",
    headers=headers,
    json=drill3_payload
)

#print("Status code:", result.status_code)
#print("Raw response:", result.text)

data = json.loads(result.text.split("data:")[1].strip())
text = data['result']['content'][0]
info = json.loads(text['text'])

refs = [paper['paperId'] for paper in info['references'] if paper['paperId'] is not None]

drill3_batchPayload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_paper_batch",
        "arguments": {
            "ids": refs,
            "fields": "title,year",
        }
    }
}

result = requests.post(
    "https://asta-tools.allen.ai/mcp/v1",
    headers=headers,
    json=drill3_batchPayload
)

#print("Status code:", result.status_code)
#print("Raw response:", result.text)

data = json.loads(result.text.split("data:")[1].strip())

references = []
for paper in data['result']['content']:
    info = json.loads(paper['text'])
    references.append({'title': info['title'], 'year': info['year']})

refs_sorted = sorted(references, key=lambda r: r['year'] or 0)

print("================== Drill 3 - Get References ====================\n")
print(f"Result Count: {len(data['result']['content'])}\n")

for i, ref in enumerate(refs_sorted, 1):
    print(f"{i}. {ref['title']} ({ref['year']})")
print("\n\n")