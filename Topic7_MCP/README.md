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

- [Exercise D Markdown Report](./outputs/exD_report.md)

### Closing Discussion

You wrote tool schemas by hand in concept, then saw MCP provide them dynamically. What does this automation buy you? What does it cost (complexity, new failure modes)?
The benefit of having the automation is that it works even when tools change because it can update automatically. The cost is that you are relying on the tool server to have correct info for all their tools. The failure modes that are new would mabye be the llm not being able to properly create a query from the schema given to it.

The Asta tools return rich JSON. How did you decide what to include in the context window and what to discard? What happened to response quality when you passed everything vs. a summary?
The way i decided what to include was just be seeing what I was trying to achieve then add those fields to the query. Passing everything meant that the model picked up all the information and so it wasnt as specific when answering or creating a response.

In Exercise D, you controlled the tool-calling order. What would it take to let the LLM decide the order? What could go wrong?
It would require giving the llm the tools and letting it call when given the prompt, this could work, the potentially go wrong if the llm decides to continue to call certain parts and would extend the amount of calls needed to get the information that it needs.

MCP is a relatively young standard. What would you want a mature MCP ecosystem to offer that is not available today?
Something that I think I would want a mature mcp ecosystem to offer that is not available today is potentially a way to monitor tool call chains. 

## 2. Agent-to-Agent Communication with A2A

### Exercise: A2A Trivia Tournament

- [Trivia Bot Code](./a2a_agent_template.py)

- [Trivia Bot DryRun Output](./a2a_output.png)

How well did TF-IDF matching perform? What would work better? How might this compare to semantic embeddings?
TF-IDF works well when there is simple keyword overlpa but fails on short questions. This compares to semantic embeddings is that the embeddings works better since it is able to caputre more iinformation and helps provide better routing.

### Discussion Questions

MCP vs A2A: How is sending a task to another agent different from calling an MCP tool? What can an agent do that a tool cannot?
Sending a task to another agent means the task can be interpreted differently as determined by a specialized agent whereas the tool will work as the tool has always worked. The agent can interpret the task while the tool with just do the task it was designed to do.

Discovery: We used a central registry. What are the alternatives? What are the tradeoffs of centralized vs decentralized discovery?
The alternatives could be a peer to peer system or soem way of the agents announcing themselves. The tradeoffs of centralized vs decentralized discovery is that with centralized the central server is the point of failure if that goes down so do all the agents relying on it and for decentralized it is harder to set up and connect the agents.

System prompts as strategy: How much did the system prompt matter for scoring? Could you craft a prompt that is good at all categories while still being funny on off-topic questions?
The system prompt mattered alot, yes it is possible to craft a prompt that is good at all categories while still being funny on off topic questions but if it is good at all categores there isnt going to be much off topic questions for it to be funny.

Smart routing: TF-IDF matched questions to agents based on text overlap. What would happen with semantic embeddings instead? What if agents could self-report confidence?
What would happen with semantic embeddings instead of tf-idf would mean that routing would be more accurate because the context would be better understood rather than just relying on keywords. If agents could report confidence then the system could do almost like a mixture of experts type system where they vote or choose the most confident agent.

Trust and reliability: In a real multi-agent system, how would you handle an agent that returns bad data? What if an agent is slow or goes offline mid-task?
The way to handle an agent that returns bad data would to have some sort of verification agent or model or soemthign to check the data. If an agent is lsow or offline then the best solution would be to have a connection timeout and then either a fallback agent or just return an error to try agan later.

Scaling: What would break if there were 1,000 agents instead of 20? What architectural changes would you need?
If there were a 1000 agents instead of 20 then the routing would potentially have issues and the registry would also have issues. The changes that would be necessary would be improvements to the routing and registry and better way to go through the agents.