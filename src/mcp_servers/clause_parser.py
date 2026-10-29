"""
ReguGuard MCP Server: clause_parser
===================================
Splits regulation text into clauses/sections and extracts monetary thresholds & dates.
Tools:
- parse_pdf(path)
- split_clauses(text)
- extract_thresholds(text)
"""

from __future__ import annotations
import re
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clause_parser")


@mcp.tool()
def split_clauses(text: str) -> list:
    """Split legal text into paragraphs or clause chunks."""
    # Split on Para, Section, G.S.R., or double newlines
    raw_paragraphs = re.split(r'\n\s*\n', text)
    clauses = []
    idx = 1
    for p in raw_paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue

        # Look for explicit clause label
        label_match = re.search(r'^(Para\s*\d+|Section\s*\d+(\([0-9a-zA-Z]+\))*|G\.S\.R\.[^\n]+)', p_clean, re.IGNORECASE)
        section_label = label_match.group(1) if label_match else f"para {idx}"

        clauses.append({
            "section": section_label,
            "text": p_clean
        })
        idx += 1

    return clauses


@mcp.tool()
def extract_thresholds(text: str) -> dict:
    """Extract rupee monetary turnover thresholds and dates using regex."""
    # Pattern e.g. "five hundred crore rupees", "10 crore rupees", "5 crore rupees"
    word_to_num = {
        "one": 1, "two": 2, "five": 5, "ten": 10, "twenty": 20, "fifty": 50,
        "hundred": 100, "five hundred": 500
    }

    threshold_rupees = None
    threshold_match = re.search(r'(\d+|five hundred|one|two|five|ten|twenty|fifty)\s*(crore|lakh)?\s*rupees', text, re.IGNORECASE)

    if threshold_match:
        val_str = threshold_match.group(1).lower()
        unit = (threshold_match.group(2) or "").lower()

        base_val = word_to_num.get(val_str, None)
        if base_val is None:
            try:
                base_val = float(val_str)
            except ValueError:
                base_val = 0.0

        if unit == "crore" or "crore" in threshold_match.group(0).lower():
            threshold_rupees = base_val * 10_000_000.0
        elif unit == "lakh":
            threshold_rupees = base_val * 100_000.0
        else:
            threshold_rupees = base_val

    # Dates e.g., 1st day of August, 2023 or 2023-08-01
    date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})', text, re.IGNORECASE)
    extracted_date = date_match.group(1) if date_match else None

    return {
        "raw_text_snippet": text[:150],
        "threshold_rupees": threshold_rupees,
        "threshold_crore": (threshold_rupees / 10_000_000.0) if threshold_rupees else None,
        "extracted_date": extracted_date
    }


@mcp.tool()
def parse_pdf(path: str) -> dict:
    """Parse text from a PDF file using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(path)
        pages = [page.get_text() for page in doc]
        return {
            "status": "ok",
            "page_count": len(pages),
            "full_text": "\n".join(pages)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    mcp.run()

