# PDF Study QA Skill

Study and ask questions about PDF documents using AI-powered analysis.

## Description

This skill enables you to upload PDF documents and ask questions about their content. It extracts text from PDFs and uses AI to provide answers based on the document's content.

## Usage

```bash
# Load the skill
/skill pdf-study-qa

# Ask questions about a PDF
/study-pdf <path-to-pdf> "What is the main topic of this document?"
```

## Features

- **Text Extraction**: Automatically extracts text from PDF files
- **Contextual Q&A**: Ask questions and get answers based on document content
- **Multi-page Support**: Handles documents of any length
- **Citation Support**: Answers include references to specific pages/sections

## Supported PDF Types

- Research papers
- Books and textbooks
- Technical documentation
- Reports and whitepapers
- Legal documents
- Any text-based PDF

## Workflow

1. **Upload**: Provide the path to your PDF file
2. **Process**: The skill extracts and indexes the text content
3. **Query**: Ask questions in natural language
4. **Answer**: Receive contextual answers with citations

## Example Queries

- "Summarize the key findings in chapter 3"
- "What are the main arguments presented?"
- "Find all mentions of 'machine learning'"
- "Compare the conclusions in sections 5 and 6"
- "Extract all tables and their data"

## Requirements

- Python 3.8+
- PyPDF2 or pdfplumber for text extraction
- OpenAI API key or compatible LLM for Q&A

## Notes

- Scanned PDFs (images) require OCR preprocessing
- Large documents may be processed in chunks
- Answers are based on extracted text, not visual layout
