# SPARC Bootstrap Validator Implementation Report

## 1. Implementation Executive Status

Implemented `src/validate_sparc_bootstrap.py` as a fail-closed SPARC/bootstrap preflight validator for manuscript reproduction, figure reproduction, parameter extraction, test mode, and full production support.

Classification: `SPARC_VALIDATOR_IMPLEMENTATION_PASS_READY_FOR_RELEASE_REBUILD`.

## 2. Files Read

- `notes/SPARC_DATA_DEPENDENCY_AUDIT.md`
- `notes/SPARC_DATA_DEPENDENCY_MATRIX.csv`
- `notes/SPARC_BOOTSTRAP_VALIDATOR_DESIGN.md`
- `notes/SPARC_DOWNLOAD_GUIDE_OUTLINE.md`
- `notes/SPARC_PREFLIGHT_ERROR_CATALOG.csv`
- `src/run_m_surrogate_extension.py`
- SPARC extractor scripts in the local source repository, read-only
- Vendor/source files in the local source repository, read-only
- Release-candidate docs directory, for allowed validator README placement

## 3. Files Created or Modified

Created or modified only allowed outputs:

- `src/validate_sparc_bootstrap.py`
- `release_candidate/docs/SPARC_BOOTSTRAP_VALIDATOR_README.md`
- `notes/SPARC_BOOTSTRAP_VALIDATOR_IMPLEMENTATION_REPORT.md`
- `notes/SPARC_BOOTSTRAP_VALIDATOR_IMPLEMENTATION_CHECKS.csv`
- `notes/SPARC_BOOTSTRAP_VALIDATOR_TEST_SUMMARY.md`
- `notes/bootstrap_validation_test_outputs/*`

No manuscript, figure, compact-result, production-output, raw-data, or bibliography files were modified.

## 4. Validator CLI

Implemented CLI arguments:

```text
--mode {manuscript-reproduction,figure-reproduction,parameter-extraction,test-mode,full-production}
--project-root PATH
--source-root PATH
--sparc-extractor-root PATH
--release-root PATH
--output-dir PATH
--json
--strict
--allow-one-galaxy-dry-run
```

Explicit roots are preferred. If safe default discovery is used, the validator emits a warning recommending explicit roots.

## 5. Implemented Mode Checks

The validator writes human-readable Markdown, checks CSV, file inventory CSV, and optional JSON when `--output-dir` is provided. Without `--output-dir`, it prints a concise terminal summary and creates no files.

The checks schema and file-inventory schema match the task requirements.

## 6. Parameter-Extraction Validation

Implemented checks for:

- canonical lowercase `RAW/table1.mrt`;
- table1 readability, nonzero size, parser-candidate count, duplicate normalized names, and numeric field parse;
- optional `Bulges.mrt`, `wise_ii table1.mrt`, `RAW/rotmod/`, and `rotmod*.zip` status;
- `table2.mrt` as not required by the current extractor;
- existing extractor JSON extension-case fragility.

The validator does not run extraction.

## 7. Test-Mode Validation

Implemented checks for:

- required project contract/provenance files;
- branch attrition counts and spectral-subset relation;
- deterministic test selection as the first two sorted spectral-valid galaxies;
- source root, `data/sparc`, frozen parameter source, gravity constant source, reconstruction adapter marker discovery, and Python dependency availability;
- selected test rotmod file presence and finite radius/velocity row quality.

The validator does not run test-mode production.

## 8. Full-Production Validation

Implemented checks for:

- all common project/source checks;
- vendor parameter coverage for all 134 partial-branch galaxies;
- rotmod presence and parse quality for all 134 partial-branch galaxies;
- spectral N=76 subset coverage;
- production engine reconciliation/zero-row guard marker scan;
- optional one-galaxy dry-run flag, currently reported as `SKIP` because no safe standalone dry-run interface is implemented in the validator.

The validator does not run full production.

## 9. Figure-Reproduction Validation

Implemented checks for:

- figure-generation script presence;
- compact QC-accepted summary files;
- `figure2_source_data.csv` for provenance;
- three final revised figure PDFs;
- large realization table explicitly not required.

The validator does not regenerate figures.

## 10. Manuscript-Reproduction Validation

Implemented checks for:

- `manuscript/main.tex`;
- active `\input{...}` and `\include{...}` section references;
- `manuscript/references.bib`;
- active `\includegraphics{...}` figure references;
- raw SPARC/source tree explicitly not required for compile-only reproduction;
- optional strict isolated `pdflatex` run in a temporary output directory only when `--strict` is provided.

No LaTeX build artifacts are left by normal validation.

## 11. Error Handling and Fail-Closed Policy

The validator uses the SPARC preflight error catalog as the basis for specific remediation messages where applicable.

Missing raw SPARC files do not block manuscript-only or compact paper reproduction modes. Missing `table1.mrt` blocks parameter extraction. Missing source-root or selected rotmod files blocks test/full production modes. Optional fallback files produce warnings, not hard failures.

## 12. Public Documentation

Created `release_candidate/docs/SPARC_BOOTSTRAP_VALIDATOR_README.md` because the release-candidate docs directory exists. The paper-root `docs/` directory is absent, so no root docs file was created.

The public README uses placeholders only and does not include private absolute paths. It states that raw SPARC files are not bundled by default, users must obtain official source files themselves, redistribution requires licensing review, and paper reproduction does not require raw SPARC.

## 13. Local Test Results

Positive validation runs completed with exit code 0:

- manuscript reproduction;
- figure reproduction;
- parameter extraction;
- test mode;
- full production preflight.

All positive-mode machine-readable summaries reported `PASS`.

## 14. Negative Test Results

Negative validation runs failed closed as intended:

- missing parameter-extraction table path: exit code 1, blocking `SPARC001_TABLE1_MISSING`;
- missing source-root path for full-production: exit code 1, blocking source, vendor, gravity, adapter, and rotmod checks.

No real data were modified.

## 15. Release-Candidate Impact

The validator README was added to the release-candidate docs directory. No release scientific files, manuscript files, compact results, figures, or production outputs were changed.

A future release rebuild can include the validator script and documentation as part of the paper-reproduction support layer.

## 16. Remaining Risks

- Raw SPARC redistribution/licensing remains a human review item.
- The optional one-galaxy reconstruction dry-run is intentionally not implemented until a safe standalone dry-run interface exists.
- Strict LaTeX compile is available only when invoked with `--strict` and when local TeX tooling exists.

## 17. What This Implementation Allows

This implementation allows users to preflight local SPARC/source dependencies by mode before attempting parameter extraction, test-mode checks, or a full production rerun.

It also allows lightweight paper-reproduction validation without raw SPARC data or the large realization table.

## 18. What This Implementation Does Not Allow

This implementation does not download, redistribute, or license SPARC data. It does not rerun production, regenerate figures, modify results, or authorize scientific claims.

It does not implement generic user-supplied data support.

## 19. Required Next Step

Recommended next task: `RELEASE_CANDIDATE_SURGICAL_FIX_AND_REBUILD`.

## 20. Final Status

SPARC bootstrap validator implementation completed with local positive and negative tests passing. Ready for release rebuild.
