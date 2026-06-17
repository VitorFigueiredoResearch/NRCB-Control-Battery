#!/usr/bin/env python3
# Copyright (C) 2026 Vitor M. F. Figueiredo
# SPDX-License-Identifier: GPL-3.0-only
#
# This file is part of the Nisa Radial Control Battery (NRCB).
"""SPARC bootstrap preflight validator for NRCB reproduction modes.

This utility checks local availability and shape of SPARC/source inputs. It does
not download data, redistribute data, rerun production, or regenerate figures.
"""
from __future__ import annotations

import argparse
import ast
import csv
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

MODES = (
    "manuscript-reproduction",
    "figure-reproduction",
    "parameter-extraction",
    "test-mode",
    "full-production",
)
CHECK_COLUMNS = [
    "check_id",
    "mode",
    "check_name",
    "severity",
    "status",
    "observed",
    "expected",
    "path_or_pattern",
    "remediation",
    "mode_blocked",
    "mode_still_available",
    "notes",
]
INVENTORY_COLUMNS = [
    "input_id",
    "mode",
    "path_or_pattern",
    "exists",
    "readable",
    "size_bytes",
    "expected_count",
    "observed_count",
    "status",
    "classification",
    "notes",
]
CONTRACT_FILES = [
    "M_SURROGATE_EXTENSION_DESIGN.md",
    "EVIDENCE_LOCK.md",
    "SAMPLE_ATTRITION_134_TO_76.csv",
    "HEADLINE_VALUE_RECOMPUTE.csv",
    "REALIZATION_CENSUS.csv",
]
EXPECTED_PARTIAL = 134
EXPECTED_SPECTRAL = 76
EXPECTED_VENDOR_RECORDS = 175
EXPECTED_TABLE1_RECORDS = 175
MIN_ROTMOD_ROWS = 4
TEST_GALAXIES = 2


@dataclass
class CheckRecord:
    check_id: str
    mode: str
    check_name: str
    severity: str
    status: str
    observed: str
    expected: str
    path_or_pattern: str
    remediation: str
    mode_blocked: str
    mode_still_available: str
    notes: str


@dataclass
class InventoryRecord:
    input_id: str
    mode: str
    path_or_pattern: str
    exists: str
    readable: str
    size_bytes: str
    expected_count: str
    observed_count: str
    status: str
    classification: str
    notes: str


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--sparc-extractor-root", type=Path)
    parser.add_argument("--release-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true", help="Write JSON output when --output-dir is provided.")
    parser.add_argument("--strict", action="store_true", help="Enable optional strict checks such as isolated LaTeX compile.")
    parser.add_argument("--allow-one-galaxy-dry-run", action="store_true")
    return parser.parse_args(argv)


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value)
    return str(value)


def try_float(value: Any) -> Optional[float]:
    try:
        output = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return output if math.isfinite(output) else None


def canonical_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name).upper()


def strip_latex_comment(line: str) -> str:
    escaped = False
    out = []
    for char in line:
        if char == "%" and not escaped:
            break
        out.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    return "".join(out)


def file_state(path: Path) -> Tuple[str, str, str]:
    try:
        exists = path.exists()
    except OSError:
        return "NO", "NO", ""
    if not exists:
        return "NO", "NO", ""
    try:
        size = path.stat().st_size
    except OSError:
        return "YES", "NO", ""
    readable = "YES"
    if path.is_file():
        try:
            with path.open("rb") as handle:
                handle.read(1)
        except OSError:
            readable = "NO"
    return "YES", readable, str(size)


def count_csv_rows(path: Path) -> Optional[int]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            try:
                next(reader)
            except StopIteration:
                return 0
            return sum(1 for _ in reader)
    except OSError:
        return None


def parse_table1_rows(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    rows: List[Dict[str, Any]] = []
    malformed: List[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if not line.strip() or line.startswith("#") or line.lower().startswith("title"):
            continue
        parts = line.split()
        if len(parts) < 15:
            continue
        name = parts[0]
        if not re.search(r"[A-Za-z]", name) or len(name) < 2:
            continue
        l36 = try_float(parts[7])
        rd = try_float(parts[11])
        mhi = try_float(parts[13])
        if l36 is None and rd is None and mhi is None:
            malformed.append(name)
        rows.append({"name": name, "key": canonical_name(name), "L36": l36, "Rd": rd, "MHI": mhi})
    return rows, malformed


def parse_frozen_parameters(vendor_run: Path) -> Dict[str, Dict[str, Any]]:
    required = {"name", "Rd_star", "Mstar", "hz_star", "Rd_gas", "Mgas", "hz_gas"}
    tree = ast.parse(vendor_run.read_text(encoding="utf-8", errors="ignore"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)) or not getattr(node, "elts", None):
            continue
        try:
            values = ast.literal_eval(node)
        except Exception:
            continue
        if isinstance(values, (list, tuple)) and values and all(isinstance(item, dict) and required.issubset(item) for item in values):
            return {str(item["name"]): dict(item) for item in values}
    return {}


def parse_gravity_constant(path: Path) -> Optional[float]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "G" for target in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except Exception:
                return None
            return float(value)
    return None


def parse_attrition(path: Path) -> Tuple[List[str], List[str], int, List[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    partial = sorted(row["galaxy"] for row in rows if row.get("partial_branch_status") == "COMPLETED")
    spectral = sorted(row["galaxy"] for row in rows if row.get("spectral_branch_status") == "VALID")
    duplicates = sorted({row["galaxy"] for row in rows if sum(1 for r in rows if r.get("galaxy") == row.get("galaxy")) > 1})
    return partial, spectral, len(rows), duplicates


def rotmod_quality(path: Path) -> Tuple[int, str]:
    good_rows = 0
    reason = ""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.split()
                if len(parts) < 2:
                    continue
                radius = try_float(parts[0])
                velocity = try_float(parts[1])
                if radius is not None and velocity is not None and radius > 0 and velocity > 0:
                    good_rows += 1
    except OSError as exc:
        return 0, f"unreadable: {exc}"
    if good_rows < MIN_ROTMOD_ROWS:
        reason = f"only {good_rows} finite positive radius/velocity rows"
    return good_rows, reason


def discover_source_root(project_root: Path) -> Optional[Path]:
    parent = project_root.parent
    try:
        siblings = list(parent.iterdir())
    except OSError:
        return None
    for sibling in siblings:
        if sibling == project_root or not sibling.is_dir():
            continue
        if (sibling / "data" / "sparc").is_dir() and (sibling / "vendor" / "h1_src" / "run_sparc_lite.py").is_file():
            return sibling
    return None


def discover_adapter(source_root: Path) -> Optional[Path]:
    analysis_root = source_root / "comparative_analysis" / "comparative_validation"
    if not analysis_root.is_dir():
        return None
    try:
        parents = list(analysis_root.iterdir())
    except OSError:
        return None
    markers = ["def reconstruct_bundle", "def density_peak_from_sigma", "def density_peak_from_c"]
    for parent in parents:
        if not parent.is_dir():
            continue
        for child in parent.glob("*extended_shared*"):
            if not child.is_dir():
                continue
            for candidate in child.glob("run_*extended_shared_*.py"):
                try:
                    text = candidate.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if all(marker in text for marker in markers):
                    return candidate
    return None


class BootstrapValidator:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.mode = args.mode
        self.checks: List[CheckRecord] = []
        self.inventory: List[InventoryRecord] = []
        self.counter = 1
        self.default_warnings: List[str] = []
        self.project_root = (args.project_root or Path.cwd()).resolve()
        if args.project_root is None:
            self.default_warnings.append("project root defaulted to current working directory; explicit --project-root is preferred")
        self.source_root = args.source_root.resolve() if args.source_root else None
        self.sparc_extractor_root = args.sparc_extractor_root.resolve() if args.sparc_extractor_root else None
        self.release_root = args.release_root.resolve() if args.release_root else None
        self.catalog = self.load_error_catalog()

    def load_error_catalog(self) -> Dict[str, Dict[str, str]]:
        path = self.project_root / "notes" / "SPARC_PREFLIGHT_ERROR_CATALOG.csv"
        if not path.is_file():
            return {}
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                return {row["error_code"]: row for row in csv.DictReader(handle)}
        except OSError:
            return {}

    def next_id(self, prefix: str) -> str:
        value = f"{prefix}{self.counter:03d}"
        self.counter += 1
        return value

    def add_check(
        self,
        check_name: str,
        severity: str,
        status: str,
        observed: Any,
        expected: Any,
        path_or_pattern: Any = "",
        remediation: str = "",
        mode_blocked: str = "",
        mode_still_available: str = "",
        notes: str = "",
        check_id: Optional[str] = None,
    ) -> None:
        if severity not in {"ERROR", "WARNING", "INFO"}:
            raise ValueError(f"invalid severity: {severity}")
        if status not in {"PASS", "FAIL", "WARN", "SKIP", "NOT_APPLICABLE"}:
            raise ValueError(f"invalid status: {status}")
        prefix = self.mode.split("-")[0].upper()[:3]
        self.checks.append(
            CheckRecord(
                check_id or self.next_id(prefix),
                self.mode,
                check_name,
                severity,
                status,
                as_text(observed),
                as_text(expected),
                as_text(path_or_pattern),
                remediation,
                mode_blocked,
                mode_still_available,
                notes,
            )
        )

    def add_catalog_check(self, code: str, check_name: str, status: str, observed: Any = "", notes: str = "") -> None:
        row = self.catalog.get(code, {})
        severity = row.get("severity", "ERROR")
        self.add_check(
            check_name=check_name,
            severity=severity,
            status=status,
            observed=observed or row.get("condition", ""),
            expected=row.get("expected_path_or_pattern", ""),
            path_or_pattern=row.get("expected_path_or_pattern", ""),
            remediation=row.get("remediation", ""),
            mode_blocked=row.get("mode_blocked", ""),
            mode_still_available=row.get("mode_still_available", ""),
            notes=notes or row.get("user_message", ""),
            check_id=code,
        )

    def add_inventory(
        self,
        input_id: str,
        path_or_pattern: Any,
        path: Optional[Path],
        expected_count: Any = "",
        observed_count: Any = "",
        status: str = "INFO",
        classification: str = "",
        notes: str = "",
    ) -> None:
        exists = readable = size = ""
        if path is not None:
            exists, readable, size = file_state(path)
        self.inventory.append(
            InventoryRecord(
                input_id=input_id,
                mode=self.mode,
                path_or_pattern=as_text(path_or_pattern),
                exists=exists,
                readable=readable,
                size_bytes=size,
                expected_count=as_text(expected_count),
                observed_count=as_text(observed_count),
                status=status,
                classification=classification,
                notes=notes,
            )
        )

    def file_check(self, check_name: str, path: Path, severity: str, expected: str, remediation: str, mode_blocked: str, mode_still_available: str, check_id: Optional[str] = None) -> bool:
        exists, readable, size = file_state(path)
        ok = exists == "YES" and readable == "YES" and (not path.is_file() or int(size or 0) > 0)
        self.add_check(
            check_name,
            severity,
            "PASS" if ok else "FAIL",
            f"exists={exists}; readable={readable}; size_bytes={size}",
            expected,
            path,
            remediation,
            mode_blocked,
            mode_still_available,
            check_id=check_id,
        )
        return ok

    def resolve_source_root(self) -> Optional[Path]:
        if self.source_root is not None:
            return self.source_root
        discovered = discover_source_root(self.project_root)
        if discovered is not None:
            self.source_root = discovered.resolve()
            self.add_check(
                "source root default discovery",
                "WARNING",
                "WARN",
                "source root discovered by sibling scan",
                "explicit --source-root preferred",
                "<source-root>",
                "Pass --source-root for reproducible validation.",
                "none if discovery is correct",
                "all modes",
                "Default discovery mirrors current engine behavior.",
            )
            return self.source_root
        self.add_catalog_check("SPARC013_SOURCE_ROOT_NOT_FOUND", "source root discovery", "FAIL")
        return None

    def resolve_extractor_root(self) -> Optional[Path]:
        if self.sparc_extractor_root is not None:
            return self.sparc_extractor_root
        source = self.resolve_source_root()
        if source is not None:
            candidate = source / "tools" / "sparc_extractor"
            if candidate.is_dir():
                self.sparc_extractor_root = candidate.resolve()
                self.add_check(
                    "SPARC extractor root default discovery",
                    "WARNING",
                    "WARN",
                    "extractor root discovered under source root",
                    "explicit --sparc-extractor-root preferred",
                    "<sparc-extractor-root>",
                    "Pass --sparc-extractor-root for reproducible validation.",
                    "none if discovery is correct",
                    "all modes",
                )
                return self.sparc_extractor_root
        self.add_check(
            "SPARC extractor root discovery",
            "ERROR",
            "FAIL",
            "not found",
            "explicit --sparc-extractor-root or source-root/tools/sparc_extractor",
            "<sparc-extractor-root>",
            "Provide --sparc-extractor-root for parameter extraction validation.",
            "parameter-extraction",
            "paper reproduction",
        )
        return None

    def run(self) -> int:
        if self.mode == "parameter-extraction":
            self.check_parameter_extraction()
        elif self.mode == "test-mode":
            self.check_test_mode()
        elif self.mode == "full-production":
            self.check_full_production()
        elif self.mode == "figure-reproduction":
            self.check_figure_reproduction()
        elif self.mode == "manuscript-reproduction":
            self.check_manuscript_reproduction()
        else:
            raise AssertionError(self.mode)
        return 1 if self.has_blocking_errors() else 0

    def has_blocking_errors(self) -> bool:
        return any(check.severity == "ERROR" and check.status == "FAIL" for check in self.checks)

    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.status == "WARN" or (check.severity == "WARNING" and check.status == "FAIL"))

    def error_count(self) -> int:
        return sum(1 for check in self.checks if check.severity == "ERROR" and check.status == "FAIL")

    def check_parameter_extraction(self) -> None:
        root = self.resolve_extractor_root()
        if root is None:
            return
        raw = root / "RAW"
        self.add_inventory("sparc_extractor_raw", "<sparc-extractor-root>/RAW", raw, status="INFO", classification="REQUIRED_PARAMETER_EXTRACTION")
        actual_names = []
        try:
            actual_names = [child.name for child in raw.iterdir()]
        except OSError:
            pass
        lowercase_present = "table1.mrt" in actual_names
        wrong_case_present = any(name.lower() == "table1.mrt" and name != "table1.mrt" for name in actual_names)
        table1 = raw / "table1.mrt"
        if not lowercase_present and wrong_case_present:
            self.add_catalog_check("SPARC002_TABLE1_WRONG_CASE", "table1 lowercase filename", "FAIL", observed="wrong-case table1 variant present")
        if not self.file_check(
            "required SPARC table1.mrt",
            table1,
            "ERROR",
            "readable nonzero lowercase table1.mrt",
            "Place official SPARC table1.mrt under RAW with lowercase filename.",
            "parameter-extraction",
            "paper reproduction from compact outputs",
            check_id="SPARC001_TABLE1_MISSING",
        ):
            self.add_inventory("sparc_table1_raw", "RAW/table1.mrt", table1, expected_count="175 rows", status="FAIL", classification="REQUIRED_PARAMETER_EXTRACTION")
            return
        rows, malformed = parse_table1_rows(table1)
        names = [row["key"] for row in rows]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        self.add_inventory("sparc_table1_raw", "RAW/table1.mrt", table1, expected_count=EXPECTED_TABLE1_RECORDS, observed_count=len(rows), status="PASS" if len(rows) == EXPECTED_TABLE1_RECORDS else "FAIL", classification="REQUIRED_PARAMETER_EXTRACTION")
        self.add_check(
            "table1 candidate galaxy count",
            "ERROR",
            "PASS" if len(rows) == EXPECTED_TABLE1_RECORDS else "FAIL",
            len(rows),
            EXPECTED_TABLE1_RECORDS,
            "RAW/table1.mrt",
            "Use complete official SPARC table1.mrt.",
            "parameter-extraction",
            "paper reproduction from compact outputs",
            check_id="SPARC003_TABLE1_BAD_COUNT",
        )
        self.add_check(
            "table1 duplicate normalized names",
            "ERROR",
            "PASS" if not duplicates else "FAIL",
            duplicates or "none",
            "no duplicate canonical names",
            "RAW/table1.mrt",
            "Inspect aliases and duplicate source rows.",
            "parameter-extraction",
            "paper reproduction from compact outputs",
            check_id="SPARC005_TABLE1_DUPLICATE_NAMES",
        )
        self.add_check(
            "table1 numeric field parse",
            "ERROR",
            "PASS" if not malformed else "FAIL",
            malformed[:10] if malformed else "none",
            "L36/Rd/MHI not all malformed for candidate rows",
            "RAW/table1.mrt",
            "Check fixed-width/split parser assumptions and file integrity.",
            "parameter-extraction",
            "paper reproduction from compact outputs",
            check_id="SPARC004_TABLE1_MALFORMED_FIELDS",
        )
        for input_id, filename, code in [
            ("sparc_bulges_raw", "Bulges.mrt", "SPARC006_OPTIONAL_BULGES_MISSING"),
            ("sparc_wise_raw", "wise_ii table1.mrt", "SPARC007_OPTIONAL_WISE_MISSING"),
        ]:
            path = raw / filename
            exists, readable, size = file_state(path)
            status = "PASS" if exists == "YES" and readable == "YES" and int(size or 0) > 0 else "WARN"
            self.add_check(
                f"optional {filename}",
                "WARNING",
                status,
                f"exists={exists}; readable={readable}; size_bytes={size}",
                "optional fallback file if available",
                f"RAW/{filename}",
                self.catalog.get(code, {}).get("remediation", "Optional fallback may be supplied if needed."),
                self.catalog.get(code, {}).get("mode_blocked", "none"),
                self.catalog.get(code, {}).get("mode_still_available", "all current modes"),
                check_id=code,
            )
            self.add_inventory(input_id, f"RAW/{filename}", path, expected_count="0 or 1 optional", observed_count=exists, status=status, classification="OPTIONAL_PARAMETER_FALLBACK")
        rotmod = raw / "rotmod"
        rotmod_files = list(rotmod.glob("*_rotmod.dat")) if rotmod.is_dir() else []
        self.add_check(
            "optional extraction rotmod directory",
            "WARNING" if not rotmod_files else "INFO",
            "PASS" if rotmod_files else "WARN",
            f"{len(rotmod_files)} *_rotmod.dat files",
            "optional fallback; 175 files for complete coverage",
            "RAW/rotmod/*_rotmod.dat",
            "Optional for extraction; required rotmods are checked separately for test/full production.",
            "none for extraction if table fields suffice",
            "parameter-extraction",
            check_id="SPARC008_OPTIONAL_ROTMOD_FALLBACK_MISSING",
        )
        self.add_inventory("sparc_extractor_rotmod", "RAW/rotmod/*_rotmod.dat", rotmod, expected_count="optional; 175 for complete fallback", observed_count=len(rotmod_files), status="PASS" if rotmod_files else "WARN", classification="OPTIONAL_PARAMETER_FALLBACK")
        zip_files = list(raw.glob("rotmod*.zip"))
        self.add_check("optional rotmod archive fallback", "INFO", "PASS" if zip_files else "NOT_APPLICABLE", len(zip_files), "0 or more optional archives", "RAW/rotmod*.zip", "No action required unless archive fallback is intended.", "none", "all current modes")
        table2 = raw / "table2.mrt"
        table2_exists = table2.is_file()
        self.add_check("table2 current-stage status", "INFO", "NOT_APPLICABLE", "present" if table2_exists else "absent", "not required by current extractor/production path", "RAW/table2.mrt", "No action required for current NRCB modes.", "none", "all current modes", check_id="SPARC009_TABLE2_MISSING")
        output_dir = root / "output"
        json_lower = output_dir / "galaxies_h1_lines.json"
        json_upper = output_dir / "galaxies_h1_lines.JSON"
        if json_lower.exists() or json_upper.exists():
            status = "WARN" if json_upper.exists() and not json_lower.exists() else "PASS"
            observed = f"lowercase={json_lower.exists()}; uppercase={json_upper.exists()}"
            self.add_check("extractor JSON extension case", "WARNING", status, observed, "consistent lowercase .json preferred", "output/galaxies_h1_lines.json", "Normalize future release outputs or make validator case-aware.", "none", "parameter-extraction", check_id="SPARC011_JSON_CASE_MISMATCH")

    def read_attrition_checked(self) -> Tuple[List[str], List[str]]:
        attrition = self.project_root / "notes" / "SAMPLE_ATTRITION_134_TO_76.csv"
        if not attrition.is_file():
            self.add_catalog_check("SPARC025_BRANCH_ATTRITION_MISSING", "branch attrition file", "FAIL")
            return [], []
        partial, spectral, row_count, duplicates = parse_attrition(attrition)
        ok = len(partial) == EXPECTED_PARTIAL and len(spectral) == EXPECTED_SPECTRAL and set(spectral).issubset(partial) and not duplicates
        self.add_inventory("sample_attrition_contract", "notes/SAMPLE_ATTRITION_134_TO_76.csv", attrition, expected_count="175 rows; partial=134; spectral=76", observed_count=f"rows={row_count}; partial={len(partial)}; spectral={len(spectral)}", status="PASS" if ok else "FAIL", classification="REQUIRED_FULL_PRODUCTION")
        self.add_check("branch attrition counts and subset", "ERROR", "PASS" if ok else "FAIL", f"rows={row_count}; partial={len(partial)}; spectral={len(spectral)}; duplicates={duplicates or 'none'}", "rows=175; partial=134; spectral=76; spectral subset partial", "notes/SAMPLE_ATTRITION_134_TO_76.csv", "Restore or audit the branch-membership contract.", "test-mode;full-production", "figure/manuscript reproduction", check_id="SPARC026_BRANCH_COUNTS_MISMATCH")
        return partial, spectral

    def check_project_contracts(self) -> None:
        for name in CONTRACT_FILES:
            path = self.project_root / "notes" / name
            self.file_check(f"project contract {name}", path, "ERROR", "required contract/provenance file exists", "Restore audited project contract file.", "test-mode;full-production", "figure/manuscript reproduction")
            self.add_inventory(f"contract_{name}", f"notes/{name}", path, expected_count="1 file", observed_count="1" if path.is_file() else "0", status="PASS" if path.is_file() else "FAIL", classification="REQUIRED_FULL_PRODUCTION")

    def check_source_common(self) -> Tuple[Optional[Path], Dict[str, Dict[str, Any]], Optional[float], Optional[Path]]:
        source = self.resolve_source_root()
        if source is None:
            return None, {}, None, None
        sparc_dir = source / "data" / "sparc"
        self.file_check("source data/sparc directory", sparc_dir, "ERROR", "directory exists", "Provide source root with data/sparc rotation-curve files.", "test-mode;full-production", "paper reproduction", check_id="SPARC021_ROTMOD_DIR_MISSING")
        vendor_run = source / "vendor" / "h1_src" / "run_sparc_lite.py"
        self.file_check("vendor frozen parameter source", vendor_run, "ERROR", "run_sparc_lite.py exists", "Restore verified vendored source file.", "test-mode;full-production", "paper reproduction", check_id="SPARC014_VENDOR_RUN_MISSING")
        fleet: Dict[str, Dict[str, Any]] = {}
        if vendor_run.is_file():
            try:
                fleet = parse_frozen_parameters(vendor_run)
            except Exception as exc:
                self.add_check("vendor embedded parameter parse", "ERROR", "FAIL", type(exc).__name__, "175 embedded parameter records", "vendor source", "Inspect vendor source parser markers.", "test-mode;full-production", "paper reproduction", check_id="SPARC015_EMBEDDED_PARAMETERS_MISSING")
            else:
                self.add_check("vendor embedded parameter count", "ERROR", "PASS" if len(fleet) == EXPECTED_VENDOR_RECORDS else "FAIL", len(fleet), EXPECTED_VENDOR_RECORDS, "vendor source", "Restore audited embedded parameter source.", "test-mode;full-production", "paper reproduction", check_id="SPARC015_EMBEDDED_PARAMETERS_MISSING")
        g_file = source / "vendor" / "h1_src" / "src" / "newtonian.py"
        self.file_check("gravity constant source", g_file, "ERROR", "newtonian.py with literal G", "Restore verified gravity-constant source.", "test-mode;full-production", "paper reproduction", check_id="SPARC017_GRAVITY_CONSTANT_MISSING")
        constant = parse_gravity_constant(g_file) if g_file.is_file() else None
        self.add_check("gravity constant parse", "ERROR", "PASS" if constant is not None else "FAIL", constant if constant is not None else "not parsed", "finite literal G assignment", "vendor source", "Restore audited constant source.", "test-mode;full-production", "paper reproduction", check_id="SPARC017_GRAVITY_CONSTANT_MISSING")
        adapter = discover_adapter(source)
        self.add_check("reconstruction adapter discovery", "ERROR", "PASS" if adapter else "FAIL", "discovered under comparative_analysis" if adapter else "not found", "one adapter matching required markers", "comparative_analysis/comparative_validation/**/run_*extended_shared_*.py", "Restore verified adapter or configure explicit adapter path in future wrapper.", "test-mode;full-production", "paper reproduction", check_id="SPARC018_ADAPTER_NOT_FOUND")
        if adapter:
            try:
                compile(adapter.read_text(encoding="utf-8", errors="ignore"), str(adapter), "exec")
                syntax_status = "PASS"
                observed = "syntax compile succeeded"
            except Exception as exc:
                syntax_status = "FAIL"
                observed = f"{type(exc).__name__}: {exc}"
            self.add_check("adapter syntax compile", "ERROR", syntax_status, observed, "adapter source parses", "adapter source", "Inspect adapter syntax/dependencies before rerun.", "test-mode;full-production", "paper reproduction", check_id="SPARC019_ADAPTER_IMPORT_FAILED")
        for module_name in ("numpy", "scipy"):
            found = importlib.util.find_spec(module_name) is not None
            self.add_check(f"Python dependency available: {module_name}", "WARNING", "PASS" if found else "WARN", "available" if found else "not importable", "dependency importable for reconstruction adapter", module_name, "Install documented environment before test/full production rerun.", "test/full production may fail if missing", "paper reproduction", notes="Dependency check only; adapter was not executed.")
        return source, fleet, constant, adapter

    def check_rotmod_files(self, source: Path, galaxies: Sequence[str], mode_label: str) -> None:
        sparc_dir = source / "data" / "sparc"
        missing: List[str] = []
        malformed: List[str] = []
        for galaxy in galaxies:
            path = sparc_dir / f"{galaxy}_rotmod.dat"
            self.add_inventory(f"rotmod_{galaxy}", f"data/sparc/{galaxy}_rotmod.dat", path, expected_count=f">={MIN_ROTMOD_ROWS} finite positive rows", classification="REQUIRED_FULL_PRODUCTION" if mode_label == "full-production" else "REQUIRED_TEST_MODE")
            if not path.is_file() or path.stat().st_size <= 0:
                missing.append(galaxy)
                continue
            good_rows, reason = rotmod_quality(path)
            if good_rows < MIN_ROTMOD_ROWS:
                malformed.append(f"{galaxy}: {reason}")
        self.add_check(
            f"{mode_label} selected rotmod files present",
            "ERROR",
            "PASS" if not missing else "FAIL",
            missing or "none missing",
            f"{len(galaxies)} selected galaxy rotmod files",
            "data/sparc/{galaxy}_rotmod.dat",
            "Restore missing official rotmod files; do not rerun until coverage is complete.",
            mode_label,
            "paper reproduction from compact outputs",
            check_id="SPARC022_SELECTED_ROTMOD_MISSING" if missing else None,
        )
        self.add_check(
            f"{mode_label} selected rotmod parse quality",
            "ERROR",
            "PASS" if not malformed else "FAIL",
            malformed[:20] if malformed else "all selected files have sufficient finite rows",
            f"at least {MIN_ROTMOD_ROWS} finite positive radius/velocity rows per file",
            "data/sparc/{galaxy}_rotmod.dat",
            "Inspect malformed rotmod files and replace corrupted inputs.",
            mode_label,
            "paper reproduction from compact outputs",
            check_id="SPARC023_ROTMOD_MALFORMED" if malformed else None,
        )

    def check_test_mode(self) -> None:
        self.check_project_contracts()
        partial, spectral = self.read_attrition_checked()
        source, fleet, _constant, _adapter = self.check_source_common()
        selected = spectral[:TEST_GALAXIES]
        self.add_check("test-mode selected galaxies", "INFO", "PASS" if len(selected) == TEST_GALAXIES else "FAIL", selected, "first two sorted spectral-valid galaxies", "attrition contract", "Restore attrition contract before test-mode rerun.", "test-mode", "paper reproduction")
        if fleet:
            missing_params = [galaxy for galaxy in selected if galaxy not in fleet]
            self.add_check("test-mode vendor parameter coverage", "ERROR", "PASS" if not missing_params else "FAIL", missing_params or "complete", "embedded parameters for selected test galaxies", "vendor source", "Restore audited vendor parameter source.", "test-mode", "paper reproduction", check_id="SPARC028_VENDOR_BRANCH_COVERAGE_MISSING" if missing_params else None)
        if source is not None and selected:
            self.check_rotmod_files(source, selected, "test-mode")

    def check_full_production(self) -> None:
        self.check_project_contracts()
        partial, spectral = self.read_attrition_checked()
        source, fleet, _constant, _adapter = self.check_source_common()
        if fleet and partial:
            missing_params = [galaxy for galaxy in partial if galaxy not in fleet]
            self.add_check("full-production vendor parameter coverage", "ERROR", "PASS" if not missing_params else "FAIL", missing_params[:20] if missing_params else "complete", "embedded parameters for all 134 partial-branch galaxies", "vendor source", "Restore audited vendor parameter source before full production.", "full-production", "paper reproduction", check_id="SPARC028_VENDOR_BRANCH_COVERAGE_MISSING" if missing_params else None)
        subset_ok = bool(spectral) and set(spectral).issubset(partial)
        self.add_check("full-production spectral subset coverage", "ERROR", "PASS" if subset_ok else "FAIL", f"partial={len(partial)}; spectral={len(spectral)}", "spectral N=76 is subset of partial N=134", "attrition contract", "Reconcile branch membership before full production.", "full-production", "paper reproduction", check_id="SPARC027_SPECTRAL_NOT_SUBSET" if not subset_ok else None)
        if source is not None and partial:
            self.check_rotmod_files(source, partial, "full-production")
        engine = self.project_root / "src" / "run_m_surrogate_extension.py"
        guard_ok = False
        observed = "engine missing"
        if engine.is_file():
            text = engine.read_text(encoding="utf-8", errors="ignore")
            markers = ["reconcile_execution", "production_blocked", "MISSING_RECONSTRUCTION", "no_galaxies_silently_removed"]
            guard_ok = all(marker in text for marker in markers)
            observed = "; ".join(marker for marker in markers if marker in text) or "required guard markers not found"
        self.add_check("production reconciliation guard scan", "ERROR", "PASS" if guard_ok else "FAIL", observed, "reconciliation/zero-row protection markers present", "src/run_m_surrogate_extension.py", "Inspect production engine guard logic before full production.", "full-production", "paper reproduction")
        if self.args.allow_one_galaxy_dry_run:
            self.add_check("optional one-galaxy dry-run", "INFO", "SKIP", "not run", "safe dry-run interface explicitly supported", "reconstruction adapter", "No safe standalone one-galaxy dry-run interface is implemented in this validator.", "none", "all modes", notes="Production was not run.")

    def check_figure_reproduction(self) -> None:
        root = self.release_root if self.release_root else self.project_root
        script_candidates = [root / "figures" / "generate_control_validation_figures.py", root / "figures" / "source" / "generate_control_validation_figures.py"]
        script = next((candidate for candidate in script_candidates if candidate.is_file()), script_candidates[0])
        self.file_check("figure generation script", script, "ERROR", "figure-generation script exists", "Restore figure-generation script if figure regeneration is needed.", "figure-reproduction", "manuscript reproduction if final PDFs exist")
        results = root / "results" / "m_surrogate_extension_v1"
        for name, expected_rows in [("per_galaxy_null_summary.csv", "916 rows"), ("global_control_battery_summary.csv", "9 rows"), ("figure2_source_data.csv", "3436 rows")]:
            path = results / name
            ok = self.file_check(f"compact result {name}", path, "ERROR", f"nonzero CSV with {expected_rows}", "Restore QC-accepted compact result file.", "figure-reproduction;paper reproduction", "manuscript compile if final figures exist")
            observed_rows = count_csv_rows(path) if ok else None
            self.add_inventory(name, f"results/m_surrogate_extension_v1/{name}", path, expected_count=expected_rows, observed_count=observed_rows if observed_rows is not None else "", status="PASS" if ok else "FAIL", classification="REQUIRED_FIGURE_REPRODUCTION")
        for name in [
            "figure1_workflow_control_validation_rev1.pdf",
            "figure2_control_distribution_comparison_rev1.pdf",
            "figure3_spectral_phase_control_caveat_rev1.pdf",
        ]:
            candidates = [root / "figures" / name, root / "manuscript" / "figures" / name]
            found = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
            self.file_check(f"final figure PDF {name}", found, "ERROR", "final approved figure PDF exists", "Restore approved final figure PDF; do not regenerate without authorization.", "manuscript/figure reproduction", "compact result inspection", check_id="SPARC032_MANUSCRIPT_FIGURE_MISSING" if not found.is_file() else None)
        large = results / "per_realization_controls.csv"
        self.add_check("large realization table requirement", "INFO", "NOT_APPLICABLE", "present" if large.exists() else "absent", "not required for figure/paper reproduction", "results/m_surrogate_extension_v1/per_realization_controls.csv", "No action needed for paper reproduction.", "none", "figure/manuscript reproduction", check_id="SPARC036_LARGE_REALIZATION_ABSENT")

    def check_manuscript_reproduction(self) -> None:
        root = self.release_root if self.release_root else self.project_root
        manuscript = root / "manuscript"
        main_tex = manuscript / "main.tex"
        if not self.file_check("manuscript main.tex", main_tex, "ERROR", "main.tex exists", "Restore manuscript/main.tex.", "manuscript-reproduction", "figure/result inspection"):
            return
        text = main_tex.read_text(encoding="utf-8", errors="ignore")
        active = "\n".join(strip_latex_comment(line) for line in text.splitlines())
        section_refs = re.findall(r"\\(?:input|include)\{([^}]+)\}", active)
        missing_sections: List[str] = []
        for ref in section_refs:
            section_path = (manuscript / ref)
            if section_path.suffix == "":
                section_path = section_path.with_suffix(".tex")
            if not section_path.is_file():
                missing_sections.append(ref)
            self.add_inventory(f"manuscript_section_{ref}", ref, section_path, expected_count="1 file", observed_count="1" if section_path.is_file() else "0", status="PASS" if section_path.is_file() else "FAIL", classification="REQUIRED_MANUSCRIPT_REPRODUCTION")
        self.add_check("active section files", "ERROR", "PASS" if not missing_sections else "FAIL", missing_sections or "all active sections present", "all active input/include files exist", "manuscript/sections/*.tex", "Restore missing active section files.", "manuscript-reproduction", "source inspection")
        refs = manuscript / "references.bib"
        self.file_check("bibliography file", refs, "ERROR", "references.bib exists", "Restore manuscript/references.bib.", "manuscript-reproduction", "source inspection")
        graphics_refs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", active)
        missing_figs: List[str] = []
        for ref in graphics_refs:
            fig_path = (manuscript / ref)
            if fig_path.suffix == "":
                fig_path = fig_path.with_suffix(".pdf")
            if not fig_path.is_file():
                missing_figs.append(ref)
            self.add_inventory(f"manuscript_figure_{Path(ref).name}", ref, fig_path, expected_count="1 file", observed_count="1" if fig_path.is_file() else "0", status="PASS" if fig_path.is_file() else "FAIL", classification="REQUIRED_MANUSCRIPT_REPRODUCTION")
        self.add_check("included figure files", "ERROR", "PASS" if not missing_figs else "FAIL", missing_figs or "all included figures present", "all includegraphics targets exist", "figure PDF paths in manuscript", "Restore approved figure PDFs.", "manuscript-reproduction", "compact result inspection", check_id="SPARC032_MANUSCRIPT_FIGURE_MISSING" if missing_figs else None)
        self.add_check("raw SPARC requirement for compile-only", "INFO", "NOT_APPLICABLE", "not required", "manuscript compile should not require raw SPARC/source repository", "data/external/SPARC", "No action required for compile-only reproduction.", "none", "manuscript reproduction")
        if self.args.strict:
            self.strict_compile(manuscript, main_tex)

    def strict_compile(self, manuscript: Path, main_tex: Path) -> None:
        pdflatex = shutil.which("pdflatex")
        if not pdflatex:
            self.add_check("strict LaTeX compile", "WARNING", "SKIP", "pdflatex not available", "pdflatex available", "manuscript/main.tex", "Install TeX locally to run strict compile check.", "none", "manuscript source checks", notes="No build artifacts were created.")
            return
        with tempfile.TemporaryDirectory(prefix="sparc_bootstrap_tex_") as temp_dir:
            command = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={temp_dir}", str(main_tex)]
            proc = subprocess.run(command, cwd=str(manuscript), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
            self.add_check("strict LaTeX compile", "ERROR", "PASS" if proc.returncode == 0 else "FAIL", f"exit_code={proc.returncode}", "pdflatex exits 0 in temporary output directory", "manuscript/main.tex", "Inspect LaTeX log; validator leaves no build artifacts.", "manuscript-reproduction", "non-strict source checks", notes="Temporary compile output was removed.")

    def write_outputs(self) -> None:
        if not self.args.output_dir:
            status = "FAIL" if self.has_blocking_errors() else "PASS"
            print(f"SPARC_BOOTSTRAP_VALIDATION_STATUS={status}")
            print(f"MODE={self.mode}")
            print(f"ERRORS={self.error_count()}")
            print(f"WARNINGS={self.warning_count()}")
            for check in self.checks:
                if check.status in {"FAIL", "WARN"}:
                    print(f"{check.severity}:{check.status}:{check.check_name}: {check.observed}")
            return
        output_dir = self.args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        checks_path = output_dir / "sparc_bootstrap_validation_checks.csv"
        with checks_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CHECK_COLUMNS)
            writer.writeheader()
            for check in self.checks:
                writer.writerow(asdict(check))
        inventory_path = output_dir / "sparc_bootstrap_file_inventory.csv"
        with inventory_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=INVENTORY_COLUMNS)
            writer.writeheader()
            for item in self.inventory:
                writer.writerow(asdict(item))
        report_path = output_dir / "sparc_bootstrap_validation_report.md"
        report_path.write_text(self.render_report(), encoding="utf-8")
        if self.args.json:
            payload = {
                "mode": self.mode,
                "status": "FAIL" if self.has_blocking_errors() else "PASS",
                "error_count": self.error_count(),
                "warning_count": self.warning_count(),
                "checks": [asdict(check) for check in self.checks],
                "file_inventory": [asdict(item) for item in self.inventory],
            }
            (output_dir / "sparc_bootstrap_validation.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def render_report(self) -> str:
        status = "FAIL" if self.has_blocking_errors() else "PASS"
        lines = [
            "# SPARC Bootstrap Validation Report",
            "",
            f"- Mode: `{self.mode}`",
            f"- Overall status: `{status}`",
            f"- Blocking errors: {self.error_count()}",
            f"- Warnings: {self.warning_count()}",
            "- Downloads attempted: NO",
            "- Production rerun attempted: NO",
            "- Figures regenerated: NO",
            "",
            "## Summary",
            "",
        ]
        if self.has_blocking_errors():
            lines.append("This preflight found one or more blocking errors for the selected mode. Other modes may remain available as listed in the check table.")
        else:
            lines.append("This preflight found no blocking errors for the selected mode. Warnings, if present, should still be reviewed before public release or full rerun support.")
        lines += ["", "## Failed or Warning Checks", ""]
        notable = [check for check in self.checks if check.status in {"FAIL", "WARN"}]
        if not notable:
            lines.append("No failed or warning checks.")
        else:
            for check in notable:
                lines.append(f"- `{check.check_id}` {check.severity}/{check.status}: {check.check_name}. Observed: {check.observed}. Remediation: {check.remediation}")
        lines += ["", "## All Checks", ""]
        for check in self.checks:
            lines.append(f"- `{check.check_id}` `{check.status}` `{check.severity}` - {check.check_name}")
        lines += ["", "## File Inventory", ""]
        if not self.inventory:
            lines.append("No file inventory entries were recorded for this mode.")
        else:
            for item in self.inventory:
                lines.append(f"- `{item.input_id}` `{item.status}`: {item.path_or_pattern} ({item.observed_count or item.exists})")
        lines.append("")
        return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    validator = BootstrapValidator(args)
    exit_code = validator.run()
    validator.write_outputs()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
