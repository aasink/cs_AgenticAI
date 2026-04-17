import ollama

# list of available models
MODELS = [
    "llava",
    "granite3.2-vision",
    "llama3.2-vision",
    "qwen3-vl:2b",
    "qwen3-vl:4b",
    "qwen2.5vl:7b",
    "gemma4:e2b",
    "gemma4:e4b",
    "minicpm-v:8b"
]

DEFAULT_MODEL = "gemma4:e4b"

def list_models() -> list[str]:
    """Return the list of available VLM models."""
    return MODELS

def query(image_path: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send an image and prompt to a VLM via Ollama.
 
    Args:
        image_path: Path to the image file
        prompt: The question or instruction to the model
        model: Ollama model name to use (must be pulled first)
 
    Returns:
        The model's response as a string
    """
    if model not in MODELS:             # check if model available
        raise ValueError(
            f"Model '{model}' not in available models list: {MODELS}\n"
            f"Pull it first with: ollama pull {model}"
        )
 
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path],
                }
            ],
        )
        return response["message"]["content"]
 
    except ollama.ResponseError as e:
        raise RuntimeError(
            f"Ollama error with model '{model}': {e}\n"
            f"Ensure Ollama is running and the model is pulled: ollama pull {model}"
        )