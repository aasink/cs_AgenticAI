from src.tools import vlm, ocr
from src.agents import verifier
from src.agents.analyzer import (
    SINGLE_COLUMN,
    MULTI_COLUMN,
    TABLE,
    FIGURE,
    MIXED,
)
from src.agents.prompts import (
    EXTRACT_SINGLE_COLUMN,
    EXTRACT_MULTI_COLUMN,
    EXTRACT_TABLE,
    EXTRACT_MIXED,
    EXTRACT_FIGURE,
)


def execute(image_path: str, classification: str, model: str = vlm.DEFAULT_MODEL) -> str:
    """
    Execute the appropriate extraction strategy for a page based on its classification.
 
    Args:
        image_path: Path to the page image
        classification: Layout classification from analyzer.py
        model: VLM model to use
 
    Returns:
        Extracted text as a string
    """
    if classification == SINGLE_COLUMN:
        # try OCR first, verify it, fall back to VLM if it fails
        ocr_text = ocr.extract_text(image_path)
        result = verifier.verify(image_path, ocr_text, model=model)
        if result["passed"]:
            return ocr_text
        return vlm.query(image_path, EXTRACT_SINGLE_COLUMN, model=model)
 
    elif classification == MULTI_COLUMN:
        # OCR cannot handle column reordering, go straight to VLM
        return vlm.query(image_path, EXTRACT_MULTI_COLUMN, model=model)
 
    elif classification == TABLE:
        # OCR garbles table structure, go straight to VLM
        return vlm.query(image_path, EXTRACT_TABLE, model=model)
 
    elif classification == MIXED:
        # VLM handles everything together
        return vlm.query(image_path, EXTRACT_MIXED, model=model)
 
    elif classification == FIGURE:
        # VLM generates a brief description
        return vlm.query(image_path, EXTRACT_FIGURE, model=model)
 
    else:
        # fallback
        return vlm.query(image_path, EXTRACT_SINGLE_COLUMN, model=model)