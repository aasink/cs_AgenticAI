# Topic 4 Exploring Table of Contents

---

## 3. Tool Node & React Agent Examples

What features of Python does ToolNode use to dispatch tools in parallel?  What kinds of tools would most benefit from parallel dispatch?  
The python features that tool node uses to dispatch tools in parallel are...  The kinds of tools that would most benefit from parallel dispatch would be ...

How do the two programs handle special inputs such as "verbose" and "exit"?  
The way that the programs handle special inputs is they set the command state equal to the special input and then in the router function the special command flag is set for verbose if needed and then is sent back to the user input or ends depending on the special input.

Compare the graph diagrams of the two programs.  How do they differ if at all?  
The way that the  graph diagrams differ is that the call model then the model calling tools is not there in the react agent one and instead the tool calling all happens in the react agent graph.

What is an example of a case where the structure imposed by the LangChain react agent is too restrictive and you'd want to pursue the toolnode approach?  
An example of a case where the structure imposed by the lang chain react agent is too restrictive and you'd want to pursue the tool node approach is ...