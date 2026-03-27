import pytesseract
from PIL import Image


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text as a string
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found: {image_path}")

def extract_text_with_layout(image_path: str) -> str:
    """
    Extract text from an image while preserving layout information.
    Better for complex documents with columns and tables.

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text with layout preserved as a string
    """
    try:
        image = Image.open(image_path)
        # PSM 6 assumes a single uniform block of text
        # PSM 3 is fully automatic page segmentation (default)
        # PSM 1 is automatic with OSD - better for complex layouts
        custom_config = r"--psm 1"
        text = pytesseract.image_to_string(image, config=custom_config)
        return text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found: {image_path}")


def is_text_heavy(image_path: str, threshold: float = 0.3) -> bool:
    """
    Heuristic to determine if an image is text-heavy.
    Used by the agent to decide whether OCR is worth running.

    Args:
        image_path: Path to the image file
        threshold: Word density threshold above which image is considered text-heavy

    Returns:
        True if image is text-heavy, False otherwise
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    words = text.split()
    image_area = image.width * image.height
    word_density = len(words) / (image_area / 10000)
    return word_density > threshold