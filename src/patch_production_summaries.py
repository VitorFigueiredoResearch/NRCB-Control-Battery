#!/usr/bin/env python3
# Copyright (C) 2026 Vitor M. F. Figueiredo
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of the Nisa Radial Control Battery (NRCB).
"""Regenerate derived production summaries from existing realization rows."""
from __future__ import annotations

import csv
import math
import os
from collections import defaultdict
from pathlib import Path

import numpy as np


SCRIPT_PATH = Path(__file__).resolve()
PAPER_ROOT = SCRIPT_PATH.parent.parent
OUTPUT_DIR = PAPER_ROOT / "results" / "m_surrogate_extension_v1"
REALIZATION_FILE = OUTPUT_DIR / "per_realization_controls.csv"
GALAXY_SUMMARY_FILE = OUTPUT_DIR / "per_galaxy_null_summary.csv"
GLOBAL_SUMMARY_FILE = OUTPUT_DIR / "global_control_battery_summary.csv"
FIGURE_FILE = OUTPUT_DIR / "figure2_source_data.csv"
REPORT_FILE = OUTPUT_DIR / "execution_report.md"

TOL = 1e-12
QUANTILE_METHOD = "linear"
SHIFT_TIERS = {"circular_shift_control_partial_rank", "circular_shift_control_partial_rank_absolute"}
PHASE_TIERS = {"random_phase_surrogate_residual", "random_phase_surrogate_radial_template"}

REALIZATION_COLUMNS = ["galaxy_id", "canonical_galaxy_name", "sample_branch", "control_tier", "realization_type", "iteration", "seed", "shift_offset", "n_valid_radii", "statistic_name", "statistic_value", "valid_output", "invalid_reason", "source_script", "source_input_file", "notes"]
GALAXY_SUMMARY_COLUMNS = ["galaxy_id", "sample_branch", "control_tier", "n_realizations", "n_valid_realizations", "observed_statistic", "control_median", "control_mean", "control_std", "control_p05", "control_p16", "control_p84", "control_p95", "empirical_percentile_observed", "empirical_p_two_sided", "finite_status", "notes"]
GLOBAL_SUMMARY_COLUMNS = ["sample_branch", "control_tier", "n_galaxies", "total_realizations", "observed_median", "control_median_of_medians", "control_global_p05", "control_global_p95", "median_empirical_percentile", "notes"]
FIGURE_COLUMNS = ["panel", "sample_branch", "control_tier", "value_type", "statistic_value", "galaxy_id", "realization", "notes"]


def as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return math.nan
    return number if math.isfinite(number) else math.nan


def text_number(value: object) -> str:
    number = as_float(value)
    return "" if not math.isfinite(number) else f"{number:.17g}"


def quantile(values: np.ndarray, probability: float) -> float:
    return float(np.quantile(values, probability, method=QUANTILE_METHOD))


def empirical_midrank(values: np.ndarray, observed: float) -> float:
    delta = values - observed
    lt_count = int(np.count_nonzero(delta < -TOL))
    eq_count = int(np.count_nonzero(np.abs(delta) <= TOL))
    gt_count = int(np.count_nonzero(delta > TOL))
    if lt_count + eq_count + gt_count != values.size:
        raise RuntimeError("Empirical rank counts do not partition controls")
    return min(1.0, max(0.0, (lt_count + 0.5 * eq_count) / values.size))


def empirical_two_sided_abs(values: np.ndarray, observed: float) -> float:
    result = (1 + int(np.count_nonzero(np.abs(values) >= abs(observed) - TOL))) / (values.size + 1)
    return min(1.0, max(0.0, result))


def read_existing_summaries() -> tuple[dict[tuple[str, str, str], dict[str, str]], list[str]]:
    with GALAXY_SUMMARY_FILE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != GALAXY_SUMMARY_COLUMNS:
            raise RuntimeError("Existing per-galaxy summary schema mismatch")
        rows = list(reader)
    return {(row["galaxy_id"], row["sample_branch"], row["control_tier"]): row for row in rows}, reader.fieldnames


def stream_groups() -> dict[tuple[str, str, str], dict[str, object]]:
    groups: dict[tuple[str, str, str], dict[str, object]] = {}
    with REALIZATION_FILE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REALIZATION_COLUMNS:
            raise RuntimeError("Realization schema mismatch")
        for row in reader:
            key = (row["galaxy_id"], row["sample_branch"], row["control_tier"])
            group = groups.setdefault(
                key,
                {
                    "n_realizations": 0,
                    "values": [],
                    "fixed": True,
                    "n_valid_radii": None,
                    "offsets": set(),
                },
            )
            group["n_realizations"] = int(group["n_realizations"]) + 1
            group["fixed"] = bool(group["fixed"]) and row["realization_type"] == "fixed_reference"
            if row["n_valid_radii"]:
                n_valid = int(row["n_valid_radii"])
                if group["n_valid_radii"] not in {None, n_valid}:
                    raise RuntimeError(f"Conflicting n_valid_radii for {key}")
                group["n_valid_radii"] = n_valid
            if row["shift_offset"]:
                offsets = group["offsets"]
                assert isinstance(offsets, set)
                offset = int(row["shift_offset"])
                if offset in offsets:
                    raise RuntimeError(f"Duplicate shift offset for {key}")
                offsets.add(offset)
            if row["valid_output"] == "TRUE":
                if not row["statistic_value"]:
                    raise RuntimeError(f"Valid row missing statistic value for {key}")
                values = group["values"]
                assert isinstance(values, list)
                values.append(float(row["statistic_value"]))
    return groups


def summarize_groups(
    groups: dict[tuple[str, str, str], dict[str, object]],
    existing: dict[tuple[str, str, str], dict[str, str]],
) -> tuple[list[dict[str, object]], dict[tuple[str, str], list[float]]]:
    summaries: list[dict[str, object]] = []
    pooled_by_tier: dict[tuple[str, str], list[float]] = defaultdict(list)
    if set(groups) != set(existing):
        raise RuntimeError("Realization groups do not match existing summary groups")

    for key in sorted(groups):
        gid, branch, tier = key
        group = groups[key]
        prior = existing[key]
        values = np.asarray(group["values"], dtype=float)
        if values.size and not np.all(np.isfinite(values)):
            raise RuntimeError(f"Nonfinite valid controls for {key}")
        observed = as_float(prior["observed_statistic"])
        fixed = bool(group["fixed"])
        percentile = empirical_p = math.nan
        status = "NO_VALID_REALIZATIONS"
        notes = "Per-galaxy summary; not a pooled p-value"

        if fixed:
            status = "FIXED_REFERENCE_NOT_NULL"
            notes = "Fixed reference: percentile and p-value empty"
        elif tier in SHIFT_TIERS:
            n_valid_radii = int(group["n_valid_radii"])
            offsets = group["offsets"]
            assert isinstance(offsets, set)
            if offsets != set(range(1, n_valid_radii)):
                raise RuntimeError(f"Non-exhaustive production shift group: {key}")
            if values.size:
                percentile = empirical_midrank(values, observed)
                empirical_p = empirical_two_sided_abs(values, observed)
                status = "FINITE_EXACT_SHIFT"
        elif values.size:
            percentile = empirical_midrank(values, observed)
            if tier in PHASE_TIERS:
                empirical_p = min(1.0, max(0.0, 2.0 * min(percentile, 1.0 - percentile)))
                status = "DEGENERATE_PHASE_BLIND_STATISTIC" if np.ptp(values) <= TOL else "FINITE"
            else:
                empirical_p = empirical_two_sided_abs(values, observed)
                status = "FINITE_RANDOM_ENSEMBLE"

        if math.isfinite(percentile) and not 0.0 <= percentile <= 1.0:
            raise RuntimeError(f"Out-of-range empirical percentile for {key}: {percentile}")
        if math.isfinite(empirical_p) and not 0.0 <= empirical_p <= 1.0:
            raise RuntimeError(f"Out-of-range empirical p-value for {key}: {empirical_p}")
        if fixed and (math.isfinite(percentile) or math.isfinite(empirical_p)):
            raise RuntimeError(f"Fixed reference has empirical fields for {key}")

        getq = lambda probability: quantile(values, probability) if values.size else math.nan
        summaries.append(
            {
                "galaxy_id": gid,
                "sample_branch": branch,
                "control_tier": tier,
                "n_realizations": int(group["n_realizations"]),
                "n_valid_realizations": values.size,
                "observed_statistic": prior["observed_statistic"],
                "control_median": text_number(np.median(values) if values.size else math.nan),
                "control_mean": text_number(np.mean(values) if values.size else math.nan),
                "control_std": text_number(np.std(values) if values.size else math.nan),
                "control_p05": text_number(getq(0.05)),
                "control_p16": text_number(getq(0.16)),
                "control_p84": text_number(getq(0.84)),
                "control_p95": text_number(getq(0.95)),
                "empirical_percentile_observed": text_number(percentile),
                "empirical_p_two_sided": text_number(empirical_p),
                "finite_status": status,
                "notes": notes,
            }
        )
        pooled_by_tier[(branch, tier)].extend(values.tolist())
    return summaries, pooled_by_tier


def summarize_global(
    summaries: list[dict[str, object]],
    pooled_by_tier: dict[tuple[str, str], list[float]],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in summaries:
        grouped[(str(row["sample_branch"]), str(row["control_tier"]))].append(row)
    output: list[dict[str, object]] = []
    for key in sorted(grouped):
        branch, tier = key
        group = grouped[key]
        finite = lambda field: np.asarray([as_float(row[field]) for row in group if math.isfinite(as_float(row[field]))])
        observed = finite("observed_statistic")
        medians = finite("control_median")
        percentiles = finite("empirical_percentile_observed")
        pooled = np.asarray(pooled_by_tier[key], dtype=float)
        output.append(
            {
                "sample_branch": branch,
                "control_tier": tier,
                "n_galaxies": len(group),
                "total_realizations": sum(int(row["n_realizations"]) for row in group),
                "observed_median": text_number(np.median(observed) if observed.size else math.nan),
                "control_median_of_medians": text_number(np.median(medians) if medians.size else math.nan),
                "control_global_p05": text_number(quantile(pooled, 0.05) if pooled.size else math.nan),
                "control_global_p95": text_number(quantile(pooled, 0.95) if pooled.size else math.nan),
                "median_empirical_percentile": text_number(np.median(percentiles) if percentiles.size else math.nan),
                "notes": "Descriptive across-galaxy summary only; not a pooled empirical test",
            }
        )
    return output


def make_figure_rows(summaries: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in summaries:
        panel = "partial_rank_controls" if row["sample_branch"] == "partial_rank_134" else "spectral_controls"
        for value_type, field in [("observed", "observed_statistic"), ("control_median", "control_median"), ("control_p05", "control_p05"), ("control_p95", "control_p95")]:
            if row[field]:
                output.append(
                    {
                        "panel": panel,
                        "sample_branch": row["sample_branch"],
                        "control_tier": row["control_tier"],
                        "value_type": value_type,
                        "statistic_value": row[field],
                        "galaxy_id": row["galaxy_id"],
                        "realization": "per_galaxy_summary",
                        "notes": "Lightweight plot-ready branch-labeled summary",
                    }
                )
    return output


def validate_summaries(summaries: list[dict[str, object]]) -> None:
    for row in summaries:
        fixed = row["finite_status"] == "FIXED_REFERENCE_NOT_NULL"
        for field in ["empirical_percentile_observed", "empirical_p_two_sided"]:
            value = str(row[field])
            if fixed and value:
                raise RuntimeError(f"Fixed reference has non-empty {field}")
            if value and not 0.0 <= float(value) <= 1.0:
                raise RuntimeError(f"Out-of-range {field}: {value}")


def atomic_write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def patch_report() -> None:
    text = REPORT_FILE.read_text(encoding="utf-8")
    stale = "- A separate test-mode QC rerun is required before production execution."
    replacement = "- Production outputs have been generated. A separate production-output QC is required before manuscript use or terminology upgrade."
    if stale in text:
        text = text.replace(stale, replacement)
    elif replacement not in text:
        raise RuntimeError("Expected production report requirement wording not found")
    patch_note = "- Derived summary outputs were corrected after production QC; realization rows were not regenerated or modified."
    if patch_note not in text:
        text = text.rstrip() + "\n\n## Derived summary patch\n\n" + patch_note + "\n- Production terminology upgrade remains unauthorized until a production-QC rerun passes.\n"
    temporary = REPORT_FILE.with_suffix(REPORT_FILE.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, REPORT_FILE)


def main() -> None:
    existing, _ = read_existing_summaries()
    groups = stream_groups()
    summaries, pooled = summarize_groups(groups, existing)
    validate_summaries(summaries)
    globals_ = summarize_global(summaries, pooled)
    figures = make_figure_rows(summaries)
    atomic_write_csv(GALAXY_SUMMARY_FILE, GALAXY_SUMMARY_COLUMNS, summaries)
    atomic_write_csv(GLOBAL_SUMMARY_FILE, GLOBAL_SUMMARY_COLUMNS, globals_)
    atomic_write_csv(FIGURE_FILE, FIGURE_COLUMNS, figures)
    patch_report()
    print("Derived production summaries regenerated from existing realization rows.")
    print("Production execution was not rerun.")
    print("Production terminology upgrade authorized? NO, QC_RERUN_REQUIRED")


if __name__ == "__main__":
    main()
