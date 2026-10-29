"""
Acceptance Test for PRD Step 10: Complete Dataset & Personas
============================================================
Tests:
- Exactly 12 synthetic SMEs with varied parameters.
- Exactly 48 labelled cases with quota distribution matching PRD §10.
- All 6 personas with 3 structural variants (18 prompt variants).
"""

import json
from pathlib import Path
import yaml
import pytest
from src.mcp_servers.sme_db import list_smes


def test_12_smes_dataset():
    # CONCEPT: 12 SME profiles (PRD §10)
    smes = list_smes()
    assert len(smes) == 12
    turnovers = [s["aato_crore"] for s in smes]
    assert min(turnovers) < 5.0  # At least one below threshold
    assert max(turnovers) > 5.0  # At least one above threshold


def test_48_labelled_cases_quota():
    # CONCEPT: 48 labelled cases quota (PRD §10)
    cases_file = Path("data/cases/cases.jsonl")
    assert cases_file.exists()

    cases = []
    with open(cases_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    assert len(cases) == 48

    categories = [c["category"] for c in cases]
    assert categories.count("direct_impact") == 12
    assert categories.count("no_impact") == 10
    assert categories.count("threshold_change") == 10
    assert categories.count("ambiguous") == 8
    assert categories.count("conflicting_amendments") == 4
    assert categories.count("adversarial") == 4


def test_18_persona_prompt_variants():
    # CONCEPT: 6 personas x 3 structural variants = 18 prompt variants (PRD §8.2, §10)
    personas = ["owner", "accountant", "consultant", "auditor", "adversarial_toxic", "adversarial_injection"]
    total_variants = 0

    for p in personas:
        p_file = Path(f"data/personas/{p}.yaml")
        assert p_file.exists(), f"Persona file {p}.yaml missing"
        with open(p_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            assert "variants" in data
            assert len(data["variants"]) == 3
            total_variants += len(data["variants"])

    assert total_variants == 18

