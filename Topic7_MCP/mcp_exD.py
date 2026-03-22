import requests
import os
import json
import sys
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

def parse_content(data):
    results = []
    for item in data["result"]["content"]:
        if item["type"] == "text":
            try:
                results.append(json.loads(item["text"]))
            except json.JSONDecodeError:
                results.append(item["text"])
    return results

def call_tool(name, arguments):
    print(f"  [FETCHING] {name}({json.dumps(arguments)})", file=sys.stderr, flush=True)
    try:
        data = asta_post("tools/call", {"name": name, "arguments": arguments})
        return parse_content(data)
    except Exception as e:
        print(f"  [ERROR] {name}: {e}", file=sys.stderr)
        return []

def get_seed_paper(paper_id):
    """Retrieve full metadata for the seed paper."""
    results = call_tool("get_paper", {
        "paper_id": paper_id,
        "fields": "title,abstract,year,authors,fieldsOfStudy,citationCount"
    })
    return results[0] if results else {}

def get_top_references(paper_id):
    results = call_tool("get_paper", {
        "paper_id": paper_id,
        "fields": "references.title,references.year,references.citationCount,references.abstract,references.paperId"
    })
    if not results:
        return []
    refs = results[0].get("references", [])
    refs = [r for r in refs if r.get("paperId") and r.get("citationCount") is not None]
    refs_sorted = sorted(refs, key=lambda r: r.get("citationCount") or 0, reverse=True)
    return refs_sorted[:5]

def get_citing_papers(paper_id, year):
    results = call_tool("get_citations", {
        "paper_id": paper_id,
        "fields": "title,year,abstract,authors,citationCount",
        "limit": 20,
        "publication_date_range": f"{year - 3}-01-01:{year}-12-31"
    })
    citing = [r for r in results if isinstance(r, dict) and r.get("title")]
    citing_sorted = sorted(citing, key=lambda r: r.get("citationCount") or 0, reverse=True)
    return citing_sorted[:5]

def get_author_other_works(authors):
    author_profiles = []
    for author in authors:
        author_id = author.get("authorId")
        if not author_id:
            continue
        results = call_tool("get_author_papers", {
            "author_id": author_id,
            "paper_fields": "title,year,citationCount,abstract",
            "limit": 10
        })
        papers = [r for r in results if isinstance(r, dict) and r.get("title")]
        papers_sorted = sorted(papers, key=lambda p: p.get("citationCount") or 0, reverse=True)
        top = papers_sorted[0] if papers_sorted else None
        author_profiles.append({
            "name": author.get("name"),
            "top_paper": top
        })
    return author_profiles

def generate_report(seed, top_refs, citing, author_profiles, paper_id):
    print("  [GENERATING] Writing markdown report...", file=sys.stderr, flush=True)

    context = f"""
SEED PAPER:
Title: {seed.get('title')}
Year: {seed.get('year')}
Authors: {', '.join(a['name'] for a in seed.get('authors', []))}
Fields: {', '.join(seed.get('fieldsOfStudy') or [])}
Citations: {seed.get('citationCount')}
Abstract: {seed.get('abstract')}

TOP 5 REFERENCES (by citation count):
{json.dumps(top_refs, indent=2)}

TOP 5 RECENT CITING PAPERS (2022-2025):
{json.dumps(citing, indent=2)}

AUTHOR PROFILES (most notable other work):
{json.dumps(author_profiles, indent=2)}
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research analyst. Write clear, structured academic markdown reports."},
            {"role": "user", "content": f"""Using the following research data, write a structured markdown report with these exact sections:

1. A one-paragraph **Summary** of the seed paper
2. A **Foundational Works** section listing the 5 key references with a sentence on each
3. A **Recent Developments** section listing 5 citing papers with a sentence on each
4. An **Author Profiles** section with each author's most notable other work
5. A **Research Gaps** section identifying open problems based on the references and citations

Data:
{context}"""}
        ],
        max_tokens=2000
    )
    return response.choices[0].message.content

def main():
    print("Citation Network Explorer Agent")

    if len(sys.argv) > 1:
        paper_id = sys.argv[1] 
    else:
        print("Error: No seed paper provided.\n\nProvide seed paper.\n\nExample Command: python mcp_exD.py ARXIV:2210.03629")
        sys.exit(1)
    
    print(f"\nBuilding citation neighborhood for: {paper_id}\n", file=sys.stderr)

    # ordered pipeline — each step may depend on previous results
    print("Fetching seed paper metadata...", file=sys.stderr)
    seed = get_seed_paper(paper_id)
    if not seed:
        print("ERROR: Could not retrieve seed paper.", file=sys.stderr)
        sys.exit(1)
    print()

    print("Fetching top references...", file=sys.stderr)
    top_refs = get_top_references(paper_id)
    print()

    print("Fetching recent citing papers...", file=sys.stderr)
    citing = get_citing_papers(paper_id, seed.get("year"))
    print()

    print("Fetching author profiles...", file=sys.stderr)
    author_profiles = get_author_other_works(seed.get("authors", []))
    print()

    print("Generating report...\n", file=sys.stderr)
    report = generate_report(seed, top_refs, citing, author_profiles, paper_id)
    print()

    # print report to stdout
    print(f"# Citation Neighborhood Report\n")
    print(f"**Seed Paper:** {paper_id}  ")
    print(f"**Generated:** {__import__('datetime').date.today()}\n")
    print("---\n")
    print(report)

if __name__ == "__main__":
    main()