import os


def stitch_pages(pages: list[str]) -> str:
    """
    Combine extracted text from all pages into a single document.

    Args:
        pages: List of extracted text strings, one per page

    Returns:
        Combined text as a single string
    """
    return "\n\n".join(page for page in pages if page.strip())


def save(text: str, output_path: str) -> None:
    """
    Save the final clean text to a file.

    Args:
        text: The full extracted document text
        output_path: Path to save the output file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def default_output_path(pdf_path: str) -> str:
    """
    Generate a default output path based on the input PDF path.
    Saves the output text file in the same directory as the PDF.

    Args:
        pdf_path: Path to the input PDF

    Returns:
        Output path as a string
    """
    base = os.path.splitext(pdf_path)[0]
    return f"{base}_extracted.txt"