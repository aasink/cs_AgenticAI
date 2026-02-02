# Topic 3 Tools Table of Contents

---

## 1. Ollama Server running Llama3.2-1B

- [MMLU Eval File 1](./llama_mmlu_eval1.py), [MMLU Eval File 2](./llama_mmlu_eval2.py)

- [Ollama MMLU Eval File 1](./ollama_eval1.py), [Ollama MMLU Eval File 2](./ollama_eval2.py)

- [Bash File to run MMLU Eval](./runllama.bash), [Bash File to run Ollama MMLU Eval](./runOllama.bash)

### Llama 3.2-1B Runtimes & Accuracy w/o Ollama
-----------------------------------------------

Sequential Execution     : 21.30 real         8.01 user         3.80 sys   
Parallel Execution       : 15.23 real         9.14 user         4.28 sys    
- Topic 1 Accuracy (Computer Security) : 57.99%
- Topic 2 Accuracy (College Computer Science) : 25%

### Llama 3.2-1B Runtimes & Accuracy w/ Ollama
------------------------------------------------

Sequential Execution     : 40.30 real         3.30 user         0.56 sys  
Parallel Execution       : 27.62 real         3.62 user         0.71 sys  
- Topic 1 Accuracy (Computer Security) : 39%
- Topic 2 Accuracy (College Computer Science) : 22%

### Observations
What I observed from the executions of these programs was that Ollama took twice as long to run and also did not have as good accuracy compared to running it without Ollama. Although what is interesting the user and system time was much smaller with Ollama. Something I think that may have contributed to the slower runtimes was that Ollama was using just the 3.2-1B model while the hugging face version was using the instruct version of the model. In addition, since Ollama had to send a request for every question that it was asked it think was mostly responsible for the increased time.

## 2. GPT 4o Mini Test 

- [GPT Test File](./gpt4omini_test.py)

```python  
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say: Working!"}],
 max_tokens=5
```

### Explanation of Code
The first line in this code creates a client object for Open AI so that you can send requests to Open AI. The second line in the code creates teh chat request to Open AI with the parameters for which model it should use and  the message history as well as the max number of tokens to respond with.


## 3. Manual Tool Handling - Calculator Tool

- [Manual Tool Handling File](./manual-tool-handling.py)

- [Manual Tool Handling Example Outputs](./outputs/output3.txt)

## 4. LangGraph Tool Handling

- [LangGraph Tool Handling File](./langgraph-tool-handling.py)

- [LangGraph Tool Handling Example Outputs](./outputs/output4.txt)

Can you create a query that uses all your tools?  Can you get seqential chaining to hit the 5 turn limit in the outer loop?  
Yes I was able to create queries that used all my tools and was able to use all of them to hit the 5 turn limit in the outer loop, though this was difficult to do, because as I add more tool calls to the chain, the more the model grouped the tools calls per iteration.

## 5. Conversations - LangGraph Nodes & Edges 

- [LangGraph Conversation File](./langgraph-conversation.py)

## 6. Question
Where is there an opportunity for parallelization in your agent that is not yet being taken advantage of?
