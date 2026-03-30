from src.tools import vlm
from src.agents.prompts import VERIFY_OUTPUT

MAX_RETRIES = 3


def verify(image_path: str, extracted_text: str, model: str = vlm.DEFAULT_MODEL) -> dict:
    """
    Verify the quality of extracted text against the original page image.

    Args:
        image_path: Path to the original page image
        extracted_text: Text extracted by the executor
        model: VLM model to use

    Returns:
        Dictionary with:
            - passed: True if output looks correct, False otherwise
            - reason: Reason for failure if passed is False
    """
    prompt = VERIFY_OUTPUT.format(extracted_text=extracted_text)
    response = vlm.query(image_path, prompt, model=model)

    if response.strip().upper().startswith("PASS"):
        return {"passed": True, "reason": None}
    else:
        reason = response.strip().removeprefix("FAIL:").strip()
        return {"passed": False, "reason": reason}


def should_retry(attempts: int) -> bool:
    """
    Determine whether to retry based on number of attempts so far.

    Args:
        attempts: Number of extraction attempts made so far

    Returns:
        True if should retry, False if max retries reached
    """
    return attempts < MAX_RETRIES