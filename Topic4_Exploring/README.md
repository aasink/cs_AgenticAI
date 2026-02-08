# Topic 4 Exploring Table of Contents

---

## 3. Tool Node & React Agent Examples

- [Tool Node Agent](./toolnode_example.py)

- [React Agent Agent](./react_agent_example.py)

![Tool Node Graph](./langchain_manual_tool_graph.png)

![React Agent Agent](./langchain_conversation_graph.png)

![React Agent](./langchain_react_agent.png)

What features of Python does ToolNode use to dispatch tools in parallel?  What kinds of tools would most benefit from parallel dispatch?  
The python features that tool node uses to dispatch tools in parallel are the asynchronous features so that they can run multiple tool calls at the same time to speed up the time it takes. The kinds of tools that would most benefit from parallel dispatch would be any tools that dont rely on others tools for input and any sort of tools that are fetching something from somewhere like a database or the internet.

How do the two programs handle special inputs such as "verbose" and "exit"?  
The way that the programs handle special inputs is they set the command state equal to the special input and then in the router function the special command flag is set for verbose if needed and then is sent back to the user input or ends depending on the special input.

Compare the graph diagrams of the two programs.  How do they differ if at all?  
The way that the  graph diagrams differ is that the call model then the model calling tools is not there in the react agent one and instead the tool calling all happens in the react agent graph.

What is an example of a case where the structure imposed by the LangChain react agent is too restrictive and you'd want to pursue the toolnode approach?  
An example of a case where the structure imposed by the lang chain react agent is too restrictive and you'd want to pursue the tool node approach is anytime you want that concurrency that tool node does where the react agent does not do that so an example would be something like an agent that searches the web on multiple sites for sources to use for comparisons. 

## 5. 2-hour Agent Project

- [2 Hour Youtube Transcript Agent](./agent.py)
