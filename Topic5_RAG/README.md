# Topic 5 RAG Table of Contents

---

## 1. Open Model RAG vs. No RAG Comparison

- [RAG Pipeline ipynb](./manual_rag_pipeline_universal_updated.ipynb)

- [RAG v. No RAG Model T Output](./outputs/e1_modelT.txt)

- [RAG v. No RAG Congressional Record Output](./outputs/e1_CR.txt)

Does the model hallucinate specific values without RAG?
Yes the model does hallucinate specific values without RAG, this is particularly noticeable on the question for the spark plug gaps for the model T. Where the model give random values that are in the right ballpark but with the RAG since the pdf to txt is not accurate and it dosent pick up the actual value RAG instead of making the number up uses the gaps for the piston rings instead. But when asked for piston ring gaps the model does hallucinate but with RAG it gives the correct answers.

Does RAG ground the answers in the actual manual?
Similar to the previous questions, yes it does ground the answers in the actual manual but when the answer isnt there like for the spark plug gap question, the model with rag seems to get the next closest value it can find and would instead give me the piston ring gaps, but when asked for the piston ring gaps it does give the correct measurments.

Are there questions where the model's general knowledge is actually correct?
Yes on the sparkplug gap question since the correcct value is not translated into the text file from the pdf, the RAG model uses the piston ring gaps and the model without RAG does provide the correct answer.

## 2. Open Model + RAG vs. Large Model Comparison

- [GPT 4o Mini Code](./ragless.py)

- [GPT 4o Mini Model T Output](./outputs/e2_modelT.txt)

- [GPT 4o Mini Congressional Record Output](./outputs/e2_CR.txt)

Does GPT 4o Mini do a better job than Qwen 2.5 1.5B in avoiding hallucinations?
Yes the model does do a better job than Qwen without RAG at avoiding hallucinations however instead of hallucinating it seems to give the most general answer it can give. For the question about adjusting the carb, gpt 4o mini give the general instructions for adjusting the carb, which would work on more modern carburetors but the instructions for the model T are not the same. It also did not hallucinate on the congressional records questions and instead just said it could not provide information for those dates or gave info as of a date instead of making things up like Qwen did.

Which questions does GPT 4o Mini answer correctly?  Compare the cut-off date of GPT 4o Mini pre-training and the age of the Model T Ford and Congressional Record corpora.
The questions that gpt 4o mini answered correctly were the model T questions although the answers that it gave were more general rather than specifically for the model T like the question about slipping transmission and adjusting the carburetor the answers were in general what to do not specific instructions for the model T. For the congressional record one, the question about the act and the questions about senators was correct but the first two question the model stated that it was unable to anser due to the training date.


## 3. Open Model + RAG vs. State-of-the-Art Chat Model

- [GPT 5.2 Model T Output](https://chatgpt.com/share/698bf0c0-29ac-8000-b9d5-37315eb1cc7a)

- [GPT 5.2 Congressional Record Output](https://chatgpt.com/share/698bf197-4b38-8000-afe4-ea046e13be9d)

Where does the frontier model's general knowledge succeed?
The gpt 5.2's general knowledge succeeded for the questions about the model T it was a lot more specific than gpt 4o mini was and was able to properly answer those questions for the congressional record questions, it was better for the first question but the models knowledge was pretty much on par with gpt 4o mini in terms of the answer that was given since the answers were pretty similar in content.

When did the frontier model appear to be using live web search to help answer your questions?
The model T questions, gpt 5.2 was able to answer with out any web searching since there were no source tags listing a website but for the congressional record questions they all cited various sources mostly from congres. gov. 

Where does your RAG system provide more accurate, specific answers?
For the model T questions they were about the same with the RAG being a bit more specific since that had only one source of info to get information from whereas the frontier model had the entire internet but with the congressional record questions they were about the same since they both had access to the the congressional record except for the last two questions where the record was not needed to answer and the frontier model was a bit more specific while the rag model was a bit more in reference to the record.

What does this tell you about when RAG adds value vs. when a powerful model suffices?
What this tells me about when RAG adds value and when a powerful model is better is that when you want the model to use information that may not be publicly available or any sort of niche topics or very current topics is when you would want RAG and for more well known and less niche topics is where you would probably do better with a powerful model.

## 4. Effect of Top-K Retrieval Count

- [Top-K Retrival Experiment Output](./outputs/e4_output.txt)

At what point does adding more context stop helping?
Around k = 5 is where adding more context seems to stop helping, because before that the model doesnt seem to get all the information or it leaves some of it out but after k = 5 the model doesnt seem to add any more information it is pretty much just giving the same info it gave for k = 5.

When does too much context hurt (irrelevant information, confusion)?
Too much context hurts the response of the model when it starts adding more words that it needs to like when responding to one question it would say 'the service manual recommends' for the smaller k values but for the larger one it started adding way more words to say that like including 'according to the instructions in the context and then still using the same phrase that it was using for the smaller k values so it just started adding unecessary tokens for no reason.

How does k interact with chunk size?
The k interacts with the chunk size by determining how much information is being collected from the embeddings depending on the chunk size the size of the k determines how much information the model needs in order for it to get the most information without having too much extra information.

## 5. Handling Unanswerable Questions\

- [Handling Unanswerable Questions Output](./outputs/e5_output.txt)

Does the model admit it doesn't know?
Sometimes, the first two questions that I asked which were completely off topic and related but not in the corpus, the model said that it was not in the context and tried to help find an answer from the context or recommended additional sources. However for the false premise question, it did not admit and instead made up an answer, as I had asked about using the starter on a 1915 model T and the model answered as if the 1915 model T had a starter but starters were not added until 1919.

Does it hallucinate plausible-sounding but wrong answers?
The answers that it did give wrong answers for did sound very plausible and if you didnt know better it would sound pretty accurate, since I had asked about usage of the starter on 1915 model T when the starter was only added in 1919 but the model still told me that the manual warns against using the starter in certain conditions on the 1915 model T.

Does retrieved context help or hurt? (Does irrelevant context encourage hallucination?)
I think that irrelevant context would encourage hallucination because if that context is similar to what the question is asking but would not help with the model giving a correct answer then I think that that context would basically be encouraging the model to hallucinate.

Modify your prompt template to add "If the context doesn't contain the answer, say 'I cannot answer this from the available documents.'" Does this help?
This somewhat helps, the model already did a good job of noting when it did not find the information in the context but the area it got stuck was on false premise questions and for these it kind of depends on how similar the question topic is to something in the context using the starter example, there were references to the starter but no mention of when it was introduced to the model T so it depends on whether the model would pick up that the fact that information about the specific model year is not there or it just sees the information about the starters and just uses that without realizing the model year being asked about never had that feature.


## 6. Query Phrasing Sensitivity

- [Query Phrasing Sensitivity Output](./outputs/e6_output.txt)

Which phrasings retrieve the best chunks?
The phrasings that recieved the best chunks were the formal, causal, and question form style questions and they mostly had scores of .56 ish where as the keyword and indirect were both much lower at .48 and .39.

Do keyword-style queries work better or worse than natural questions?
The keyword style queries work worse than natural questions as the chunks that keyword style got were lower than the natural questions and the answer that were returned were more vague and not as specific as the answers for the natural questions.

What does this tell you about potential query rewriting strategies?
What this tells me about query rewriting strategies is that it is better to make the question more specific and requesting specific information because the model gets better information and is able to create a better answer to the query.

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