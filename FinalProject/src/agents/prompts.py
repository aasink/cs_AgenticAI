# Used by analyzer.py to classify what is on a page
ANALYZE_PAGE = """You are a page layout classifier.
Given an image of a document page, choose exactly ONE of the following labels:
- single_column
- multi_column
- table
- figure
- mixed
- empty

Definitions:
- single_column: the page is primarily text in one main column. Small images or icons do NOT change this.
- multi_column: text is arranged in two or more vertical columns.
- table: the page contains a structured grid of rows and columns.
- figure: the page is dominated by an image, diagram, chart, or illustration.
- mixed: the page contains two or more major content types (text, figure, table), OR any figure/table occupies roughly half or more of the page.
- empty: blank or nearly blank page.

Rules:
- Respond with ONLY the label.
- Do not describe the page.
- Do not output anything else.
"""

# Used by executor.py based on what the analyzer found
EXTRACT_SINGLE_COLUMN = """Extract all text from this image exactly as it appears.
Do not summarize, paraphrase, describe, or interpret the content in any way.
Preserve the original wording, punctuation, and reading order.
Output only the raw extracted text, nothing else."""

EXTRACT_MULTI_COLUMN = """Extract all text from this image exactly as it appears.
The page has multiple columns. Read them in the correct order, left to right, and combine into a single column of text.
Do not summarize, paraphrase, describe, or interpret the content in any way.
Preserve the original wording and punctuation.
Output only the raw extracted text, nothing else."""

EXTRACT_TABLE = """Extract all text from this image exactly as it appears.
The page contains one or more tables. For each table:
- Output one row per line
- Separate columns with a pipe character |
- Preserve all column headers exactly as written
- Do not break rows across lines
Do not summarize, paraphrase, describe, or interpret the content in any way.
Output only the raw extracted text and tables, nothing else."""

EXTRACT_MIXED = """Extract all text from this image exactly as it appears.
The page has a mix of text and tables.
- Read columns in the correct order, left to right, combining them into a single column
- For tables, output one row per line with columns separated by a pipe character |
- Preserve the overall reading order of the page
Do not summarize, paraphrase, describe, or interpret the content in any way.
Preserve the original wording and punctuation throughout.
Output only the raw extracted text and tables, nothing else."""

EXTRACT_FIGURE = """This page contains a figure or image.
Provide a brief one sentence description of what the figure shows.
Format it as: [FIGURE: <description>]
Output only the figure description, nothing else."""

# Used by verifier.py to check the output of the executor
VERIFY_OUTPUT = """You are checking the quality of text extracted from a document page image.
Here is the extracted text:
{extracted_text}

Check for the following issues:
- Is the reading order correct?
- Are any words or sentences cut off or missing?
- Are tables properly formatted with one row per line?
- Is there any garbled, nonsensical, or summarized text instead of direct extraction?

Reply with either:
PASS - if the output looks correct
FAIL: <brief reason (1-2 sentences max)> - if there is a problem

Do not rewrite the text, just evaluate it."""