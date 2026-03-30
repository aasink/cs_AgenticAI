import tempfile
import os
from src.tools import pdf, vlm
from src.agents import analyzer, executor, verifier, output


def run(pdf_path: str, output_path: str = None, model: str = vlm.DEFAULT_MODEL) -> str:
    """
    Run the full agent pipeline on a PDF.

    Args:
        pdf_path: Path to the input PDF
        output_path: Path to save the output text file, defaults to next to the PDF
        model: VLM model to use

    Returns:
        Path to the output text file
    """
    if output_path is None:
        output_path = output.default_output_path(pdf_path)

    with tempfile.TemporaryDirectory() as temp_dir:      # use a tmp dir for page images that gets cleaned up after
        print(f"Processing: {pdf_path}")
        print(f"Pages: {pdf.get_page_count(pdf_path)}")

        # split PDF into page images
        image_paths = pdf.pdf_to_images(pdf_path, temp_dir)

        pages = []
        for i, image_path in enumerate(image_paths):                        # process each page
            print(f"  Page {i + 1}/{len(image_paths)}...", end=" ")
            page_text = _process_page(image_path, model)
            pages.append(page_text)
            print("done")

        final_text = output.stitch_pages(pages)    # stitch pages together and save
        output.save(final_text, output_path)

    print(f"\nSaved to: {output_path}")
    return output_path


def _process_page(image_path: str, model: str) -> str:
    """
    Process a single page through the full agent loop:
    analyze → execute → verify → retry if needed

    Args:
        image_path: Path to the page image
        model: VLM model to use

    Returns:
        Extracted text for the page
    """
    analysis = analyzer.analyze(image_path, model=model) # analyze the page
    classification = analysis
    print(classification)

    attempts = 0
    extracted_text = None

    while verifier.should_retry(attempts):
        attempts += 1
        extracted_text = executor.execute(image_path, classification, model=model)  # execute extraction based on classification

        result = verifier.verify(image_path, extracted_text, model=model)  # verify the output

        if result["passed"]:
            break
        else:
            print(f"\n    Retry {attempts} ({result['reason']})", end=" ")

    return extracted_text