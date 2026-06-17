# User Workflow Layer Design

## Overview

The refreshed release design separates three user modes so readers do not confuse paper reproduction with full production reruns or future user-data adaptation.

## Mode 1: Paper Reproduction Mode

Goal: reproduce the manuscript package and verify compact reported outputs.

Typical workflow:

1. Install the locked environment once it is finalized.
2. Compile the manuscript.
3. Confirm final figure PDFs exist.
4. Verify compact result files exist.
5. Run a future `src/check_release_integrity.py` smoke test.
6. Compare rounded manuscript values against `provenance/FIGURE_VALUE_LEDGER.csv`.

Inputs:

- Manuscript source.
- Final figures.
- Compact summary CSVs.
- Provenance ledgers.

Not required:

- Raw SPARC redistribution.
- Full production rerun.
- Large `per_realization_controls.csv` table.

Status: ready for release-package build, with integrity-check script still to be implemented.

## Mode 2: Example / Smoke-Test Mode

Goal: demonstrate expected data shape and small diagnostic outputs using an included example.

Planned workflow:

1. Read `data/example/example_radial_profiles.csv`.
2. Validate columns and finite values.
3. Run a small diagnostic configuration with reduced surrogate counts.
4. Write example outputs into `examples/output/` or `results/example_smoke_test/`.
5. Check that output schemas match documented expectations.

Needed future pieces:

- Small example dataset that is either synthetic or redistributable.
- `src/validate_user_profile_csv.py`.
- `src/run_example_smoke_test.py`.
- Example output schema documentation.

Status: designed but not implemented.

## Mode 3: User-Supplied Data Mode

Goal: let researchers run the workflow on their own radial-profile data when the input contract is satisfied.

Planned workflow:

1. Place CSV files under `data/user_profiles/`.
2. Run schema validation.
3. Inspect branch eligibility report.
4. Run diagnostics with explicit user-selected surrogate counts.
5. Review warnings and invalid-row accounting.
6. Use output summaries only within the stated control-family definitions.

Needed future pieces:

- `src/run_user_radial_profile_diagnostics.py`.
- User input adapter from CSV groups to diagnostic vectors.
- Clear branch eligibility rules.
- Output directory isolation for user runs.
- Runtime and memory guidance after measurement.

Status: designed but requires future wrapper implementation.

## Full Production Rerun Mode

Goal: rerun the original paper production pipeline when external source/data dependencies are available.

Current script:

- `src/run_m_surrogate_extension.py --production`.

Constraints:

- Requires paper-specific reconstruction adapter and external data/source tree.
- Should not be represented as the quick user-data path.
- Runtime depends on data volume and surrogate counts.
- Raw/external data redistribution must be resolved before public release.

## Language Boundary

The user workflow must describe computational diagnostics and control-family outputs only. It must not imply physical interpretation, model validation, or field-wide practice claims.
