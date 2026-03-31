from src.tools import vlm
from src.agents.prompts import ANALYZE_PAGE

# Page layout classifications
SINGLE_COLUMN = "single_column"
MULTI_COLUMN = "multi_column"
TABLE = "table"
FIGURE = "figure"
MIXED = "mixed"
EMPTY = "empty"

ALL_CLASSIFICATIONS = [SINGLE_COLUMN, MULTI_COLUMN, TABLE, FIGURE, MIXED, EMPTY]


def analyze(image_path: str, model: str = vlm.DEFAULT_MODEL) -> dict:
    """
    Analyze a page image and classify its layout.

    Args:
        image_path: Path to the page image
        model: VLM model to use

    Returns:
        Dictionary with:
            - classification: one of the layout types above
            - description: the raw VLM description of the page
    """
    vlm_output = vlm.query(image_path, ANALYZE_PAGE, model=model)

    label = vlm_output.strip().lower()

    if label in ALL_CLASSIFICATIONS:  # If the model returns a valid label, use it
        return label

    return SINGLE_COLUMN       