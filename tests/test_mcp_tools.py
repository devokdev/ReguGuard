"""
Unit & Acceptance Tests for PRD §14 Step 3: MCP Tool Servers
=============================================================
Acceptance criteria:
- Each tool is callable via MCP or direct functions.
- Diff of the sample pair (notif_13_2020 vs notif_10_2023) returns the expected
  threshold change (500 crore/10 crore -> 5 crore).
- SME DB retrieves profiles and writes memory.
- Deadline calculator correctly computes dates and countdowns.
"""

import pytest
from src.mcp_servers.doc_fetcher import fetch_regulation, list_new_documents
from src.mcp_servers.clause_parser import split_clauses, extract_thresholds
from src.mcp_servers.diff_tool import diff_versions
from src.mcp_servers.sme_db import get_profile, list_smes, update_memory
from src.mcp_servers.deadline_calc import compute_deadline, days_remaining
from src.mcp_servers.vector_search import index_document, search


def test_doc_fetcher():
    # CONCEPT: doc_fetcher tool
    doc = fetch_regulation("notif_10_2023")
    assert doc["status"] == "ok"
    assert "five crore rupees" in doc["content"]

    new_docs = list_new_documents(since="2022-01-01")
    assert len(new_docs) >= 2


def test_clause_parser():
    # CONCEPT: clause_parser tool
    sample_text = (
        "Para 1: In exercise of powers conferred...\n\n"
        "Para 2: Turnover exceeds five crore rupees with effect from 1st day of August, 2023."
    )
    clauses = split_clauses(sample_text)
    assert len(clauses) == 2
    assert "Para 2" in clauses[1]["section"]

    thresh = extract_thresholds(clauses[1]["text"])
    assert thresh["threshold_crore"] == 5.0
    assert "August" in thresh["extracted_date"]


def test_diff_tool_acceptance():
    # CONCEPT: Step 3 Acceptance Test - Diff of sample pair returns expected threshold change
    doc_old = fetch_regulation("notif_13_2020")["content"]
    doc_new = fetch_regulation("notif_10_2023")["content"]

    changes = diff_versions(doc_old, doc_new)
    assert len(changes) >= 1

    # Check that threshold modification is accurately extracted
    found_threshold_change = any(
        c.get("threshold_new") == 50000000.0 or "five crore" in str(c.get("new_text"))
        for c in changes
    )
    assert found_threshold_change, "Expected 5 crore threshold change not detected in diff!"


def test_sme_db():
    # CONCEPT: sme_db tool
    smes = list_smes()
    assert len(smes) >= 4  # Expanded to 12 synthetic SMEs in Step 10
    assert any(s["sme_id"] == "SME-01" for s in smes)

    p = get_profile("SME-01")
    assert p["status"] == "ok"
    assert p["name"] == "Bharat Agro Implements Pvt Ltd"

    # Test memory update
    up = update_memory("SME-01", "Installed ERP v2.4 in Q2")
    assert up["status"] == "ok"


def test_deadline_calc():
    # CONCEPT: deadline_calc tool
    res = compute_deadline("2023-08-01", "einvoice_setup")
    assert res["status"] == "ok"
    assert res["deadline"] == "2023-08-01"

    calc = days_remaining("2030-01-01")
    assert calc["status"] == "ok"
    assert calc["days_remaining"] > 0
    assert calc["is_past"] is False


def test_vector_search():
    # CONCEPT: vector_search tool
    res_idx = index_document(
        doc_id="test_doc",
        text="All registered persons with aggregate turnover exceeding five crore rupees shall issue e-invoices.",
        version="v1",
        effective_date="2023-08-01"
    )
    assert res_idx["status"] == "ok"

    hits = search(query="turnover exceeding five crore", doc_id="test_doc", k=2)
    assert len(hits) >= 1
    assert "five crore" in hits[0]["text"]

