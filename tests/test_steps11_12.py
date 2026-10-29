"""
Acceptance Tests for Steps 11 & 12: Benchmarking & Provenance
============================================================
Tests:
- Benchmark metric calculation (precision, recall, F1, false alarm rate).
- Provenance graph construction and JSON/Markdown audit pack export.
"""

from pathlib import Path
import pytest
from src.schemas import ImpactReport
from src.orchestrator import ReguGuardOrchestrator
from src.observability.provenance import ProvenancePackGenerator
from eval.metrics import compute_benchmark_metrics


def test_provenance_pack_generation():
    # CONCEPT: Step 12 Acceptance Test - Provenance Pack
    orchestrator = ReguGuardOrchestrator()
    report = orchestrator.run(
        case_id="CASE-AUDIT-PROV",
        doc_id="notif_10_2023",
        prior_doc_id="notif_13_2020",
        sme_id="SME-01"
    )

    generator = ProvenancePackGenerator(report)
    graph = generator.generate_provenance_graph()

    assert graph["case_id"] == "CASE-AUDIT-PROV"
    assert "evidence_chain" in graph
    assert len(graph["evidence_chain"]) >= 1

    files = generator.export_audit_pack()
    assert Path(files["json_path"]).exists()
    assert Path(files["markdown_path"]).exists()


def test_metrics_calculation():
    # CONCEPT: Step 11 Acceptance Test - Metrics Engine
    sample_runs = [
        {"gold_verdict": "impacted", "predicted_verdict": "impacted", "latency_s": 1.2, "cost_usd": 0.0, "tokens": 100},
        {"gold_verdict": "not_impacted", "predicted_verdict": "not_impacted", "latency_s": 0.8, "cost_usd": 0.0, "tokens": 100},
        {"gold_verdict": "impacted", "predicted_verdict": "not_impacted", "latency_s": 1.0, "cost_usd": 0.0, "tokens": 100}
    ]
    res = compute_benchmark_metrics(sample_runs)
    assert res["total_runs"] == 3
    assert res["accuracy"] == round(2 / 3, 4)
    assert res["recall"] == 0.5
    assert res["false_alarm_rate"] == 0.0

