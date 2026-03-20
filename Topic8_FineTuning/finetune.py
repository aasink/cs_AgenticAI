import json, random
import tinker
from tinker import types
import numpy as np
import sqlite3
from dotenv import load_dotenv
import os

from sql_matches import *


#================================ Evaluation Functions ================================#

def sample_from_model(sampling_client, tokenizer, context: str, question: str) -> str:
    """Generate SQL from the model given schema and question."""
    prompt = f"""Table schema:
    {context}
    Question: {question}
    SQL: """
    prompt_tokens = tokenizer.encode(prompt, add_special_tokens=True)
    model_input = types.ModelInput.from_ints(tokens=prompt_tokens)
    params = types.SamplingParams(max_tokens=150, temperature=0.0, stop=["\n\n", "Question:"])
    result = sampling_client.sample(prompt=model_input, sampling_params=params, num_samples=1).result()
    if result.sequences:
        return tokenizer.decode(result.sequences[0].tokens).strip()
    return ""

def eval_one(sampling_client, tokenizer, ex: dict) -> bool:
    """Evaluate one example: generate SQL, then check if it matches expected."""
    sql = sample_from_model(sampling_client, tokenizer, ex["context"], ex["question"])
    return sql_matches(sql, ex["answer"], schema=ex["context"])

def evaluate_test_set(sampling_client, tokenizer, test_data: list) -> float:
    """Compute accuracy = fraction of test examples where generated SQL matches expected."""
    correct = sum(1 for ex in test_data if eval_one(sampling_client, tokenizer, ex))
    return correct / len(test_data)



#================================ Prepare Training Data Functions ================================#


def format_prompt(example: dict) -> tuple[str, str]:
    """Format example as prompt and completion for text-to-SQL."""
    prompt = f"""Table schema:
{example['context']}
Question: {example['question']}
SQL: """
    completion = example["answer"]
    return prompt, completion

def process_example(example: dict, tokenizer) -> types.Datum:
    """Convert a (question, context, answer) example into a Tinker Datum."""
    prompt, completion = format_prompt(example)

    prompt_tokens = tokenizer.encode(prompt, add_special_tokens=True)
    prompt_weights = [0.0] * len(prompt_tokens)

    # Add space before completion, end with \n\n so the model learns to stop
    completion_str = f" {completion}\n\n"
    completion_tokens = tokenizer.encode(completion_str, add_special_tokens=False)
    completion_weights = [1.0] * len(completion_tokens)

    tokens = prompt_tokens + completion_tokens
    weights = prompt_weights + completion_weights

    # Next-token prediction: input is tokens[:-1], target is tokens[1:]
    input_tokens = tokens[:-1]
    target_tokens = tokens[1:]
    weights = weights[1:]

    return types.Datum(
        model_input=types.ModelInput.from_ints(tokens=input_tokens),
        loss_fn_inputs={
            "target_tokens": np.array(target_tokens, dtype=np.int64),
            "weights": np.array(weights, dtype=np.float32),
        },
    )


#================================ Print Sample Examples ================================#

with open("sql_create_context_v4.json") as f:
    data = json.load(f)

print(f"Total examples: {len(data)}")
print(f"\nSample example:")
ex = data[0]
print(f"  Question: {ex['question']}")
print(f"  Context:  {ex['context'][:120]}...")
print(f"  Answer:   {ex['answer']}")
print("\n\n")


#================================ Load and Explore Data ================================#

NUM_TEST_EXAMPLES = 200  # Held-out for evaluation; all remaining data used for training
random.shuffle(data)
test_data = data[:NUM_TEST_EXAMPLES]
train_data = data[NUM_TEST_EXAMPLES:]
print(f"Training examples: {len(train_data)} (all except evaluation)")
print(f"Test examples: {len(test_data)}")
print("\n")


#================================ Load API Key ================================#

load_dotenv()
tinker.api_key = os.getenv("TINKER_API_KEY")


#================================ Evaluate Base Model ================================#

service_client = tinker.ServiceClient()
base_model = "meta-llama/Llama-3.2-1B"
training_client = service_client.create_lora_training_client(base_model=base_model)
tokenizer = training_client.get_tokenizer()

print("\n--- Evaluating Base Model on 200 Test Questions ---")
base_sampling_client = training_client.save_weights_and_get_sampling_client(
    name="base-model"
)
base_accuracy = evaluate_test_set(
    base_sampling_client, tokenizer, test_data#, "base"
)
print(f"Base model accuracy: {base_accuracy:.2%} ({int(base_accuracy * 200)}/200)")

print("\n\n")



#================================ Prepare Training Data ================================#

processed_train = [
    process_example(ex, tokenizer) for ex in train_data
]
random.shuffle(processed_train)




#================================ Training ================================#

NUM_EPOCHS = 1
BATCH_SIZE = 256
LEARNING_RATE = 5e-4  # Tinker-recommended for Llama-3.2-1B with LoRA

step = 0
for epoch in range(NUM_EPOCHS):
    random.shuffle(processed_train)
    for batch_idx in range(0, len(processed_train), BATCH_SIZE):
        batch = processed_train[batch_idx : batch_idx + BATCH_SIZE]
        if len(batch) == 0:
            break

        fwdbwd_future = training_client.forward_backward(batch, "cross_entropy")
        optim_future = training_client.optim_step(
            types.AdamParams(learning_rate=LEARNING_RATE)
        )

        fwdbwd_result = fwdbwd_future.result()
        optim_result = optim_future.result()

        # Compute loss (weighted cross-entropy over completion tokens only)
        to_arr = lambda x: x.to_numpy() if hasattr(x, "to_numpy") else np.array(x.tolist())
        logprobs = np.concatenate([to_arr(o["logprobs"]) for o in fwdbwd_result.loss_fn_outputs])
        weights = np.concatenate([to_arr(d.loss_fn_inputs["weights"]) for d in batch])
        loss = float(-np.dot(logprobs, weights) / (weights.sum() + 1e-8))

        step += 1
        if step % 100 == 0 or batch_idx + BATCH_SIZE >= len(processed_train):
            print(f"Epoch {epoch + 1}/{NUM_EPOCHS}, update {step}, loss: {loss:.4f}")




#================================ Evaluate Fine Tuned Model ================================#

print("\n--- Evaluating Fine-Tuned Model on 200 Test Questions ---")
finetuned_sampling_client = training_client.save_weights_and_get_sampling_client(
    name="finetuned-model"
)
finetuned_accuracy = evaluate_test_set(
    finetuned_sampling_client, tokenizer, test_data
)
print(f"Fine-tuned model accuracy: {finetuned_accuracy:.2%} ({int(finetuned_accuracy * 200)}/200)")

print("\n--- Comparison ---")
print(f"Base model accuracy:       {base_accuracy:.2%} ({int(base_accuracy * 200)}/200)")
print(f"Fine-tuned model accuracy: {finetuned_accuracy:.2%} ({int(finetuned_accuracy * 200)}/200)")
print(f"Improvement:               {(finetuned_accuracy - base_accuracy):.2%}")


#================================ Novel Schema Questions ================================#

novel_questions = [
    {
        "difficulty": "Easy",
        "context": "CREATE TABLE employees (id INTEGER, name VARCHAR, salary REAL, department VARCHAR)",
        "question": "What are the names of employees in the engineering department?",
        "answer": "SELECT name FROM employees WHERE department = 'engineering'"
    },
    {
        "difficulty": "Easy",
        "context": "CREATE TABLE products (id INTEGER, name VARCHAR, price REAL, category VARCHAR)",
        "question": "How many products cost more than 50 dollars?",
        "answer": "SELECT COUNT(*) FROM products WHERE price > 50"
    },
    {
        "difficulty": "Medium",
        "context": "CREATE TABLE students (id INTEGER, name VARCHAR, score INTEGER, class VARCHAR)",
        "question": "What is the highest score in the science class?",
        "answer": "SELECT MAX(score) FROM students WHERE class = 'science'"
    },
    {
        "difficulty": "Medium",
        "context": "CREATE TABLE orders (id INTEGER, customer VARCHAR, amount REAL, date VARCHAR)",
        "question": "List the top 3 customers by total order amount.",
        "answer": "SELECT customer FROM orders GROUP BY customer ORDER BY SUM(amount) DESC LIMIT 3"
    },
    {
        "difficulty": "Hard",
        "context": "CREATE TABLE courses (id INTEGER, name VARCHAR, department VARCHAR); CREATE TABLE enrollments (student_id INTEGER, course_id INTEGER, grade VARCHAR)",
        "question": "How many students are enrolled in each department?",
        "answer": "SELECT c.department, COUNT(e.student_id) FROM courses c JOIN enrollments e ON c.id = e.course_id GROUP BY c.department"
    },
]

print("\n--- Novel Schema Questions (Out-of-Distribution) ---\n")
for i, ex in enumerate(novel_questions):
    generated_sql = sample_from_model(finetuned_sampling_client, tokenizer, ex["context"], ex["question"])
    match = sql_matches(generated_sql, ex["answer"], schema=ex["context"])
    
    print(f"[{ex['difficulty']}] Q{i+1}: {ex['question']}")
    print(f"  Expected:  {ex['answer']}")
    print(f"  Generated: {generated_sql}")
    print(f"  Match:     {'✓' if match else '✗'}")
    print()