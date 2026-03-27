import os
import fitz  


def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200) -> list[str]:
    """
    Convert each page of a PDF into a PNG image.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save page images
        dpi: Resolution for rendering pages - higher is better quality but slower

    Returns:
        List of image paths in page order
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 is default PDF DPI
        pix = page.get_pixmap(matrix=mat)
        image_path = os.path.join(output_dir, f"page_{page_num + 1:04d}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    doc.close()
    return image_paths


def extract_embedded_text(pdf_path: str) -> list[str]:
    """
    Extract the embedded text layer from each page of a PDF.
    This is fast but may be garbled for complex layouts.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of extracted text strings, one per page
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages_text = []

    for page in doc:
        text = page.get_text()
        pages_text.append(text.strip())

    doc.close()
    return pages_text


def get_page_count(pdf_path: str) -> int:
    """
    Return the number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def cleanup_images(image_paths: list[str]) -> None:
    """
    Delete temporary page images after processing.

    Args:
        image_paths: List of image paths to delete
    """
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)