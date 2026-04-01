# Final Project: Agentic PDF Extraction Pipeline
---
 
An agentic, open-source alternative to ChatGPT Vision for processing complex PDF documents. Uses a local vision-language model and OCR to convert PDFs with multi-column layouts and tables into clean, single-column plain text — no API keys, no data leaving your machine.
 
---
 
## Table of Contents
 
- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Benchmarking](#benchmarking)
- [Roadmap](#roadmap)
 
---
 
## The Problem
 
PDFs with complex layouts — multiple columns, embedded tables — get garbled when you extract text normally. ChatGPT Vision handles these perfectly, but you can't call it via API. Merlin replicates that capability using entirely open-source, locally running tools.
 
This makes Merlin particularly useful as a preprocessing step for RAG pipelines, where garbled table extraction breaks question answering over document contents.
 
---
 
## How It Works
 
Merlin runs an agent loop over each page of a PDF:
 
1. **Analyze** — the agent looks at the page visually and classifies its layout
2. **Execute** — based on the classification, the agent picks the right extraction strategy
3. **Verify** — the agent checks its own output and retries if something looks wrong
 
Layout types handled:
 
| Layout | Strategy |
|--------|----------|
| Single column text | OCR, fall back to VLM if OCR fails verification |
| Multi-column text | VLM reorders columns into single column |
| Tables | VLM reconstructs rows, one per line |
| Mixed | VLM handles columns and tables together |
| Figures | VLM generates a brief description |
 
---

## Setup
 
### Prerequisites
 
- Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Install Ollama: https://ollama.com
 
Then pull the desired vision model:
```bash
ollama pull [MODEL]
ollama pull qwen3-vl:2b         # (Recommended)
ollama pull qwen3-vl:4b
ollama pull qwen3-vl:8b
ollama pull llava
ollama pull granite3.2-vision
ollama pull llama3.2-vision
```

If running a model not listed above, add model designator to MODELS in [src/tools/vlm.py](./src/tools/vlm.py)
 
### Install Python Dependencies
 
```bash
pip install -r requirements.txt
```

---
 
## Usage
 
### GUI
 
```bash
python app.py
```
 
Upload a PDF, choose an output path and model, and click Run. Progress is shown page by page in the log.
 
### Command Line
 
```bash
python app-cli.py path/to/document.pdf
```
 
With options:
```bash
# custom output path
python app-cli.py document.pdf --output clean.txt path/to/document.pdf
 
# different model
python app-cli.py document.pdf --model qwen3-vl:2b path/to/document.pdf
```
 
---
 
## Project Structure
 
```
project/
│
├── app.py                      # Tkinter GUI
├── app-cli.py                 # CLI entry point
├── requirements.txt
├── README.md
│
├── src/
│   ├── agent/
│   │   ├── agent.py            # orchestrates the full agent loop
│   │   ├── analyzer.py         # classifies each page layout
│   │   ├── executor.py         # carries out the agent's plan using tools
│   │   ├── verifier.py         # checks output, triggers retry if needed
│   │   ├── prompts.py          # prompts that guide the agent
│   │   └── output.py           # stitches pages and saves final text
│   │
│   └── tools/
│       ├── vlm.py              # Ollama VLM calls
│       ├── ocr.py              # Tesseract OCR
│       └── pdf.py              # PDF splitting, embedded text extraction
│
├── test/                       # sample PDFs for testing
│   ├──
│   ├──
│   ├──
│   └── 
│
└── benchmark/
    ├── benchmark.py            # runs pipeline on test docs, scores results
    └── results/                # saved benchmark outputs
```
 
---
 
## Benchmarking
 
Run the benchmark suite to compare output quality against GPT-5 Vision:
 
```bash
python benchmark/benchmark.py
```
 
Results are saved to `benchmark/results/`.
 
---