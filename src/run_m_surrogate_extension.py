#!/usr/bin/env python3
# Copyright (C) 2026 Vitor M. F. Figueiredo
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of the Nisa Radial Control Battery (NRCB).
"""Neutral, reproducible M-surrogate control engine."""
from __future__ import annotations

import argparse, ast, csv, hashlib, importlib.util, json, math, platform, subprocess, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np

SCRIPT_PATH = Path(__file__).resolve()
PAPER_ROOT = SCRIPT_PATH.parent.parent
NOTES_DIR = PAPER_ROOT / "notes"
OUTPUT_DIR = PAPER_ROOT / "results" / "m_surrogate_extension_v1"
BASE_SEED = 20260503
SEED_NAMESPACE = "ac-control-validation-m-surrogate-v1"
RANDOM_M_REQUESTED, TEST_GALAXIES, TEST_RANDOM_M, TEST_SHIFT_LIMIT = 1000, 2, 3, 3
GRID_LENGTH, MIN_PARTIAL_POINTS, MIN_SPECTRAL_POINTS = 64, 5, 16
QUANTILE_METHOD = "linear"
ATTRITION_FILE = NOTES_DIR / "SAMPLE_ATTRITION_134_TO_76.csv"
CONTRACT_FILES = [NOTES_DIR / name for name in ["M_SURROGATE_EXTENSION_DESIGN.md", "EVIDENCE_LOCK.md", "SAMPLE_ATTRITION_134_TO_76.csv", "HEADLINE_VALUE_RECOMPUTE.csv", "REALIZATION_CENSUS.csv"]]
REALIZATION_COLUMNS = ["galaxy_id", "canonical_galaxy_name", "sample_branch", "control_tier", "realization_type", "iteration", "seed", "shift_offset", "n_valid_radii", "statistic_name", "statistic_value", "valid_output", "invalid_reason", "source_script", "source_input_file", "notes"]
GALAXY_SUMMARY_COLUMNS = ["galaxy_id", "sample_branch", "control_tier", "n_realizations", "n_valid_realizations", "observed_statistic", "control_median", "control_mean", "control_std", "control_p05", "control_p16", "control_p84", "control_p95", "empirical_percentile_observed", "empirical_p_two_sided", "finite_status", "notes"]
GLOBAL_SUMMARY_COLUMNS = ["sample_branch", "control_tier", "n_galaxies", "total_realizations", "observed_median", "control_median_of_medians", "control_global_p05", "control_global_p95", "median_empirical_percentile", "notes"]
FIGURE_COLUMNS = ["panel", "sample_branch", "control_tier", "value_type", "statistic_value", "galaxy_id", "realization", "notes"]
MANIFEST_COLUMNS = ["run_id", "timestamp", "base_seed", "code_version_or_git_hash_if_available", "input_file", "output_file", "tier", "M_requested", "M_effective", "status", "notes"]
WARNING_COLUMNS = ["warning_id", "tier", "galaxy", "warning_type", "message", "severity", "action_required"]
OUTPUT_NAMES = ["per_realization_controls.csv", "per_galaxy_null_summary.csv", "global_control_battery_summary.csv", "figure2_source_data.csv", "extension_run_manifest.csv", "execution_report.md", "implementation_warnings.csv"]
PARTIAL_BRANCH, SPECTRAL_BRANCH = "partial_rank_134", "spectral_control_76"
SHUFFLE_SIGNED, SHUFFLE_ABSOLUTE = "shuffle_surrogate_partial_rank", "shuffle_surrogate_partial_rank_absolute"
SHIFT_SIGNED, SHIFT_ABSOLUTE = "circular_shift_control_partial_rank", "circular_shift_control_partial_rank_absolute"
PHASE_RESIDUAL, PHASE_TEMPLATE = "random_phase_surrogate_residual", "random_phase_surrogate_radial_template"
SMOOTH_TIERS = ["smooth_profile_exponential_reference", "smooth_profile_linear_reference", "smooth_profile_quadratic_reference"]

class MissingSourceError(RuntimeError): pass

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__); mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--test-mode", action="store_true"); mode.add_argument("--production", action="store_true"); return parser.parse_args()

def as_float(value):
    try: output = float(value)
    except (TypeError, ValueError): return math.nan
    return output if math.isfinite(output) else math.nan

def text_number(value):
    number = as_float(value); return "" if not math.isfinite(number) else f"{number:.17g}"

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""): digest.update(chunk)
    return digest.hexdigest()

def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore"); writer.writeheader()
        for row in rows: writer.writerow({column: row.get(column, "") for column in columns})

def add_warning(warnings, tier, galaxy, warning_type, message, severity, action_required):
    warnings.append({"warning_id": f"W{len(warnings)+1:04d}", "tier": tier, "galaxy": galaxy, "warning_type": warning_type, "message": message, "severity": severity, "action_required": action_required})

def stable_seed(galaxy, tier, iteration):
    material = f"{SEED_NAMESPACE}|{BASE_SEED}|{galaxy}|{tier}|{iteration:06d}".encode(); return int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=False)

def assert_no_builtin_hash_call():
    for node in ast.walk(ast.parse(SCRIPT_PATH.read_text(encoding="utf-8-sig"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "hash": raise AssertionError("Unstable built-in hash call found")

def rankdata_average(values):
    values = np.asarray(values, float); order = np.argsort(values, kind="mergesort"); ranks = np.empty(values.size); start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]: end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1) + 1; start = end
    return ranks

def residualize_rank(values, radius):
    values, radius = np.asarray(values, float), np.asarray(radius, float); mask = np.isfinite(values) & np.isfinite(radius)
    if mask.sum() < MIN_PARTIAL_POINTS: return None
    vr, rr = rankdata_average(values[mask]), rankdata_average(radius[mask]); matrix = np.column_stack([np.ones_like(rr), rr])
    try: coefficients, *_ = np.linalg.lstsq(matrix, vr, rcond=None)
    except Exception: return None
    residual = vr - matrix @ coefficients; return residual if np.all(np.isfinite(residual)) and np.std(residual) > 1e-12 else None

def partial_rank(x, y, radius):
    x, y, radius = np.asarray(x, float), np.asarray(y, float), np.asarray(radius, float); mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(radius)
    if mask.sum() < MIN_PARTIAL_POINTS: return math.nan
    xr, yr = residualize_rank(x[mask], radius[mask]), residualize_rank(y[mask], radius[mask])
    if xr is None or yr is None or xr.size != yr.size: return math.nan
    return float(np.corrcoef(xr, yr)[0, 1])

def normalized_radial_covariate(values):
    values = np.asarray(values, float); positive = values[np.isfinite(values) & (values > 0)]; scale = float(np.median(positive)) if positive.size else 1.0
    return np.nan_to_num(values / max(scale, 1e-30), nan=0, posinf=0, neginf=0)

def radial_template(values):
    logged = np.log10(np.maximum(np.asarray(values, float), 1e-12)); return np.clip(np.exp(-(logged / 0.50) ** 2), 0, 1)

def interpolate_log_radius(radii, values):
    radii, values = np.asarray(radii, float), np.asarray(values, float); mask = np.isfinite(radii) & np.isfinite(values) & (radii > 0)
    if mask.sum() < MIN_SPECTRAL_POINTS: raise ValueError("INSUFFICIENT_SPECTRAL_POINTS")
    radii, values = radii[mask], values[mask]; x = np.log10(radii / max(float(np.median(radii)), 1e-30)); order = np.argsort(x); x, values = x[order], values[order]
    unique, inverse = np.unique(x, return_inverse=True); means = np.array([np.mean(values[inverse == i]) for i in range(unique.size)])
    if unique.size < MIN_SPECTRAL_POINTS or np.ptp(unique) <= 1e-9: raise ValueError("INVALID_LOG_RADIUS_GRID")
    result = np.interp(np.linspace(unique.min(), unique.max(), GRID_LENGTH), unique, means)
    if not np.all(np.isfinite(result)): raise ValueError("NONFINITE_INTERPOLATION")
    return result

def normalized_power(values):
    values = np.asarray(values, float)
    if values.size != GRID_LENGTH or not np.all(np.isfinite(values)): raise ValueError("INVALID_SPECTRAL_VECTOR")
    positive = np.abs(np.fft.rfft(values - np.mean(values))) ** 2; positive = positive[1:]; total = float(np.sum(positive))
    if not math.isfinite(total) or total <= 1e-30: raise ValueError("ZERO_SPECTRAL_POWER")
    return positive / total

def spectral_concentration(values):
    power = normalized_power(values); return 1 - float(-np.sum(np.where(power > 0, power * np.log(power), 0)) / math.log(max(power.size, 2)))

def random_phase_profile(values, seed):
    centered = np.asarray(values, float) - np.mean(values); transform = np.fft.rfft(centered); amplitudes = np.abs(transform); rng = np.random.default_rng(seed); randomized = np.zeros_like(transform, complex)
    stop = transform.size - 1 if centered.size % 2 == 0 else transform.size
    if stop > 1: randomized[1:stop] = amplitudes[1:stop] * np.exp(1j * rng.uniform(0, 2 * math.pi, stop - 1))
    if centered.size % 2 == 0 and transform.size > 1: randomized[-1] = amplitudes[-1] * (1 if rng.random() >= .5 else -1)
    result = np.fft.irfft(randomized, n=centered.size)
    if not np.all(np.isfinite(result)): raise ValueError("NONFINITE_INVERSE_FFT")
    return result

def discover_source_root():
    for sibling in PAPER_ROOT.parent.iterdir():
        if sibling != PAPER_ROOT and sibling.is_dir() and (sibling / "data" / "sparc").is_dir() and (sibling / "vendor" / "h1_src" / "run_sparc_lite.py").is_file(): return sibling
    raise MissingSourceError("Read-only source repository was not located")

def discover_adapter(source_root):
    analysis_root = source_root / "comparative_analysis" / "comparative_validation"
    if not analysis_root.is_dir(): raise MissingSourceError("Read-only analysis context was not located")
    for parent in analysis_root.iterdir():
        if not parent.is_dir(): continue
        for child in parent.glob("*extended_shared*"):
            if not child.is_dir(): continue
            for candidate in child.glob("run_*extended_shared_*.py"):
                text = candidate.read_text(encoding="utf-8", errors="ignore")
                if all(marker in text for marker in ["def reconstruct_bundle", "def density_peak_from_sigma", "def density_peak_from_c"]): return candidate
    raise MissingSourceError("Read-only reconstruction adapter was not located")

def load_adapter(path):
    spec = importlib.util.spec_from_file_location("neutral_reconstruction_adapter", path)
    if spec is None or spec.loader is None: raise MissingSourceError("Read-only reconstruction adapter could not be loaded")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def load_frozen_parameters(source_root):
    path = source_root / "vendor" / "h1_src" / "run_sparc_lite.py"; required = {"name", "Rd_star", "Mstar", "hz_star", "Rd_gas", "Mgas", "hz_gas"}
    if not path.is_file(): raise MissingSourceError("Frozen parameter source was not located")
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8", errors="ignore"))):
        if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts: continue
        try: values = ast.literal_eval(node)
        except Exception: continue
        if isinstance(values, (list, tuple)) and values and all(isinstance(item, dict) and required.issubset(item) for item in values):
            fleet = {}
            for item in values:
                galaxy = {key: float(item[key]) if key != "name" else str(item[key]) for key in required}
                galaxy["Mgas_HI"] = galaxy["Mgas"]
                galaxy["Mgas"] = galaxy["Mgas_HI"] * 1.33
                fleet[galaxy["name"]] = galaxy
            return fleet
    raise MissingSourceError("Frozen parameter records were not found")

def load_gravity_constant(source_root):
    path = source_root / "vendor" / "h1_src" / "src" / "newtonian.py"
    if not path.is_file(): raise MissingSourceError("Frozen numerical constant source was not located")
    for node in ast.parse(path.read_text(encoding="utf-8", errors="ignore")).body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "G" for target in node.targets): return float(ast.literal_eval(node.value))
    raise MissingSourceError("Frozen numerical constant was not found")

def read_attrition():
    if not ATTRITION_FILE.is_file(): raise MissingSourceError("Sample attrition file was not located")
    with ATTRITION_FILE.open(newline="", encoding="utf-8-sig") as handle: rows = list(csv.DictReader(handle))
    partial = sorted(row["galaxy"] for row in rows if row["partial_branch_status"] == "COMPLETED"); spectral = sorted(row["galaxy"] for row in rows if row["spectral_branch_status"] == "VALID")
    if len(partial) != 134 or len(spectral) != 76 or not set(spectral).issubset(partial): raise MissingSourceError(f"Frozen sample membership mismatch: partial={len(partial)}, spectral={len(spectral)}")
    return partial, spectral

def make_row(gid, galaxy, branch, tier, kind, iteration, seed, shift, n_valid, statistic_name, value, valid, reason, notes):
    return {"galaxy_id": gid, "canonical_galaxy_name": galaxy, "sample_branch": branch, "control_tier": tier, "realization_type": kind, "iteration": iteration, "seed": seed, "shift_offset": shift, "n_valid_radii": n_valid, "statistic_name": statistic_name, "statistic_value": text_number(value), "valid_output": "TRUE" if valid else "FALSE", "invalid_reason": reason, "source_script": "src/run_m_surrogate_extension.py", "source_input_file": f"data/sparc/{galaxy}_rotmod.dat", "notes": notes}

def append_partial_pair(rows, gid, galaxy, signed_tier, absolute_tier, kind, iteration, seed, shift, n_valid, value, notes):
    valid, reason = math.isfinite(value), "" if math.isfinite(value) else "NONFINITE_PARTIAL_RANK"
    rows.append(make_row(gid, galaxy, PARTIAL_BRANCH, signed_tier, kind, iteration, seed, shift, n_valid, "partial_rank", value, valid, reason, notes))
    absolute_notes = notes + "; Derived absolute statistic shares the seed of the signed surrogate realization."
    rows.append(make_row(gid, galaxy, PARTIAL_BRANCH, absolute_tier, kind, iteration, seed, shift, n_valid, "absolute_partial_rank", abs(value) if valid else math.nan, valid, reason, absolute_notes))
def reconstruct_selected(selected, parameters, constant, adapter, warnings):
    bundles = {}
    for galaxy in selected:
        try:
            bundle = adapter.reconstruct_bundle(galaxy, parameters[galaxy], constant); required = {"r_obs", "r_frac", "residual_abs", "sigma_b"}
            if not required.issubset(bundle): raise KeyError
            bundles[galaxy] = {key: np.asarray(bundle[key], float).copy() for key in required}
        except Exception:
            add_warning(warnings, "reconstruction", galaxy, "RECONSTRUCTION_FAILED", "Read-only reconstruction did not return the required vectors", "ERROR", "Inspect source interface before production")
    return bundles

def execute_partial(selected, bundles, ids, random_m, test_mode, rows, observed, seeds, warnings):
    for galaxy in selected:
        gid = ids[galaxy]
        if galaxy not in bundles:
            add_warning(warnings, "partial_tiers", galaxy, "MISSING_RECONSTRUCTION", "Partial-tier rows unavailable", "ERROR", "Resolve reconstruction"); continue
        bundle = bundles[galaxy]; radius, residual = bundle["r_frac"], bundle["residual_abs"]; covariate = normalized_radial_covariate(bundle["sigma_b"]); n_valid = radius.size
        value = partial_rank(radial_template(covariate), residual, radius)
        for tier, observed_value in [(SHUFFLE_SIGNED, value), (SHUFFLE_ABSOLUTE, abs(value)), (SHIFT_SIGNED, value), (SHIFT_ABSOLUTE, abs(value))]: observed[(gid, tier)] = observed_value
        for iteration in range(1, random_m + 1):
            seed = stable_seed(galaxy, SHUFFLE_SIGNED, iteration); key = (galaxy, SHUFFLE_SIGNED, iteration, seed)
            if key in seeds: raise AssertionError("Duplicate deterministic seed tuple")
            seeds.add(key); value = partial_rank(radial_template(np.random.default_rng(seed).permutation(covariate.copy())), residual, radius)
            append_partial_pair(rows, gid, galaxy, SHUFFLE_SIGNED, SHUFFLE_ABSOLUTE, "shuffle_surrogate", iteration, seed, "", n_valid, value, "Frozen mask; only normalized radial covariate permuted")
        offsets = list(range(1, n_valid)); offsets = offsets[:TEST_SHIFT_LIMIT] if test_mode else offsets
        if n_valid < MIN_PARTIAL_POINTS: add_warning(warnings, "circular_shift_control", galaxy, "INSUFFICIENT_SHIFTS", "Fewer than five valid radii", "ERROR", "Retain without duplicating shifts")
        for iteration, offset in enumerate(offsets, 1):
            value = partial_rank(radial_template(np.roll(covariate, offset)), residual, radius)
            append_partial_pair(rows, gid, galaxy, SHIFT_SIGNED, SHIFT_ABSOLUTE, "test_circular_shift_subset" if test_mode else "exhaustive_circular_shift", iteration, "", offset, n_valid, value, f"Used {len(offsets)} of {n_valid-1} nontrivial offsets")

def execute_spectral(selected, bundles, ids, random_m, rows, observed, seeds, warnings):
    x = np.linspace(0, 1, GRID_LENGTH); smooth = {SMOOTH_TIERS[0]: np.exp(-x), SMOOTH_TIERS[1]: np.clip(1-x, 0, None), SMOOTH_TIERS[2]: np.clip(1-x, 0, None) ** 2}
    for galaxy in selected:
        gid = ids[galaxy]
        if galaxy not in bundles:
            add_warning(warnings, "spectral_tiers", galaxy, "MISSING_RECONSTRUCTION", "Spectral-tier rows unavailable", "ERROR", "Resolve reconstruction"); continue
        bundle, n_valid = bundles[galaxy], bundles[galaxy]["r_obs"].size
        try:
            profiles = {PHASE_RESIDUAL: interpolate_log_radius(bundle["r_obs"], bundle["residual_abs"]), PHASE_TEMPLATE: interpolate_log_radius(bundle["r_obs"], radial_template(normalized_radial_covariate(bundle["sigma_b"])))}
            for tier, profile in profiles.items():
                observed[(gid, tier)] = spectral_concentration(profile); values = []
                for iteration in range(1, random_m + 1):
                    seed = stable_seed(galaxy, tier, iteration); key = (galaxy, tier, iteration, seed)
                    if key in seeds: raise AssertionError("Duplicate deterministic seed tuple")
                    seeds.add(key)
                    try: value, valid, reason = spectral_concentration(random_phase_profile(profile, seed)), True, ""
                    except Exception: value, valid, reason = math.nan, False, "SPECTRAL_SURROGATE_FAILED"
                    if valid: values.append(value)
                    rows.append(make_row(gid, galaxy, SPECTRAL_BRANCH, tier, "random_phase_surrogate", iteration, seed, "", n_valid, "spectral_concentration", value, valid, reason, "Amplitude spectrum preserved on fixed 64-point grid"))
                if values and np.ptp(values) <= 1e-12: add_warning(warnings, tier, galaxy, "DEGENERATE_PHASE_BLIND_STATISTIC", "Spectral concentration unchanged across amplitude-preserving surrogates", "INFO", "Retain by-construction caveat during QC")
            for tier, profile in smooth.items():
                value = spectral_concentration(profile); observed[(gid, tier)] = math.nan
                rows.append(make_row(gid, galaxy, SPECTRAL_BRANCH, tier, "fixed_reference", "", "", "", n_valid, "spectral_concentration", value, math.isfinite(value), "", "Fixed branch-specific reference; not stochastic"))
        except Exception:
            add_warning(warnings, "spectral_tiers", galaxy, "SPECTRAL_PREPARATION_FAILED", "Fixed-grid profiles could not be prepared", "ERROR", "Inspect spectral validity interface")

def reconcile_execution(test_mode, partial_selected, spectral_selected, bundles, rows, random_m, warnings):
    by_galaxy_tier = defaultdict(list)
    for row in rows: by_galaxy_tier[(row["canonical_galaxy_name"], row["control_tier"])].append(row)
    expected = {}; selected_by_tier = defaultdict(set); missing_tiers = []
    partial_tiers = [SHUFFLE_SIGNED, SHUFFLE_ABSOLUTE, SHIFT_SIGNED, SHIFT_ABSOLUTE]
    spectral_tiers = [PHASE_RESIDUAL, PHASE_TEMPLATE] + SMOOTH_TIERS
    for galaxy in partial_selected:
        for tier in partial_tiers: selected_by_tier[tier].add(galaxy)
        if galaxy not in bundles:
            missing_tiers.extend(f"{galaxy}:{tier}" for tier in partial_tiers); continue
        n_valid = int(bundles[galaxy]["r_frac"].size); shift_count = min(TEST_SHIFT_LIMIT, max(0, n_valid - 1)) if test_mode else max(0, n_valid - 1)
        expected[(galaxy, SHUFFLE_SIGNED)] = random_m; expected[(galaxy, SHUFFLE_ABSOLUTE)] = random_m
        expected[(galaxy, SHIFT_SIGNED)] = shift_count; expected[(galaxy, SHIFT_ABSOLUTE)] = shift_count
    for galaxy in spectral_selected:
        for tier in spectral_tiers: selected_by_tier[tier].add(galaxy)
        expected[(galaxy, PHASE_RESIDUAL)] = random_m; expected[(galaxy, PHASE_TEMPLATE)] = random_m
        for tier in SMOOTH_TIERS: expected[(galaxy, tier)] = 1
    for key, requested in expected.items():
        if len(by_galaxy_tier.get(key, [])) != requested: missing_tiers.append(f"{key[0]}:{key[1]}")
    selected = sorted(set(partial_selected) | set(spectral_selected)); reconstructed = sorted(set(bundles)); emitted = sorted({row["canonical_galaxy_name"] for row in rows}); missing_galaxies = sorted(set(selected) - set(emitted))
    invalid_only = sorted(galaxy for galaxy in emitted if not any(row["valid_output"] == "TRUE" for row in rows if row["canonical_galaxy_name"] == galaxy))
    tier_accounting = {}
    all_tiers = [SHUFFLE_SIGNED, SHUFFLE_ABSOLUTE, SHIFT_SIGNED, SHIFT_ABSOLUTE, PHASE_RESIDUAL, PHASE_TEMPLATE] + SMOOTH_TIERS
    for tier in all_tiers:
        tier_rows = [row for row in rows if row["control_tier"] == tier]; selected_tier = sorted(selected_by_tier[tier]); emitted_tier = sorted({row["canonical_galaxy_name"] for row in tier_rows})
        requested = sum(count for (galaxy, expected_tier), count in expected.items() if expected_tier == tier)
        strategy = "Strategy: Fixed reference, not stochastic" if tier in SMOOTH_TIERS else ("Strategy: Test-mode limited subset" if tier in {SHIFT_SIGNED, SHIFT_ABSOLUTE} and test_mode else ("Strategy: Exhaustive N-1 circular shifts" if tier in {SHIFT_SIGNED, SHIFT_ABSOLUTE} else "Strategy: Random surrogate ensemble"))
        tier_accounting[tier] = {"sample_branch": PARTIAL_BRANCH if tier in partial_tiers else SPECTRAL_BRANCH, "M_requested": int(requested), "M_effective": int(len(tier_rows)), "selected_galaxies": selected_tier, "emitted_galaxies": emitted_tier, "total_emitted_rows": len(tier_rows), "valid_rows": sum(row["valid_output"] == "TRUE" for row in tier_rows), "invalid_rows": sum(row["valid_output"] == "FALSE" for row in tier_rows), "status": "COMPLETE" if requested == len(tier_rows) and len(emitted_tier) == len(selected_tier) else "INCOMPLETE", "strategy": strategy}
    error_warnings = [row for row in warnings if row["severity"] == "ERROR"]
    production_blocked = bool(not test_mode and (missing_galaxies or missing_tiers or error_warnings))
    if production_blocked:
        add_warning(warnings, "all_control_tiers", "", "RECONCILIATION_FAILURE", f"Missing galaxies={missing_galaxies}; missing tiers={sorted(set(missing_tiers))}", "ERROR", "Resolve missing rows before production completion")
    return {"mode": "test" if test_mode else "production", "selected_galaxies": selected, "reconstructed_galaxies": reconstructed, "emitted_galaxies": emitted, "invalid_only_galaxies": invalid_only, "missing_galaxies": missing_galaxies, "missing_tiers": sorted(set(missing_tiers)), "requested_random_realizations": sum(v for (g, tier), v in expected.items() if tier in {SHUFFLE_SIGNED, SHUFFLE_ABSOLUTE, PHASE_RESIDUAL, PHASE_TEMPLATE}), "emitted_rows": len(rows), "valid_rows": sum(row["valid_output"] == "TRUE" for row in rows), "invalid_rows": sum(row["valid_output"] == "FALSE" for row in rows), "no_galaxies_silently_removed": not missing_galaxies, "no_invalid_realizations_silently_removed": not missing_tiers, "production_blocked": production_blocked, "tier_accounting": tier_accounting}
def quantile(values, probability): return float(np.quantile(values, probability, method=QUANTILE_METHOD))

def empirical_midrank(values, observed_value, tol=1e-12):
    delta = values - observed_value
    lt_count = np.count_nonzero(delta < -tol)
    eq_count = np.count_nonzero(np.abs(delta) <= tol)
    gt_count = np.count_nonzero(delta > tol)
    if lt_count + eq_count + gt_count != values.size: raise AssertionError("Empirical rank counts do not partition controls")
    return min(1.0, max(0.0, (lt_count + .5 * eq_count) / values.size))

def empirical_two_sided_abs(values, observed_value, tol=1e-12):
    value = (1 + np.count_nonzero(np.abs(values) >= abs(observed_value) - tol)) / (values.size + 1)
    return min(1.0, max(0.0, value))

def summarize_per_galaxy(rows, observed):
    grouped = defaultdict(list)
    for row in rows: grouped[(row["galaxy_id"], row["sample_branch"], row["control_tier"])].append(row)
    summaries = []
    for (gid, branch, tier), group in sorted(grouped.items()):
        values = np.asarray([float(row["statistic_value"]) for row in group if row["valid_output"] == "TRUE" and row["statistic_value"]], float); observed_value = observed.get((gid, tier), math.nan)
        fixed, shift, spectral = all(row["realization_type"] == "fixed_reference" for row in group), tier in {SHIFT_SIGNED, SHIFT_ABSOLUTE}, tier in {PHASE_RESIDUAL, PHASE_TEMPLATE}
        percentile = empirical_p = math.nan; status = "NO_VALID_REALIZATIONS"; summary_notes = "Per-galaxy summary; not a pooled p-value"
        if fixed:
            status, summary_notes = "FIXED_REFERENCE_NOT_NULL", "Fixed reference: percentile and p-value empty"
        elif shift:
            n_valid = int(group[0]["n_valid_radii"]); offsets = sorted(int(row["shift_offset"]) for row in group if row["shift_offset"] != "")
            exhaustive = n_valid >= MIN_PARTIAL_POINTS and offsets == list(range(1, n_valid))
            if n_valid < MIN_PARTIAL_POINTS:
                status, summary_notes = "INSUFFICIENT_SHIFTS", "Insufficient valid radii; no exact circular-shift p-value."
            elif not exhaustive:
                status, summary_notes = "TEST_SUBSET_NOT_EXACT", "Test-mode limited subset; not an exact circular-shift distribution."
            elif values.size:
                percentile = empirical_midrank(values, observed_value)
                empirical_p = empirical_two_sided_abs(values, observed_value); status = "FINITE_EXACT_SHIFT"
        elif values.size:
            percentile = empirical_midrank(values, observed_value)
            if spectral: empirical_p, status = min(1.0, max(0.0, 2 * min(percentile, 1-percentile))), "DEGENERATE_PHASE_BLIND_STATISTIC" if np.ptp(values) <= 1e-12 else "FINITE"
            else: empirical_p, status = empirical_two_sided_abs(values, observed_value), "FINITE_RANDOM_ENSEMBLE"
        getq = lambda p: quantile(values, p) if values.size else math.nan
        summaries.append({"galaxy_id": gid, "sample_branch": branch, "control_tier": tier, "n_realizations": len(group), "n_valid_realizations": values.size, "observed_statistic": text_number(observed_value), "control_median": text_number(np.median(values) if values.size else math.nan), "control_mean": text_number(np.mean(values) if values.size else math.nan), "control_std": text_number(np.std(values) if values.size else math.nan), "control_p05": text_number(getq(.05)), "control_p16": text_number(getq(.16)), "control_p84": text_number(getq(.84)), "control_p95": text_number(getq(.95)), "empirical_percentile_observed": text_number(percentile), "empirical_p_two_sided": text_number(empirical_p), "finite_status": status, "notes": summary_notes})
    return summaries
def summarize_global(realizations, summaries):
    grouped = defaultdict(list)
    for row in summaries: grouped[(row["sample_branch"], row["control_tier"])].append(row)
    output = []
    for (branch, tier), group in sorted(grouped.items()):
        finite = lambda field: np.asarray([as_float(row[field]) for row in group if math.isfinite(as_float(row[field]))])
        obs, medians, percentiles = finite("observed_statistic"), finite("control_median"), finite("empirical_percentile_observed")
        pooled = np.asarray([as_float(row["statistic_value"]) for row in realizations if row["sample_branch"] == branch and row["control_tier"] == tier and row["valid_output"] == "TRUE"])
        output.append({"sample_branch": branch, "control_tier": tier, "n_galaxies": len(group), "total_realizations": sum(int(row["n_realizations"]) for row in group), "observed_median": text_number(np.median(obs) if obs.size else math.nan), "control_median_of_medians": text_number(np.median(medians) if medians.size else math.nan), "control_global_p05": text_number(quantile(pooled, .05) if pooled.size else math.nan), "control_global_p95": text_number(quantile(pooled, .95) if pooled.size else math.nan), "median_empirical_percentile": text_number(np.median(percentiles) if percentiles.size else math.nan), "notes": "Descriptive across-galaxy summary only; not a pooled empirical test"})
    return output

def figure_rows(summaries):
    output = []
    for row in summaries:
        panel = "partial_rank_controls" if row["sample_branch"] == PARTIAL_BRANCH else "spectral_controls"
        for value_type, field in [("observed", "observed_statistic"), ("control_median", "control_median"), ("control_p05", "control_p05"), ("control_p95", "control_p95")]:
            if row[field]: output.append({"panel": panel, "sample_branch": row["sample_branch"], "control_tier": row["control_tier"], "value_type": value_type, "statistic_value": row[field], "galaxy_id": row["galaxy_id"], "realization": "per_galaxy_summary", "notes": "Lightweight plot-ready branch-labeled summary"})
    return output

def git_version(source_root):
    try: return subprocess.run(["git", "rev-parse", "HEAD"], cwd=source_root, capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    except Exception: return ""

def write_report(test_mode, status, elapsed, partial, spectral, bundles, rows, warnings, reconciliation):
    mode = "test mode (N=2, random M=3)" if test_mode else "production mode"
    lines = ["# M-Surrogate Extension Execution Report", "", "## Executive summary", "", f"- Execution mode: {mode}.", f"- Execution status: {status}.", "- This is a statistical-hygiene implementation run.", "- Separate QC is required before manuscript terminology changes.", "", "## Input files used", ""]
    lines += [f"- `{path.relative_to(PAPER_ROOT)}`" for path in CONTRACT_FILES if path.exists()]
    lines += ["", "## Source scripts/data read", "", "- Read-only reconstruction adapter located dynamically.", "- Frozen parameters, numerical constant, and rotation-curve files read without modification.", "", "## Reconciliation accounting", "", f"- Selected galaxies: {len(reconciliation['selected_galaxies'])}.", f"- Reconstructed galaxies: {len(reconciliation['reconstructed_galaxies'])}.", f"- Galaxies with emitted rows: {len(reconciliation['emitted_galaxies'])}.", f"- Invalid-only galaxies: {reconciliation['invalid_only_galaxies']}.", f"- Missing galaxies: {reconciliation['missing_galaxies']}.", f"- Missing tiers: {reconciliation['missing_tiers']}.", f"- Emitted rows: {reconciliation['emitted_rows']}; valid rows: {reconciliation['valid_rows']}; invalid rows: {reconciliation['invalid_rows']}.", "", "## Tier accounting", ""]
    for tier, accounting in reconciliation["tier_accounting"].items(): lines.append(f"- `{tier}`: requested={accounting['M_requested']}, emitted={accounting['M_effective']}, valid={accounting['valid_rows']}, invalid={accounting['invalid_rows']}, status={accounting['status']}; {accounting['strategy']}.")
    lines += ["", "## Circular-shift status", "", f"- {'Test-mode limited subset; not an exact circular-shift distribution.' if test_mode else 'Production requests exhaustive nontrivial offsets and checks completeness before completion.'}", "", "## Smooth-reference status", "", "- Exponential, linear, and quadratic references are fixed, not stochastic.", "", "## Runtime and storage estimate", "", f"- Measured runtime: {elapsed:.3f} seconds.", "- Compressed CSV or Parquet may be useful; final figure source should remain lightweight.", "", "## Output files created", ""]
    lines += [f"- `{name}`" for name in OUTPUT_NAMES]
    remaining_requirement = "Test-mode outputs require a separate test-mode QC before production execution." if test_mode else "Production outputs have been generated. A separate production-output QC is required before manuscript use or terminology upgrade."
    lines += ["", "## Language lock", "", "- Manuscript edited: NO.", "- Physical interpretation emitted: NO.", "- Unsupported result statement emitted: NO.", "- Production terminology upgrade authorized: NO, QC_REQUIRED.", f"- Production execution: {'NO' if test_mode else 'YES, QC_REQUIRED'}.", "- Production M=1000 language requires separate production QC.", "", "## Remaining requirement", "", f"- {remaining_requirement}"]
    if reconciliation["production_blocked"]: lines += ["", "## Reconciliation failure", "", "- Production completion was blocked and the process must exit nonzero.", f"- Missing galaxies: {reconciliation['missing_galaxies']}.", f"- Missing tiers: {reconciliation['missing_tiers']}."]
    (OUTPUT_DIR / "execution_report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

def make_manifest(run_id, timestamp, source_root, status, rows, reconciliation):
    inputs = {str(path.relative_to(PAPER_ROOT)): sha256_file(path) for path in CONTRACT_FILES if path.exists()}; outputs = {name: sha256_file(OUTPUT_DIR/name) for name in OUTPUT_NAMES if name != "extension_run_manifest.csv" and (OUTPUT_DIR/name).exists()}
    shared = {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(), "quantile_method": QUANTILE_METHOD, "input_checksums": inputs, "output_checksums": outputs, "no_galaxies_silently_removed": reconciliation["no_galaxies_silently_removed"], "no_invalid_realizations_silently_removed": reconciliation["no_invalid_realizations_silently_removed"], "selected_galaxies": reconciliation["selected_galaxies"], "reconstructed_galaxies": reconciliation["reconstructed_galaxies"], "emitted_galaxies": reconciliation["emitted_galaxies"], "invalid_only_galaxies": reconciliation["invalid_only_galaxies"], "missing_galaxies": reconciliation["missing_galaxies"], "missing_tiers": reconciliation["missing_tiers"], "manifest_self_checksum": "not_applicable", "deterministic_rerun_evidence": "PENDING_MANUAL"}
    manifest = []
    for tier, accounting in reconciliation["tier_accounting"].items():
        notes = dict(shared); notes.update({"sample_branch": accounting["sample_branch"], "selected_galaxies_for_tier": accounting["selected_galaxies"], "emitted_galaxies_for_tier": accounting["emitted_galaxies"], "total_emitted_rows": accounting["total_emitted_rows"], "valid_rows": accounting["valid_rows"], "invalid_rows": accounting["invalid_rows"], "strategy": accounting["strategy"]})
        manifest.append({"run_id": run_id, "timestamp": timestamp, "base_seed": BASE_SEED, "code_version_or_git_hash_if_available": git_version(source_root), "input_file": ";".join(str(path.relative_to(PAPER_ROOT)) for path in CONTRACT_FILES), "output_file": "per_realization_controls.csv", "tier": tier, "M_requested": int(accounting["M_requested"]), "M_effective": int(accounting["M_effective"]), "status": status if accounting["status"] == "COMPLETE" else "INCOMPLETE", "notes": json.dumps(notes, sort_keys=True)})
    return manifest
def verify_outputs(rows, seeds, summaries, reconciliation, test_mode):
    if RANDOM_M_REQUESTED != 1000 or len(seeds) != len(set(seeds)): raise AssertionError("Production M or seed uniqueness check failed")
    shifts = defaultdict(list)
    for row in rows:
        if row["control_tier"] in {SHIFT_SIGNED, SHIFT_ABSOLUTE}:
            offset = int(row["shift_offset"])
            if offset == 0: raise AssertionError("Identity shift found")
            shifts[(row["galaxy_id"], row["control_tier"])].append(offset)
        if row["realization_type"] == "fixed_reference" and (row["seed"] or row["iteration"]): raise AssertionError("Fixed reference has stochastic metadata")
    if any(len(x) != len(set(x)) for x in shifts.values()): raise AssertionError("Duplicate shift found")
    for summary in summaries:
        if summary["control_tier"] in {SHIFT_SIGNED, SHIFT_ABSOLUTE}:
            if test_mode and (summary["finite_status"] != "TEST_SUBSET_NOT_EXACT" or summary["empirical_p_two_sided"]): raise AssertionError("Test shift subset incorrectly presented as exhaustive")
            if not test_mode and summary["finite_status"] not in {"FINITE_EXACT_SHIFT", "INSUFFICIENT_SHIFTS"}: raise AssertionError("Production shift status is not guarded")
    expected = {"per_realization_controls.csv": REALIZATION_COLUMNS, "per_galaxy_null_summary.csv": GALAXY_SUMMARY_COLUMNS, "global_control_battery_summary.csv": GLOBAL_SUMMARY_COLUMNS, "figure2_source_data.csv": FIGURE_COLUMNS, "extension_run_manifest.csv": MANIFEST_COLUMNS, "implementation_warnings.csv": WARNING_COLUMNS}
    for name, columns in expected.items():
        with (OUTPUT_DIR/name).open(newline="", encoding="utf-8-sig") as handle:
            if next(csv.reader(handle)) != columns: raise AssertionError(f"Schema mismatch: {name}")
    with (OUTPUT_DIR/"extension_run_manifest.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle): int(row["M_requested"]); int(row["M_effective"])

def print_status(completed, status, test_mode):
    print(f"* M-surrogate implementation script created? {'YES' if SCRIPT_PATH.exists() else 'NO'}")
    print(f"* Script path = {SCRIPT_PATH}"); print("* Execution attempted? YES"); print(f"* Execution completed? {'YES' if completed else 'NO'}"); print(f"* Execution status = {status}"); print(f"* Output directory created? {'YES' if OUTPUT_DIR.exists() else 'NO'}")
    for name in OUTPUT_NAMES: print(f"* {name} created? {'YES' if (OUTPUT_DIR/name).exists() else 'NO'}")
    print(f"* Production run executed? {'NO' if test_mode else 'YES'}")
    print(f"* Circular shifts exhaustive? {'PARTIAL' if test_mode else 'YES'}")
    print("* Smooth controls fixed references only? YES")
    print("* Production terminology upgrade authorized? NO, QC_REQUIRED")
    print("* Manuscript edited? NO"); print("* Physical interpretation emitted? NO"); print("* Unsupported result statement emitted? NO")
    print(f"* Ready for separate QC? {'YES' if completed else 'NO'}")
    print("* Recommended next task = M_SURROGATE_TESTMODE_QC_RERUN" if test_mode else "* Recommended next task = PRODUCTION_OUTPUT_QC")
def main():
    args, start = parse_args(), time.perf_counter(); test_mode = bool(args.test_mode); timestamp = datetime.now(timezone.utc).isoformat(); run_id = datetime.now(timezone.utc).strftime("mse-%Y%m%dT%H%M%SZ-test" if test_mode else "mse-%Y%m%dT%H%M%SZ-production")
    warnings, rows, seeds, observed = [], [], set(), {}; source_root = None; partial_selected, spectral_selected, bundles = [], [], {}; random_m = TEST_RANDOM_M if test_mode else RANDOM_M_REQUESTED; OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        assert_no_builtin_hash_call(); missing = [path.name for path in CONTRACT_FILES if not path.is_file()]
        if missing: raise MissingSourceError("Missing implementation contracts: " + ", ".join(missing))
        partial_all, spectral_all = read_attrition(); source_root = discover_source_root(); adapter = load_adapter(discover_adapter(source_root)); parameters, constant = load_frozen_parameters(source_root), load_gravity_constant(source_root); ids = {name: f"G{index:04d}" for index, name in enumerate(partial_all, 1)}
        if test_mode:
            partial_selected = spectral_all[:TEST_GALAXIES]; spectral_selected = list(partial_selected); add_warning(warnings, "all_control_tiers", "", "TEST_MODE_LIMIT", "Execution intentionally limited to two galaxies and three random realizations", "INFO", "Run production only after test-mode QC")
        else: partial_selected, spectral_selected = partial_all, spectral_all
        bundles = reconstruct_selected(sorted(set(partial_selected)|set(spectral_selected)), parameters, constant, adapter, warnings)
        execute_partial(partial_selected, bundles, ids, random_m, test_mode, rows, observed, seeds, warnings); execute_spectral(spectral_selected, bundles, ids, random_m, rows, observed, seeds, warnings)
        reconciliation = reconcile_execution(test_mode, partial_selected, spectral_selected, bundles, rows, random_m, warnings); status = "TEST_MODE_COMPLETED_QC_PENDING" if test_mode else ("BLOCKED_RECONCILIATION_FAILURE" if reconciliation["production_blocked"] else "PRODUCTION_COMPLETED_QC_PENDING")
        write_csv(OUTPUT_DIR/"per_realization_controls.csv", REALIZATION_COLUMNS, rows); summaries = summarize_per_galaxy(rows, observed); write_csv(OUTPUT_DIR/"per_galaxy_null_summary.csv", GALAXY_SUMMARY_COLUMNS, summaries); write_csv(OUTPUT_DIR/"global_control_battery_summary.csv", GLOBAL_SUMMARY_COLUMNS, summarize_global(rows, summaries)); write_csv(OUTPUT_DIR/"figure2_source_data.csv", FIGURE_COLUMNS, figure_rows(summaries)); write_csv(OUTPUT_DIR/"implementation_warnings.csv", WARNING_COLUMNS, warnings); write_report(test_mode, status, time.perf_counter()-start, partial_selected, spectral_selected, bundles, rows, warnings, reconciliation); write_csv(OUTPUT_DIR/"extension_run_manifest.csv", MANIFEST_COLUMNS, make_manifest(run_id, timestamp, source_root, status, rows, reconciliation)); verify_outputs(rows, seeds, summaries, reconciliation, test_mode)
        if reconciliation["production_blocked"]:
            print_status(False, status, test_mode); return 1
        print_status(True, status, test_mode); return 0
    except MissingSourceError as exc:
        add_warning(warnings, "all_control_tiers", "", "BLOCKED_MISSING_SOURCE", str(exc), "ERROR", "Resolve missing frozen source"); reconciliation = reconcile_execution(test_mode, partial_selected, spectral_selected, bundles, rows, random_m, warnings); status = "BLOCKED_MISSING_SOURCE"
        for name, columns in [("per_realization_controls.csv", REALIZATION_COLUMNS), ("per_galaxy_null_summary.csv", GALAXY_SUMMARY_COLUMNS), ("global_control_battery_summary.csv", GLOBAL_SUMMARY_COLUMNS), ("figure2_source_data.csv", FIGURE_COLUMNS)]: write_csv(OUTPUT_DIR/name, columns, [])
        write_csv(OUTPUT_DIR/"implementation_warnings.csv", WARNING_COLUMNS, warnings); write_report(test_mode, status, time.perf_counter()-start, partial_selected, spectral_selected, bundles, rows, warnings, reconciliation); write_csv(OUTPUT_DIR/"extension_run_manifest.csv", MANIFEST_COLUMNS, make_manifest(run_id, timestamp, source_root, status, rows, reconciliation)); print_status(False, status, test_mode); return 1
    except Exception as exc:
        status = "BLOCKED_IMPLEMENTATION_ERROR"; add_warning(warnings, "all_control_tiers", "", "IMPLEMENTATION_ERROR", f"{type(exc).__name__}: {exc}", "ERROR", "Correct implementation before execution"); write_csv(OUTPUT_DIR/"implementation_warnings.csv", WARNING_COLUMNS, warnings); print_status(False, status, test_mode); return 1

if __name__ == "__main__": raise SystemExit(main())
