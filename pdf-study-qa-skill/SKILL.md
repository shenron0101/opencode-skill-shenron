---
name: pdf-study-qa
description: "Use when the user wants to read PDFs, analyze .pdf files, summarize PDF content, chat with a document, extract information from PDF pages, or ask questions about a PDF. Extracts text from PDF documents and answers questions based on the content."
---

# PDF Study QA

Extract text from PDF documents and answer user questions based on the extracted content. The agent reads the PDF, chunks the text for large documents, and produces grounded answers with page references.

## Step 1 — Extract text from the PDF

Use `pdfplumber` to pull text page by page. The agent should verify each page returned content and warn the user about blank or image-only pages.

```python
import pdfplumber

def extract_pdf_text(pdf_path: str) -> list[dict]:
    """Return a list of {page, text} dicts. Skips blank pages with a warning."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                print(f"Warning: page {i} returned no text (may be scanned/image-only)")
                continue
            pages.append({"page": i, "text": text})
    if not pages:
        raise RuntimeError(
            f"No extractable text found in {pdf_path}. "
            "The PDF may be scanned — consider running OCR first (e.g. ocrmypdf)."
        )
    return pages
```

### Validation checklist

- Confirm `len(pages) > 0` before proceeding.
- If zero pages have text, surface the OCR suggestion to the user and stop.
- Log total pages extracted vs. total pages in the file so the user knows if any were skipped.

## Step 2 — Chunk for large documents

When the combined text exceeds the context window, split into overlapping chunks so no answer is lost at a boundary.

```python
def chunk_pages(pages: list[dict], max_chars: int = 12000, overlap: int = 500) -> list[dict]:
    """Merge page texts into chunks that fit within max_chars, with overlap."""
    chunks = []
    current_text = ""
    current_pages = []

    for p in pages:
        if len(current_text) + len(p["text"]) > max_chars and current_text:
            chunks.append({"pages": list(current_pages), "text": current_text})
            # keep tail for overlap
            current_text = current_text[-overlap:] + "\n" + p["text"]
            current_pages = [current_pages[-1], p["page"]]
        else:
            current_text += ("\n" if current_text else "") + p["text"]
            current_pages.append(p["page"])

    if current_text:
        chunks.append({"pages": list(current_pages), "text": current_text})
    return chunks
```

## Step 3 — Answer questions with page citations

Iterate through chunks, collect relevant excerpts, and synthesize a final answer. Always cite the page number(s) where evidence was found.

```python
def answer_question(question: str, chunks: list[dict]) -> str:
    """Find relevant chunks and compose an answer with page citations."""
    relevant = []
    q_lower = question.lower()

    for chunk in chunks:
        # Simple relevance check — in production the LLM handles this
        if any(term in chunk["text"].lower() for term in q_lower.split()):
            relevant.append(chunk)

    if not relevant:
        return "No relevant content found in the document for that question."

    context_parts = []
    for r in relevant:
        page_label = ", ".join(str(p) for p in r["pages"])
        context_parts.append(f"[Pages {page_label}]\n{r['text']}")

    context = "\n---\n".join(context_parts)
    # The agent uses this context block when formulating its response
    return context
```

The agent should present the answer in natural language and append citations like *(see page 4)* or *(pages 12–14)*.

## Complete example — end-to-end pipeline

```python
import pdfplumber

pdf_path = "/path/to/document.pdf"
question = "What are the key findings in the results section?"

# 1. Extract
pages = extract_pdf_text(pdf_path)
print(f"Extracted {len(pages)} pages with text")

# 2. Chunk
chunks = chunk_pages(pages, max_chars=12000)
print(f"Split into {len(chunks)} chunks")

# 3. Retrieve context
context = answer_question(question, chunks)

# 4. The agent reads `context` and formulates a grounded answer
#    with page citations for the user.
print(context)
```

## Error handling reference

| Condition | Action |
|-----------|--------|
| File not found | Report the path back to the user and ask them to verify it |
| Zero pages extracted | Suggest OCR preprocessing (`ocrmypdf input.pdf output.pdf`) |
| Encoding errors | Try `page.extract_text()` with `pdfplumber`; fall back to `PyPDF2` if needed |
| PDF is password-protected | Inform the user; `pdfplumber.open(path, password=pw)` accepts a password argument |
| Single page exceeds chunk size | Pass it as its own chunk and warn about possible truncation |
