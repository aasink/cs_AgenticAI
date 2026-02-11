# Topic 5 RAG Table of Contents

---

## 1. Open Model RAG vs. No RAG Comparison

- [RAG Pipeline ipynb](./manual_rag_pipeline_universal_updated.ipynb)

- [RAG v. No RAG Model T Output](./outputs/e1_modelT.txt)

- [RAG v. No RAG Congressional Record Output](./outputs/e1_CR.txt)

Does the model hallucinate specific values without RAG?

Does RAG ground the answers in the actual manual?

Are there questions where the model's general knowledge is actually correct?

## 2. Open Model + RAG vs. Large Model Comparison

- [GPT 4o Mini Code](./ragless.py)

- [GPT 4o Mini Model T Output](./outputs/e2_modelT.txt)

- [GPT 4o Mini Congressional Record Output](./outputs/e2_CR.txt)

Does GPT 4o Mini do a better job than Qwen 2.5 1.5B in avoiding hallucinations?

Which questions does GPT 4o Mini answer correctly?  Compare the cut-off date of GPT 4o Mini pre-training and the age of the Model T Ford and Congressional Record corpora.

## 3. Open Model + RAG vs. State-of-the-Art Chat Model

- [GPT 5.2 Model T Output](https://chatgpt.com/share/698bf0c0-29ac-8000-b9d5-37315eb1cc7a)

- [GPT 5.2 Congressional Record Output](https://chatgpt.com/share/698bf197-4b38-8000-afe4-ea046e13be9d)

Where does the frontier model's general knowledge succeed?

When did the frontier model appear to be using live web search to help answer your questions?

Where does your RAG system provide more accurate, specific answers?

What does this tell you about when RAG adds value vs. when a powerful model suffices?

## 4. Effect of Top-K Retrieval Count

At what point does adding more context stop helping?

When does too much context hurt (irrelevant information, confusion)?

How does k interact with chunk size?

## 5. Handling Unanswerable Questions

Does the model admit it doesn't know?

Does it hallucinate plausible-sounding but wrong answers?

Does retrieved context help or hurt? (Does irrelevant context encourage hallucination?)

## 6. Query Phrasing Sensitivity

Which phrasings retrieve the best chunks?

Do keyword-style queries work better or worse than natural questions?

What does this tell you about potential query rewriting strategies?

## 7. Chunk Overlap Experiment

Does higher overlap improve retrieval of complete information?

What's the cost? (Index size, redundant information in context)

Is there a point of diminishing returns?

## 8. Chunk Size Experiment

How does chunk size affect retrieval precision (relevant vs. irrelevant content)?

How does it affect answer completeness?

Is there a sweet spot for your corpus?

Does optimal size depend on the type of question?

## 9. Retrieval Score Analysis

When is there a clear "winner" (large gap between #1 and #2)?

When are scores tightly clustered (ambiguous)?

What score threshold would you use to filter out irrelevant results?

How does score distribution correlate with answer quality?

## 10. Prompt Template Variations

Which prompt produces the most accurate answers?

Which produces the most useful answers?

Is there a trade-off between strict grounding and helpfulness?

## 11. Cross-Document Synthesis

Can the model successfully combine information from multiple chunks?

Does it miss information that wasn't retrieved?

Does contradictory information in different chunks cause problems?