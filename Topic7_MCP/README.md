# Topic 7 MCP Table of Contents

---

## 1. MCP Tool Integration with Ai2 Asta

### Exercise A: Discover the Asta Tools

- [Excercise A Code](./mcp_exA.py)

- [Exercise A Output](./outputs/outputA.png)

Which tool would you use to find all papers about "transformer attention mechanisms"? 
The tool that I would use to find all papers about transformer attention mechanisms would be the search papers by relevance.

Which would you use to find who else published in the same area as a specific author?
The tool that I would use to find who else published in the same area as a specific author would be the get citation or get author papers and then teh search by relevance.

### Exercise B: Direct Asta Tool Calls

- [Excercise B Code](./mcp_exB.py)

- [Exercise B Output](./outputs/outputB.png)

What differences did you notice in the structure of results across the three tools? How did you handle the JSON returned inside the content[0]["text"] field?
There werent many differences from the structure, they had the fields that were included in the request and the way that i handled the json returned inside that
was to parse through and just pull out the fields that I needed to print.

### Exercise C: Asta-Powered Research Chatbot

- [Excercise C Code](./mcp_exC.py)

- [Exercise C Output 1](./outputs/outputC1.png)
- [Exercise C Output 2](./outputs/outputC2.png)
- [Exercise C Output 3](./outputs/outputC3.png)
- [Exercise C Output 4](./outputs/outputC4.txt)

What changed compared to calling tools manually in Exercise B? You wrote almost no tool-specific code — the schema came from the server. The chatbot would work identically if Asta added new tools tomorrow. That is the core value of MCP.

### Exercise D: Citation Network Explorer Agent

- [Excercise D Code](./mcp_exD.py)

- [Exercise D Output](./outputs/outputD.png)

### Closing Discussion

You wrote tool schemas by hand in concept, then saw MCP provide them dynamically. What does this automation buy you? What does it cost (complexity, new failure modes)?

The Asta tools return rich JSON. How did you decide what to include in the context window and what to discard? What happened to response quality when you passed everything vs. a summary?

In Exercise D, you controlled the tool-calling order. What would it take to let the LLM decide the order? What could go wrong?

MCP is a relatively young standard. What would you want a mature MCP ecosystem to offer that is not available today?

## 2. Agent-to-Agent Communication with A2A

### Exercise: A2A Trivia Tournament

- [Trivia Bot Code](./a2a_agent_template.py)

How well did TF-IDF matching perform? What would work better? How might this compare to semantic embeddings?

### Discussion Questions

MCP vs A2A: How is sending a task to another agent different from calling an MCP tool? What can an agent do that a tool cannot?

Discovery: We used a central registry. What are the alternatives? What are the tradeoffs of centralized vs decentralized discovery?

System prompts as strategy: How much did the system prompt matter for scoring? Could you craft a prompt that is good at all categories while still being funny on off-topic questions?

Smart routing: TF-IDF matched questions to agents based on text overlap. What would happen with semantic embeddings instead? What if agents could self-report confidence?

Trust and reliability: In a real multi-agent system, how would you handle an agent that returns bad data? What if an agent is slow or goes offline mid-task?

Scaling: What would break if there were 1,000 agents instead of 20? What architectural changes would you need?