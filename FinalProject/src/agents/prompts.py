
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
- mixed: the page contains both significant text and a significant figure or table.
- empty: blank or nearly blank page.

Rules:
- Respond with ONLY the label.
- Do not describe the page.
- Do not output anything else..
"""


# Used by executor.py based on what the analyzer found
EXTRACT_SINGLE_COLUMN = """Convert this page to plain text.
Use the embedded text if it looks clean and accurate.
Output only the extracted text, nothing else."""

EXTRACT_MULTI_COLUMN = """Convert this page to plain text.
The page has multiple columns. Read them in the correct order, left to right, and combine them into a single column of text.
Do not maintain the column structure.
Output only the extracted text, nothing else."""

EXTRACT_TABLE = """Convert this page to plain text.
The page contains one or more tables. For each table:
- output one row per line
- separate columns with a pipe character |
- preserve all column headers
- do not break rows across lines
Output only the extracted text and tables, nothing else."""

EXTRACT_MIXED = """Convert this page to plain text.
The page has a mix of columns and tables. 
- Read columns in the correct order, left to right, combining them into a single column
- For tables, output one row per line with columns separated by a pipe character |
- Preserve the overall reading order of the page
Output only the extracted text and tables, nothing else."""

EXTRACT_FIGURE = """This page contains a figure or image.
Provide a brief one sentence description of what the figure shows.
Format it as: [FIGURE: <description>]
Output only the figure description, nothing else."""


# Used by verifier.py to check the output of the executor
VERIFY_OUTPUT = """You are checking the quality of text extracted from a PDF page.
Here is the original page image and the extracted text:

{extracted_text}

Check for the following issues:
- Is the reading order correct?
- Are any words or sentences cut off or missing?
- Are tables properly formatted with one row per line?
- Is there any garbled or nonsensical text?

Reply with either:
PASS - if the output looks correct
FAIL: <brief reason> - if there is a problem

Do not rewrite the text, just evaluate it."""