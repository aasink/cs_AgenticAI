# Topic 8 Fine Tuning Table of Contents

---

- [Fine Tuning Code](./finetune.py)

- [Fine Tuned Model Output](./outputs/output1.png)


Before vs. after: What specific improvements did you observe? Did the model learn SQL syntax, schema grounding, or both? What was the change in accuracy on the 200 held-out test questions? How well did it do on the additional manual test questions (Step 7)?

Hint: on the 200 in-distribution test questions, accuracy typically improves from ~37% (base) to ~87% (fine-tuned). The Step 7 questions use novel schemas and may show lower accuracy.

RAG comparison: Imagine you had a RAG system with 1,000 (question, SQL) pairs in a vector database. For which of the test questions above would RAG work well? For which would it struggle? Why?

Error analysis: When the fine-tuned model gets a query wrong, how does it fail? Wrong column names? Wrong SQL syntax? Wrong logic? Each failure mode tells you something different about what the model learned.