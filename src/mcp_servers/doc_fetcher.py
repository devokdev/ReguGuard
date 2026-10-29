"""
ReguGuard MCP Server: doc_fetcher
=================================
Reads curated regulatory corpus from data/corpus/ and MANIFEST.csv.
Tools:
- fetch_regulation(doc_id)
- list_new_documents(since)
"""

from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from src.config import settings

mcp = FastMCP("doc_fetcher")


def _get_manifest() -> Dict[str, Dict[str, str]]:
    manifest_path = Path(settings.CORPUS_DIR) / "MANIFEST.csv"
    if not manifest_path.exists():
        return {}
    docs = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            docs[row["doc_id"]] = row
    return docs


@mcp.tool()
def fetch_regulation(doc_id: str) -> dict:
    """Fetch regulation text and metadata by document ID from data/corpus/."""
    manifest = _get_manifest()
    meta = manifest.get(doc_id, {})

    # Try .txt or .pdf
    doc_path_txt = Path(settings.CORPUS_DIR) / f"{doc_id}.txt"
    doc_path_pdf = Path(settings.CORPUS_DIR) / f"{doc_id}.pdf"

    content = ""
    if doc_path_txt.exists():
        content = doc_path_txt.read_text(encoding="utf-8")
    elif doc_path_pdf.exists():
        import fitz
        doc = fitz.open(str(doc_path_pdf))
        content = "\n".join(page.get_text() for page in doc)
    else:
        return {"status": "error", "message": f"Document {doc_id} not found in corpus"}

    return {
        "status": "ok",
        "doc_id": doc_id,
        "content": content,
        "metadata": meta
    }


@mcp.tool()
def list_new_documents(since: str = "2020-01-01") -> list:
    """List documents in corpus published on or after the 'since' date (YYYY-MM-DD)."""
    manifest = _get_manifest()
    results = []
    try:
        since_dt = datetime.strptime(since, "%Y-%m-%d").date()
    except Exception:
        since_dt = datetime(2020, 1, 1).date()

    for doc_id, info in manifest.items():
        doc_date_str = info.get("doc_date", "1970-01-01")
        try:
            doc_dt = datetime.strptime(doc_date_str, "%Y-%m-%d").date()
        except Exception:
            doc_dt = datetime(1970, 1, 1).date()

        if doc_dt >= since_dt:
            results.append({
                "doc_id": doc_id,
                "title": info.get("title", ""),
                "doc_date": doc_date_str,
                "effective_date": info.get("effective_date", ""),
                "synthetic": info.get("synthetic", "false").lower() == "true",
                "description": info.get("description", "")
            })

    return results


if __name__ == "__main__":
    mcp.run()

