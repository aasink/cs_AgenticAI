import argparse
from src.agents.agent import run
from src.tools.vlm import DEFAULT_MODEL, MODELS
import  time


def main():
    parser = argparse.ArgumentParser(
        description="Convert a complex PDF into clean plain text using an open-source vision-language model."
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file"
    )

    parser.add_argument(
        "--output",
        help="Path to save the output text file (default: next to the input PDF)",
        default=None
    )

    parser.add_argument(
        "--model",
        help=f"VLM model to use (default: {DEFAULT_MODEL}). Available: {', '.join(MODELS)}",
        default=DEFAULT_MODEL,
        choices=MODELS
    )

    args = parser.parse_args()

    start =  time.time()
    output_path = run(
        pdf_path=args.pdf_path,
        output_path=args.output,
        model=args.model
    )
    end = time.time()

    print(f"Done. Output saved to: {output_path}")

    elapsed = end-start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    milliseconds = int((elapsed - int(elapsed)) * 1000)

    print(f"Extraction time: {minutes}m {seconds}s {milliseconds}ms")



if __name__ == "__main__":
    main()