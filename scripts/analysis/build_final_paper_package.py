#!/usr/bin/env python
"""Build the final paper-facing package from frozen/derived source snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from rsfm_fairness_audit.final_paper_cleanup import (  # noqa: E402
    build_experiment8_tables,
    build_experiment9_tables,
    build_reben_example_tables,
    markdown_table,
    read_csv,
    sha256_file,
    write_csv,
)


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _plot_exp9(summary, out):
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.7), sharey=False)
    colors = {"primary_risk": "#0072B2", "M": "#009E73", "T": "#D55E00", "D": "#CC79A7"}
    for ax, task in zip(axes, ("fmow", "reben")):
        rows = [r for r in summary if r["task"] == task]
        x = np.arange(4)
        ax.bar(x, [r["mean_delta_dofav2_minus_terramind"] for r in rows], color=[colors[r["metric"]] for r in rows])
        ax.errorbar(x, [r["mean_delta_dofav2_minus_terramind"] for r in rows], yerr=[r["sd"] for r in rows], fmt="none", ecolor="#222222", capsize=3)
        ax.axhline(0, color="#333333", linewidth=.8)
        ax.set_xticks(x, [r["metric"] for r in rows])
        ax.set_title("fMoW" if task == "fmow" else "reBEN")
        ax.set_ylabel("DOFAv2 − TerraMind (risk; higher is worse)")
        ax.text(.02, .96, "3/3 seeds, same direction", transform=ax.transAxes, va="top", fontsize=8)
    fig.suptitle("Experiment 9: task-wise paired model contrasts", fontsize=12, fontweight="bold")
    fig.tight_layout()
    _save(fig, out / "experiment9_taskwise_paired_contrasts")


def _plot_exp8(stage, out):
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6))
    order = ["A_ID", "A_shifted", "B_threshold", "C_head"]
    labels = ["A: S2 ID", "A: S1 shift", "B: thresholds", "C: S1 head"]
    colors = ["#56B4E9", "#D55E00", "#E69F00", "#009E73"]
    for ax, metric in zip(axes, ("AUROC", "M", "T", "D")):
        rows = {r["paper_stage"]: r for r in stage if r["metric"] == metric}
        means = [rows[k]["mean"] for k in order]
        sds = [rows[k]["sd"] for k in order]
        x = np.arange(4)
        ax.bar(x, means, color=colors)
        ax.errorbar(x, means, yerr=sds, fmt="none", ecolor="#222222", capsize=3)
        ax.set_xticks(x, labels, rotation=35, ha="right")
        ax.set_title(metric)
        if metric != "AUROC":
            ax.set_ylabel("Risk (lower is better)")
        else:
            ax.set_ylabel("AUROC (higher is better)")
    fig.suptitle("Experiment 8: adaptation ladder on frozen paired S2→S1 shift", fontsize=12, fontweight="bold")
    fig.tight_layout()
    _save(fig, out / "experiment8_adaptation_ladder")


def _plot_reben(selected, out):
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    labels = [f"{r['country']} ×\n{r['class_label']}" for r in selected]
    values = [float(r["mean_delta_risk"]) for r in selected]
    errors = [float(r["delta_risk_sd"]) for r in selected]
    colors = ["#D55E00" if v >= 0 else "#0072B2" for v in values]
    x = np.arange(len(values))
    ax.bar(x, values, color=colors)
    ax.errorbar(x, values, yerr=errors, fmt="none", ecolor="#222222", capsize=3)
    ax.axhline(0, color="#222222", linewidth=.8)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylabel("TerraMind S1−S2 Δrisk (higher is worse)")
    ax.set_title("reBEN: pre-specified country×label shift archetypes", fontweight="bold")
    ax.text(.01, -.28, "Examples selected deterministically from the saved 190-cell candidate universe; CROMA comparison is label-level.", transform=ax.transAxes, fontsize=8)
    fig.tight_layout()
    _save(fig, out / "reben_country_label_shift_examples")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper tables and figures from explicit input metrics.")
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    src, out = args.source_dir.resolve(), args.output_dir.resolve()
    if src == out or src in out.parents or out in src.parents:
        raise ValueError("Input and output directories must be disjoint.")
    names = ["experiment9_cell_seed_metrics.csv", "experiment8_adaptation_stage_metrics.csv",
             "experiment8_adaptation_recovery.csv", "reben_terramind_country_label_burden.csv",
             "reben_terramind_label_diagnostics.csv", "reben_croma_label_diagnostics.csv"]
    missing = [name for name in names if not (src / name).is_file()]
    if missing:
        raise FileNotFoundError("Missing paper inputs: " + ", ".join(missing))
    before = {name: sha256_file(src / name) for name in names}
    exp9_seed, exp9_summary = build_experiment9_tables(read_csv(src / names[0]))
    exp8_stage, exp8_recovery = build_experiment8_tables(read_csv(src / names[1]), read_csv(src / names[2]))
    universe, selected = build_reben_example_tables(read_csv(src / names[3]), read_csv(src / names[4]), read_csv(src / names[5]))
    tables, figures = out / "tables", out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    for name, rows in [("experiment9_paired_deltas", exp9_seed), ("experiment9_summary", exp9_summary),
                       ("experiment8_stages", exp8_stage), ("experiment8_recovery", exp8_recovery),
                       ("reben_candidate_universe", universe), ("reben_selected_examples", selected)]:
        write_csv(tables / (name + ".csv"), rows)
    _plot_exp9(exp9_summary, figures)
    _plot_exp8(exp8_stage, figures)
    _plot_reben(selected, figures)
    after = {name: sha256_file(src / name) for name in names}
    if before != after:
        raise RuntimeError("Source metrics changed during figure generation.")
    (out / "manifest.json").write_text(json.dumps({"status": "complete", "source_sha256": before,
        "source_immutable": True, "inputs_distributed": False}, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
