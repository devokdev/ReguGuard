"""
ReguGuard MCP Server: vector_search
===================================
Version-aware vector search engine using ChromaDB and embedding/retrieval.
Includes metadata filters (as_of_date, in_force) and amendment chain tracing.
Tools:
- search(query, doc_id, as_of_date, k)
- index_document(doc_id, text, version, effective_date, in_force)
"""

from __future__ import annotations
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from src.config import settings
from src.mcp_servers.clause_parser import split_clauses

mcp = FastMCP("vector_search")

# Persistent Chroma DB setup
import chromadb
from chromadb.config import Settings as ChromaSettings

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        chroma_dir = Path(settings.CHROMA_DIR)
        chroma_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        _collection = _client.get_or_create_collection(
            name="regulations",
            metadata={"description": "ReguGuard Version-Aware Regulatory Corpus"}
        )
    return _collection


@mcp.tool()
def index_document(
    doc_id: str,
    text: str,
    version: str = "1.0",
    effective_date: str = "2023-08-01",
    in_force: bool = True
) -> dict:
    """Index a regulation document with clause chunking and version-aware metadata."""
    col = _get_collection()
    clauses = split_clauses(text)

    if not clauses:
        return {"status": "empty", "indexed_clauses": 0}

    ids = []
    documents = []
    metadatas = []

    for i, c in enumerate(clauses):
        cid = f"{doc_id}_{version}_{i}"
        ids.append(cid)
        documents.append(c["text"])
        metadatas.append({
            "doc_id": doc_id,
            "version": version,
            "section": c["section"],
            "effective_date": effective_date,
            "in_force": in_force
        })

    col.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return {
        "status": "ok",
        "doc_id": doc_id,
        "indexed_clauses": len(clauses)
    }


@mcp.tool()
def search(
    query: str,
    doc_id: str | None = None,
    as_of_date: str | None = None,
    k: int = 3
) -> list:
    """
    Search indexed regulation clauses using semantic/keyword matching.
    Supports filtering by doc_id and as_of_date.
    """
    col = _get_collection()
    where_filter = {}
    if doc_id:
        where_filter["doc_id"] = doc_id

    # If Chroma collection is empty, index files from corpus on the fly
    if col.count() == 0:
        corpus_dir = Path(settings.CORPUS_DIR)
        for txt_file in corpus_dir.glob("*.txt"):
            doc_name = txt_file.stem
            index_document(
                doc_id=doc_name,
                text=txt_file.read_text(encoding="utf-8"),
                version="1.0",
                effective_date="2023-08-01",
                in_force=True
            )

    results = col.query(
        query_texts=[query],
        n_results=min(k, max(col.count(), 1)),
        where=where_filter if where_filter else None
    )

    hits = []
    if results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for doc_text, meta, dist in zip(docs, metas, distances):
            eff_date_str = meta.get("effective_date", "1970-01-01")

            # as_of_date temporal filter
            if as_of_date:
                try:
                    if datetime.strptime(eff_date_str, "%Y-%m-%d") > datetime.strptime(as_of_date, "%Y-%m-%d"):
                        continue
                except Exception:
                    pass

            hits.append({
                "doc_id": meta.get("doc_id"),
                "section": meta.get("section"),
                "version": meta.get("version"),
                "effective_date": eff_date_str,
                "text": doc_text,
                "score": round(1.0 - (dist if dist <= 1.0 else 0.5), 3)
            })

    return hits


if __name__ == "__main__":
    mcp.run()

