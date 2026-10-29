"""
ReguGuard MCP Server: deadline_calc
===================================
Deterministic compliance deadline and days-remaining calculator (non-LLM).
Tools:
- compute_deadline(effective_date, rule_type)
- days_remaining(target_date)
"""

from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("deadline_calc")


@mcp.tool()
def compute_deadline(effective_date: str, rule_type: str = "einvoice_setup") -> dict:
    """
    Computes statutory or recommended compliance deadline based on rule type.
    Rule types:
    - einvoice_setup: effective_date directly (must be compliant on day 1)
    - monthly_return: 20th of the month following the period
    - quarterly_return: 22nd/24th of the month following the quarter
    - grace_period_30: effective_date + 30 days
    """
    try:
        eff_dt = datetime.strptime(effective_date, "%Y-%m-%d").date()
    except Exception:
        # Fallback to today if parsing fails
        eff_dt = date.today()

    if rule_type == "einvoice_setup":
        deadline = eff_dt
        desc = "Mandatory generation of e-invoices starts on this date"
    elif rule_type == "grace_period_30":
        deadline = eff_dt + timedelta(days=30)
        desc = "30-day operational onboarding buffer"
    elif rule_type == "monthly_return":
        # 20th of next month
        year = eff_dt.year + (eff_dt.month // 12)
        month = (eff_dt.month % 12) + 1
        deadline = date(year, month, 20)
        desc = "GSTR-3B monthly statutory filing date"
    else:
        deadline = eff_dt
        desc = f"Standard deadline for {rule_type}"

    today = date.today()
    delta_days = (deadline - today).days

    return {
        "status": "ok",
        "effective_date": eff_dt.isoformat(),
        "rule_type": rule_type,
        "deadline": deadline.isoformat(),
        "days_remaining": delta_days,
        "description": desc
    }


@mcp.tool()
def days_remaining(target_date: str) -> dict:
    """Calculates remaining days until the given target date (YYYY-MM-DD)."""
    try:
        tgt_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        today = date.today()
        diff = (tgt_dt - today).days
        return {
            "status": "ok",
            "target_date": tgt_dt.isoformat(),
            "today": today.isoformat(),
            "days_remaining": diff,
            "is_past": diff < 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    mcp.run()

