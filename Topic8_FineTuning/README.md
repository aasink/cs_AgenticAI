# Topic 8 Fine Tuning Table of Contents

---

- [Fine Tuning Code](./finetune.py)

- [Fine Tuned Model Output](./outputs/output1.png)


Before vs. after: What specific improvements did you observe? Did the model learn SQL syntax, schema grounding, or both? What was the change in accuracy on the 200 held-out test questions? How well did it do on the additional manual test questions (Step 7)?
The base model did very bad and got 0 right and during all the times i ran it the most it got correct was 1 so any thing was an improvement on it. The finetuned model was able to get about 90% correct which was much better. On the additional questions it did not do that great and only got 1 right of the 5 questions.

RAG comparison: Imagine you had a RAG system with 1,000 (question, SQL) pairs in a vector database. For which of the test questions above would RAG work well? For which would it struggle? Why?
The test questions that would work well with RAG would be the questions that would be included or very similar to a question in that 1000  question sql pairings. It would struggle for the questions that are not included at all in that database, this would be the case because the rag model would have no context that it would need to correctly create the sql query.

Error analysis: When the fine-tuned model gets a query wrong, how does it fail? Wrong column names? Wrong SQL syntax? Wrong logic? Each failure mode tells you something different about what the model learned.
The way that it fails is that it starts adding in extra parts to the query, for most of them,, the first part is fine but then it add extra parts to the query. For the other questions it got wrong it uses different logic to get the query.