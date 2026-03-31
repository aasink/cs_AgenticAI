# Final Project Table of Contents

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
