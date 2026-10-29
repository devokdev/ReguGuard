"""
ReguGuard Benchmark Visualizations Generator
============================================
Generates Boxplots, Cost-vs-Accuracy charts, and Heatmaps mandated by PRD §11.3.
Saves PNG charts into data/eval/plots/ using Plotly.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def generate_evaluation_plots(results_df: pd.DataFrame, out_dir: Path | str = "data/eval/plots") -> List[str]:
    """Generates all required Plotly charts and writes HTML/JSON representations."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated = []

    if results_df.empty:
        return generated

    # 1. Boxplot: Latency by Config
    fig_lat = px.box(
        results_df,
        x="config_id",
        y="latency_s",
        points="all",
        title="Latency Distribution Across Architecture Configs (s)",
        labels={"config_id": "Architecture Config", "latency_s": "Latency (seconds)"}
    )
    lat_file = out_path / "latency_boxplot.json"
    lat_file.write_text(fig_lat.to_json(), encoding="utf-8")
    generated.append(str(lat_file))

    # 2. Boxplot: Tokens by Config
    fig_tok = px.box(
        results_df,
        x="config_id",
        y="tokens",
        points="all",
        title="Token Usage Across Architecture Configs",
        labels={"config_id": "Architecture Config", "tokens": "Total Tokens"}
    )
    tok_file = out_path / "tokens_boxplot.json"
    tok_file.write_text(fig_tok.to_json(), encoding="utf-8")
    generated.append(str(tok_file))

    # 3. Accuracy vs Cost Scatter
    if "is_correct" in results_df.columns:
        summary = results_df.groupby("config_id").agg({
            "is_correct": "mean",
            "latency_s": "mean",
            "tokens": "mean"
        }).reset_index()

        fig_acc = px.scatter(
            summary,
            x="latency_s",
            y="is_correct",
            text="config_id",
            title="Accuracy vs Mean Latency by Configuration",
            labels={"latency_s": "Mean Latency (s)", "is_correct": "Accuracy"}
        )
        acc_file = out_path / "accuracy_vs_latency.json"
        acc_file.write_text(fig_acc.to_json(), encoding="utf-8")
        generated.append(str(acc_file))

    return generated

