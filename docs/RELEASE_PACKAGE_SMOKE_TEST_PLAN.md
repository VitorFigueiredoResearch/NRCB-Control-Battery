# Release Package Smoke Test Plan V2

This is a design plan only. The smoke test is not run in this task.

## Goals

- Verify the clean release candidate is self-consistent.
- Confirm manuscript compilation and citation resolution.
- Confirm compact result files and figure files exist.
- Confirm no private paths or excluded files entered the release.
- Confirm future example/user-data wrappers are clearly marked if not implemented.

## Paper Reproduction Checks

1. Check required manuscript files exist.
2. Run LaTeX compile sequence if TeX is available.
3. Confirm all cited keys resolve.
4. Confirm final figure PDFs exist.
5. Confirm compact result CSVs exist and are nonzero.
6. Confirm `FIGURE_VALUE_LEDGER.csv` exists.
7. Compare selected rounded manuscript values against ledger values.
8. Confirm no raw `per_realization_controls.csv` is required for paper reproduction.

## Figure Checks

1. Confirm three final revised PDFs exist.
2. Confirm figure-generation script exists.
3. Confirm figure source files exist.
4. If figure regeneration is enabled, run it in an isolated output directory.
5. Confirm branch labels and sample sizes remain explicit.

## Provenance Checks

1. Confirm production QC rerun report exists.
2. Confirm patch report exists.
3. Confirm citation lock and citation reaudit exist.
4. Confirm rounding policy and terminology lock exist.
5. Confirm release manifest exists.

## Example / Smoke-Test Checks

Future, after implementation:

1. Confirm example CSV exists.
2. Run `src/validate_user_profile_csv.py data/example/example_radial_profiles.csv`.
3. Run `src/run_example_smoke_test.py`.
4. Confirm example outputs are created in an isolated folder.
5. Confirm no physical interpretation is emitted.

## User-Supplied Data Checks

Future, after implementation:

1. Validate a user CSV with required columns.
2. Confirm branch eligibility report is emitted.
3. Run diagnostics only on valid groups.
4. Confirm invalid rows are reported and not silently removed.
5. Confirm output summaries remain within documented control-family scope.

## Release Hygiene Checks

1. Search for private absolute paths.
2. Search for backup and draft directories.
3. Search for excluded internal terms.
4. Confirm LICENSE and CITATION.cff exist.
5. Confirm environment file exists and contains verified versions only.
6. Confirm no DOI is claimed until created by the human release process.

## Runtime Honesty

The smoke test should report observed runtime after it is implemented and measured. Until then, documentation should state only that the lightweight smoke test is intended for quick verification and that full production runtime depends on data volume, radial sampling, and surrogate count.
