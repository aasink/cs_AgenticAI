import tempfile
import os
from src.tools import pdf, vlm
from src.agents import analyzer, executor, verifier, output

def run(pdf_path: str, output_path: str = None, model: str = vlm.DEFAULT_MODEL) -> str:
    """
    Run the full agent pipeline on a PDF or image.
    Args:
        pdf_path: Path to the input PDF or image file
        output_path: Path to save the output text file, defaults to next to the input
        model: VLM model to use
    Returns:
        Path to the output text file
    """
    if output_path is None:
        output_path = output.default_output_path(pdf_path)

    if pdf_path.lower().endswith('.pdf'):
        temp_dir = tempfile.mkdtemp()
        image_paths = pdf.pdf_to_images(pdf_path, temp_dir)
    else:
        image_paths = [pdf_path]
        temp_dir = None

    print(f"Processing: {pdf_path}")
    print(f"Pages: {len(image_paths)}")

    pages = []
    for i, image_path in enumerate(image_paths):
        print(f"  Page {i + 1}/{len(image_paths)}...", end=" ")
        page_text = process_page(image_path, model)
        pages.append(page_text)
        print("done")

    if temp_dir:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    final_text = output.stitch_pages(pages)
    output.save(final_text, output_path)
    # print(f"\nSaved to: {output_path}")
    return output_path


def process_page(image_path: str, model: str) -> str:
    """
    Process a single page through the full agent loop:
    analyze → execute → verify → retry if needed
    Args:
        image_path: Path to the page image
        model: VLM model to use
    Returns:
        Extracted text for the page
    """
    analysis = analyzer.analyze(image_path, model=model)
    classification = analysis

    attempts = 0
    extracted_text = None

    while verifier.should_retry(attempts):
        attempts += 1
        extracted_text = executor.execute(image_path, classification, model=model)
        result = verifier.verify(image_path, extracted_text, model=model)
        if result["passed"]:
            break
        else:
            print(f"\n    Retry {attempts} ({result['reason']})", end=" ")

    if extracted_text is None:
        return ""
    return extracted_text