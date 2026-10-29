"""
ReguGuard Evaluation Metrics Calculator
=======================================
Implements deterministic accuracy, confusion matrix, and cost/latency aggregations.
Single Source of Truth: PRD §11.2 (Criterion 10)
"""

from __future__ import annotations
from typing import Dict, List, Any


def compute_benchmark_metrics(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes precision, recall, F1, false alarm rate, and latency/cost averages."""
    total = len(runs)
    if total == 0:
        return {}

    correct = 0
    tp = fp = fn = tn = 0
    total_latency = 0.0
    total_cost = 0.0
    total_tokens = 0

    for r in runs:
        gold = r.get("gold_verdict")
        pred = r.get("predicted_verdict")
        lat = r.get("latency_s", 0.0)
        cost = r.get("cost_usd", 0.0)
        tokens = r.get("tokens", 0)

        total_latency += lat
        total_cost += cost
        total_tokens += tokens

        if pred == gold:
            correct += 1

        if gold == "impacted":
            if pred == "impacted":
                tp += 1
            else:
                fn += 1
        else:
            if pred == "impacted":
                fp += 1
            else:
                tn += 1

    accuracy = correct / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    false_alarm_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "total_runs": total,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_alarm_rate": round(false_alarm_rate, 4),
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "avg_latency_s": round(total_latency / total, 3),
        "avg_cost_usd": round(total_cost / total, 6),
        "avg_tokens": int(total_tokens / total)
    }

