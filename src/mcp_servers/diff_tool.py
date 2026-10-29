"""
ReguGuard MCP Server: diff_tool
===============================
Performs clause-level diff between prior and current regulation versions.
Returns structured additions, removals, and modifications with threshold changes.
Tools:
- diff_versions(old_text, new_text)
"""

from __future__ import annotations
import difflib
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP
from src.mcp_servers.clause_parser import split_clauses, extract_thresholds

mcp = FastMCP("diff_tool")


@mcp.tool()
def diff_versions(old_text: str, new_text: str) -> list:
    """
    Diff two regulation versions clause-by-clause.
    Identifies additions, modifications, and numeric threshold changes.
    """
    old_clauses = split_clauses(old_text)
    new_clauses = split_clauses(new_text)

    changes = []

    # Map by section or position
    old_dict = {c["section"]: c["text"] for c in old_clauses}
    new_dict = {c["section"]: c["text"] for c in new_clauses}

    # Detect modifications & additions
    for sec, n_text in new_dict.items():
        if sec in old_dict:
            o_text = old_dict[sec]
            if o_text.strip() != n_text.strip():
                # Clause was modified
                o_thresh = extract_thresholds(o_text)
                n_thresh = extract_thresholds(n_text)

                changes.append({
                    "change_type": "modified",
                    "section": sec,
                    "old_text": o_text,
                    "new_text": n_text,
                    "threshold_old": o_thresh.get("threshold_rupees"),
                    "threshold_new": n_thresh.get("threshold_rupees"),
                    "effective_date": n_thresh.get("extracted_date")
                })
        else:
            # Clause was added
            n_thresh = extract_thresholds(n_text)
            changes.append({
                "change_type": "added",
                "section": sec,
                "old_text": None,
                "new_text": n_text,
                "threshold_old": None,
                "threshold_new": n_thresh.get("threshold_rupees"),
                "effective_date": n_thresh.get("extracted_date")
            })

    # Detect removals
    for sec, o_text in old_dict.items():
        if sec not in new_dict:
            o_thresh = extract_thresholds(o_text)
            changes.append({
                "change_type": "removed",
                "section": sec,
                "old_text": o_text,
                "new_text": None,
                "threshold_old": o_thresh.get("threshold_rupees"),
                "threshold_new": None,
                "effective_date": None
            })

    # If section-based alignment yielded nothing but texts differ, use difflib unified comparison
    if not changes and old_text.strip() != new_text.strip():
        o_thresh = extract_thresholds(old_text)
        n_thresh = extract_thresholds(new_text)
        changes.append({
            "change_type": "modified",
            "section": "General / All Sections",
            "old_text": old_text[:300],
            "new_text": new_text[:300],
            "threshold_old": o_thresh.get("threshold_rupees"),
            "threshold_new": n_thresh.get("threshold_rupees"),
            "effective_date": n_thresh.get("extracted_date")
        })

    return changes


if __name__ == "__main__":
    mcp.run()

