# PlainText
### An Agentic Pipeline for Local Document Text Extraction
*CS6501 Workshop on Building AI Agents — Final Project*

---

## Presentation
▶️ [Watch the presentation](./presentation.mp4)

---

PlainText is a fully local, open-source pipeline for extracting clean text from complex documents. It uses multimodal vision-language models running via Ollama to handle layouts that traditional OCR and copy-paste can't — multi-column papers, tables, forms, figures, and mixed content — with no API keys and no data leaving your machine.

---

## Table of Contents
- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)

---

## The Problem

Documents come in all shapes — scanned pages, multi-column layouts, tables, forms, and handwriting. The variety of layouts makes accurate text extraction genuinely difficult.

**Traditional OCR** has no understanding of layout. Copy-paste a two-column paper and you get scrambled, unusable output.

**ChatGPT** limits free tier users to ~4 file uploads, requires a paid subscription beyond that, and sends your documents to OpenAI's servers.

**Cloud OCR APIs** (AWS Textract, Google Document AI) have a limited free tier that expires after 3 months, costs that scale quickly with volume and complexity, and the same privacy problem — your data leaves your machine.

PlainText solves all three: it runs entirely locally, handles complex layouts, and is completely free.

---

## How It Works

PlainText runs an agentic loop over each page of a document:

1. **Document Parser** — splits the document into individual page images
2. **Analyzer** — classifies the page layout type
3. **Executor** — applies the right extraction strategy based on the classification
4. **Verifier** — checks the output for completeness and hallucinations, retries if needed
5. **Output** — assembles all pages into a clean plain text file

Layout types handled:

| Layout | Strategy |
|--------|----------|
| Single column | Direct extraction |
| Multi-column | Reorders columns into single column |
| Table | Reconstructs rows, one per line, pipe-separated |
| Figure | Generates a brief description |
| Mixed | Handles columns and tables together |
| Empty | Skipped |

---

## Setup

### Prerequisites
- Install [Ollama](https://ollama.com)

Pull a vision-language model:
```bash
ollama pull gemma4           # Recommended — best quality
ollama pull llama3.2-vision
ollama pull qwen2.5vl:7b
ollama pull granite3.2-vision
ollama pull moondream
```

To use a model not listed above, add its name to `MODELS` in [src/tools/vlm.py](./src/tools/vlm.py).

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage

Make sure Ollama is running first — either via the desktop app or:
```bash
ollama serve
```

### GUI
```bash
python app.py
```
Select a document (PDF or image), choose an output path and model, and click Run. The progress bar tracks each page. When complete, click **Open Extracted Text File** to view the result.

### Command Line
```bash
python app-cli.py path/to/document.pdf
```

With options:
```bash
# custom output path
python app-cli.py document.pdf --output clean.txt

# different model
python app-cli.py document.pdf --model gemma4
```

Supported input formats: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp`, `.webp`

---

## Project Structure
```
PlainText/
│
├── app.py                      # Desktop GUI
├── app-cli.py                  # CLI entry point
├── requirements.txt
├── README.md
├── presentation.mp4
│
├── src/
│   ├── agents/
│   │   ├── agent.py            # Orchestrates the full pipeline
│   │   ├── analyzer.py         # Classifies each page layout
│   │   ├── executor.py         # Applies extraction strategy
│   │   ├── verifier.py         # Checks output, triggers retry if needed
│   │   ├── prompts.py          # Prompts for each pipeline stage
│   │   └── output.py           # Stitches pages and saves final text
│   │
│   └── tools/
│       ├── vlm.py              # Ollama model calls
│       └── pdf.py              # PDF splitting and page rendering
│
└── test/                       # Sample documents for testing
```

---

## Notes
- Ollama must be running before launching PlainText. Start it with `ollama serve` or via the Ollama desktop app.
- Larger models produce better results but are slower. `gemma4` is recommended for the best quality/speed balance on Apple Silicon.
- For best results on low quality scans, consider pre-processing images to boost contrast before running.