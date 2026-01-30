# Topic 3 Tools Table of Contents

---

## 1. Ollama Server running Llama3.2-1B

- [MMLU Eval File 1](./llama_mmlu_eval1.py), [MMLU Eval File 2](./llama_mmlu_eval2.py)

- [Ollama MMLU Eval File 1](./ollama_eval1.py), [Ollama MMLU Eval File 2](./ollama_eval2.py)

- [Bash File to run MMLU Eval](./runllama.bash), [Bash File to run Ollama MMLU Eval](./runOllama.bash)

### Llama 3.2-1B Runtimes w/o Ollama
-----------------------------------

Sequential Execution     : 21.30 real         8.01 user         3.80 sys    
Parallel Execution       : 15.23 real         9.14 user         4.28 sys    


### Llama 3.2-1B Runtimes w/ Ollama
-----------------------------------

Sequential Execution     : 40.30 real         3.30 user         0.56 sys  
Parallel Execution       : 27.62 real         3.62 user         0.71 sys  

### Observations
What I observed from the executions of these programs was...