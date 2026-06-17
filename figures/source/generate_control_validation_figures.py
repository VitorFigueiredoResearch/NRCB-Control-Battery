#!/usr/bin/env python3
# Copyright (C) 2026 Vitor M. F. Figueiredo
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of the Nisa Radial Control Battery (NRCB).
"""Generate neutral manuscript-ready figures from QC-accepted summaries."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def discover_release_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "results" / "m_surrogate_extension_v1").is_dir():
            return parent
    raise RuntimeError("Could not locate release root containing results/m_surrogate_extension_v1")


PAPER_ROOT = discover_release_root()
FIGURE_DIR = PAPER_ROOT / "figures"
RESULT_DIR = PAPER_ROOT / "results" / "m_surrogate_extension_v1"
SUMMARY_FILE = RESULT_DIR / "per_galaxy_null_summary.csv"
GLOBAL_FILE = RESULT_DIR / "global_control_battery_summary.csv"

COLORS = {
    "observed": "#222222",
    "shuffle": "#4C78A8",
    "shift": "#F58518",
    "phase": "#54A24B",
    "fixed": "#9D755D",
    "template": "#B279A2",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def values(rows: list[dict[str, str]], tier: str, field: str) -> np.ndarray:
    return np.asarray([float(row[field]) for row in rows if row["control_tier"] == tier and row[field]], dtype=float)


def save_figure(figure: plt.Figure, stem: str) -> None:
    output_stem = stem if stem.endswith("_rev1") else f"{stem}_rev1"
    figure.savefig(FIGURE_DIR / f"{output_stem}.pdf", bbox_inches="tight")
    figure.savefig(FIGURE_DIR / f"{output_stem}.png", dpi=300, bbox_inches="tight")
    plt.close(figure)


def add_box(ax: plt.Axes, xy: tuple[float, float], width: float, height: float, text: str, color: str) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        linewidth=1.2,
        edgecolor=color,
        facecolor="white",
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=9)


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.0, color="#555555"))


def figure1_workflow() -> None:
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Control workflow for radial-structure diagnostics", fontsize=14, pad=14)

    add_box(ax, (0.35, 0.81), 0.30, 0.11, "Observed radial diagnostic statistic", COLORS["observed"])
    add_box(ax, (0.08, 0.57), 0.35, 0.13, "Partial-rank branch: N=134\nRadius-conditioned statistic", COLORS["shuffle"])
    add_box(ax, (0.57, 0.57), 0.35, 0.13, "Spectral-control branch: N=76\nSpectral concentration", COLORS["phase"])
    add_box(ax, (0.04, 0.31), 0.18, 0.13, "Shuffle / permutation\ncontrol distributions", COLORS["shuffle"])
    add_box(ax, (0.27, 0.31), 0.20, 0.13, "Exhaustive circular-shift\nrandomization distributions", COLORS["shift"])
    add_box(ax, (0.53, 0.31), 0.20, 0.13, "Amplitude-preserving\nrandom-phase controls\nphase-blind caveat", COLORS["phase"])
    add_box(ax, (0.78, 0.31), 0.18, 0.13, "Smooth references\nfixed, not stochastic", COLORS["fixed"])
    add_box(ax, (0.31, 0.07), 0.38, 0.12, "QC and language lock\nBranch labels, validity, and scope checks", "#666666")

    add_arrow(ax, (0.44, 0.81), (0.27, 0.70))
    add_arrow(ax, (0.56, 0.81), (0.73, 0.70))
    add_arrow(ax, (0.21, 0.57), (0.14, 0.44))
    add_arrow(ax, (0.31, 0.57), (0.37, 0.44))
    add_arrow(ax, (0.68, 0.57), (0.63, 0.44))
    add_arrow(ax, (0.79, 0.57), (0.87, 0.44))
    for start, end in [
        ((0.13, 0.31), (0.39, 0.19)),
        ((0.37, 0.31), (0.46, 0.19)),
        ((0.63, 0.31), (0.54, 0.19)),
        ((0.87, 0.31), (0.61, 0.19)),
    ]:
        add_arrow(ax, start, end)
    save_figure(fig, "figure1_workflow_control_validation")


def styled_boxplot(ax: plt.Axes, data: list[np.ndarray], labels: list[str], colors: list[str]) -> None:
    box = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.58, showfliers=False)
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.30)
        patch.set_edgecolor(color)
    for median in box["medians"]:
        median.set_color("#111111")
        median.set_linewidth(1.5)
    for whisker, cap in zip(box["whiskers"], box["caps"] * 2):
        whisker.set_color("#555555")
        cap.set_color("#555555")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.7)


def figure2_control_comparison(summary_rows: list[dict[str, str]], global_rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), constrained_layout=True)
    fig.suptitle("Branch-separated control-distribution comparison", fontsize=14)

    observed_abs = values(summary_rows, "shuffle_surrogate_partial_rank_absolute", "observed_statistic")
    shuffle_median = values(summary_rows, "shuffle_surrogate_partial_rank_absolute", "control_median")
    shift_median = values(summary_rows, "circular_shift_control_partial_rank_absolute", "control_median")
    styled_boxplot(
        axes[0],
        [observed_abs, shuffle_median, shift_median],
        ["Observed\n$|\\rho_{partial}|$", "Shuffle\ncontrol median", "Circular-shift\ncontrol median"],
        [COLORS["observed"], COLORS["shuffle"], COLORS["shift"]],
    )
    axes[0].set_title("Partial-rank branch (N=134)")
    axes[0].set_ylabel("Per-galaxy statistic")
    axes[0].set_ylim(-0.03, 1.03)
    axes[0].text(
        0.02,
        0.02,
        "Control entries are per-galaxy control-distribution medians.\nCircular shifts are exhaustive nontrivial offsets.",
        transform=axes[0].transAxes,
        fontsize=8,
        va="bottom",
    )

    residual_observed = values(summary_rows, "random_phase_surrogate_residual", "observed_statistic")
    residual_control = values(summary_rows, "random_phase_surrogate_residual", "control_median")
    template_observed = values(summary_rows, "random_phase_surrogate_radial_template", "observed_statistic")
    template_control = values(summary_rows, "random_phase_surrogate_radial_template", "control_median")
    styled_boxplot(
        axes[1],
        [residual_observed, residual_control, template_observed, template_control],
        ["Residual\nobserved", "Residual\nrandom-phase", "Template\nobserved", "Template\nrandom-phase"],
        [COLORS["observed"], COLORS["phase"], COLORS["template"], COLORS["phase"]],
    )
    fixed = {
        row["control_tier"]: float(row["control_median_of_medians"])
        for row in global_rows
        if row["control_tier"].startswith("smooth_profile_")
    }
    line_styles = ["--", "-.", ":"]
    fixed_labels = ["Exponential fixed reference", "Linear fixed reference", "Quadratic fixed reference"]
    for value, style, label in zip(fixed.values(), line_styles, fixed_labels):
        axes[1].axhline(value, color=COLORS["fixed"], linestyle=style, linewidth=1.2, label=label)
    axes[1].set_title("Spectral-control branch (N=76)")
    axes[1].set_ylabel("Spectral concentration")
    axes[1].set_ylim(0.30, 1.02)
    axes[1].legend(fontsize=7.5, loc="lower right")
    axes[1].text(
        0.02,
        0.98,
        "Random-phase equality is phase-blind/by construction.\nSmooth references are fixed, not stochastic.",
        transform=axes[1].transAxes,
        fontsize=8,
        va="top",
    )
    save_figure(fig, "figure2_control_distribution_comparison")


def figure3_spectral_caveat(summary_rows: list[dict[str, str]], global_rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.1), constrained_layout=True)
    fig.suptitle("Spectral-control branch: phase-blind statistic and fixed references (N=76)", fontsize=13.5)

    for tier, label, color, marker in [
        ("random_phase_surrogate_residual", "Residual profile", COLORS["phase"], "o"),
        ("random_phase_surrogate_radial_template", "Radial-template profile", COLORS["template"], "s"),
    ]:
        observed = values(summary_rows, tier, "observed_statistic")
        controls = values(summary_rows, tier, "control_median")
        axes[0].scatter(observed, controls, s=24, alpha=0.62, color=color, marker=marker, label=label, edgecolors="none")
    axes[0].plot([0.35, 0.95], [0.35, 0.95], color="#333333", linewidth=1.0, linestyle="--", label="Identity")
    axes[0].set_xlim(0.35, 0.95)
    axes[0].set_ylim(0.35, 0.95)
    axes[0].set_xlabel("Observed spectral concentration")
    axes[0].set_ylabel("Random-phase control median")
    axes[0].set_title("Amplitude-preserving random-phase controls")
    axes[0].grid(color="#DDDDDD", linewidth=0.7)
    axes[0].legend(fontsize=8)
    axes[0].text(
        0.03,
        0.97,
        "Spectral concentration is phase-blind under\namplitude-preserving random-phase controls.",
        transform=axes[0].transAxes,
        va="top",
        fontsize=8.5,
    )

    global_by_tier = {row["control_tier"]: row for row in global_rows}
    labels = ["Residual\nobserved", "Residual\nrandom-phase", "Template\nobserved", "Template\nrandom-phase", "Exponential\nfixed", "Linear\nfixed", "Quadratic\nfixed"]
    medians = [
        float(global_by_tier["random_phase_surrogate_residual"]["observed_median"]),
        float(global_by_tier["random_phase_surrogate_residual"]["control_median_of_medians"]),
        float(global_by_tier["random_phase_surrogate_radial_template"]["observed_median"]),
        float(global_by_tier["random_phase_surrogate_radial_template"]["control_median_of_medians"]),
        float(global_by_tier["smooth_profile_exponential_reference"]["control_median_of_medians"]),
        float(global_by_tier["smooth_profile_linear_reference"]["control_median_of_medians"]),
        float(global_by_tier["smooth_profile_quadratic_reference"]["control_median_of_medians"]),
    ]
    colors = [COLORS["observed"], COLORS["phase"], COLORS["template"], COLORS["phase"], COLORS["fixed"], COLORS["fixed"], COLORS["fixed"]]
    bars = axes[1].bar(np.arange(len(labels)), medians, color=colors, alpha=0.72)
    for index in (4, 5, 6):
        bars[index].set_hatch("//")
        bars[index].set_alpha(0.45)
    axes[1].set_xticks(np.arange(len(labels)), labels, rotation=28, ha="right")
    axes[1].set_ylabel("Across-galaxy median spectral concentration")
    axes[1].set_ylim(0.45, 0.82)
    axes[1].set_title("Descriptive summaries and fixed references")
    axes[1].grid(axis="y", color="#DDDDDD", linewidth=0.7)
    axes[1].text(
        0.02,
        0.98,
        "Hatched bars: fixed references, not stochastic controls.",
        transform=axes[1].transAxes,
        va="top",
        fontsize=8.5,
    )
    save_figure(fig, "figure3_spectral_phase_control_caveat")


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )
    summary_rows = read_csv(SUMMARY_FILE)
    global_rows = read_csv(GLOBAL_FILE)
    figure1_workflow()
    figure2_control_comparison(summary_rows, global_rows)
    figure3_spectral_caveat(summary_rows, global_rows)
    print("Figure 1 generated from workflow specification.")
    print("Figure 2 generated from branch-labelled per-galaxy summaries.")
    print("Figure 3 generated with phase-blind and fixed-reference caveats.")


if __name__ == "__main__":
    main()
