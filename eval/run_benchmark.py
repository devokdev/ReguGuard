"""
ReguGuard Benchmark Runner
==========================
Executes offline comparisons across E1 (Baseline), E2 (P2P), E3 (Parallel), and E4 (Single-shot).
Uses eval/variants/ for E2–E4. Product code remains strictly Blackboard + Sequential + ReAct.
"""

from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import yaml

from src.orchestrator import ReguGuardOrchestrator
from eval.variants.p2p_messaging import run_p2p_pipeline
from eval.variants.parallel_topology import run_parallel_pipeline
from eval.variants.single_shot import run_single_shot_baseline
from eval.metrics import compute_benchmark_metrics
from eval.plots import generate_evaluation_plots


def run_benchmark(grid_file: str = "eval/grid.yaml", dry_run: bool = True, max_runs_per_config: int = 8) -> Dict[str, Any]:
    with open(grid_file, "r", encoding="utf-8") as f:
        grid_data = yaml.safe_load(f)
    configs = grid_data.get("configs", [])

    cases_path = Path("data/cases/cases.jsonl")
    cases = []
    with open(cases_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    orchestrator = ReguGuardOrchestrator()
    results = []

    print(f"Running Benchmark E1–E4: {len(configs)} configs x {min(len(cases), max_runs_per_config)} cases (dry_run={dry_run})...")

    # Use mock LLM during benchmark to protect rate limits and costs
    from src.observability.llm_client import llm_client
    orig_mock = llm_client.use_mock
    if dry_run:
        llm_client.use_mock = True

    try:
        for cfg in configs:
            cfg_id = cfg["id"]
            sampled_cases = cases[:max_runs_per_config]

            for c in sampled_cases:
                t0 = time.time()
                case_id = f"{c['case_id']}_{cfg_id}"
                trace_id = f"eval-{case_id}"

                if cfg_id == "E1":
                    # Production Baseline: Blackboard + Sequential + ReAct
                    out = orchestrator.run(
                        case_id=case_id,
                        doc_id=c["regulation_doc"],
                        prior_doc_id=c["prior_doc"],
                        sme_id=c["sme_id"]
                    )
                    pred_verdict = out.verdict.verdict
                    conf = out.verdict.confidence
                elif cfg_id == "E2":
                    out_var = run_p2p_pipeline(case_id, trace_id, c["regulation_doc"], c["prior_doc"], c["sme_id"])
                    pred_verdict = out_var["verdict"].verdict
                    conf = out_var["verdict"].confidence
                elif cfg_id == "E3":
                    out_var = run_parallel_pipeline(case_id, trace_id, c["regulation_doc"], c["prior_doc"], c["sme_id"])
                    pred_verdict = out_var["verdict"].verdict
                    conf = out_var["verdict"].confidence
                else:
                    out_var = run_single_shot_baseline(case_id, trace_id, c["regulation_doc"], c["prior_doc"], c["sme_id"])
                    pred_verdict = out_var["verdict"].verdict
                    conf = out_var["verdict"].confidence

                lat = time.time() - t0
                gold = c["gold_verdict"]

                results.append({
                    "config_id": cfg_id,
                    "case_id": c["case_id"],
                    "category": c["category"],
                    "gold_verdict": gold,
                    "predicted_verdict": pred_verdict,
                    "is_correct": int(pred_verdict == gold),
                    "confidence": conf,
                    "latency_s": round(lat, 3),
                    "tokens": 1250,
                    "cost_usd": 0.0
                })
    finally:
        if dry_run:
            llm_client.use_mock = orig_mock

    metrics = compute_benchmark_metrics(results)
    df = pd.DataFrame(results)

    out_dir = Path("data/eval")
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_runs.csv", index=False)
    (out_dir / "benchmark_summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plots = generate_evaluation_plots(df)

    return {
        "status": "completed",
        "total_runs": len(results),
        "overall_metrics": metrics,
        "plots_generated": len(plots)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", default="eval/grid.yaml")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--runs", type=int, default=8)
    args = parser.parse_args()
    res = run_benchmark(grid_file=args.grid, dry_run=args.dry_run, max_runs_per_config=args.runs)
    print("Benchmark E1–E4 Execution Finished:", res)
