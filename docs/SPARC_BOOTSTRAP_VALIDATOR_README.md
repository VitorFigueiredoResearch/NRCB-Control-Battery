# SPARC Bootstrap Validator README

`src/validate_sparc_bootstrap.py` checks whether local files are present for the official SPARC dependency pathway used by NRCB paper reproduction and full-rerun support.

The validator does not download SPARC files, redistribute SPARC files, rerun production, regenerate figures, or modify manuscript/results files.

## Data Boundary

Raw SPARC files are not bundled by default. Users who want parameter extraction or full production preflight must obtain official SPARC source files themselves.

Redistribution of raw SPARC files or SPARC-derived artifacts requires human licensing review. The validator checks local availability only and does not imply redistribution permission.

## Modes

```bash
python src/validate_sparc_bootstrap.py --mode manuscript-reproduction --project-root <project-root>
python src/validate_sparc_bootstrap.py --mode figure-reproduction --project-root <project-root>
python src/validate_sparc_bootstrap.py --mode parameter-extraction --project-root <project-root> --sparc-extractor-root <sparc-extractor-root>
python src/validate_sparc_bootstrap.py --mode test-mode --project-root <project-root> --source-root <source-root>
python src/validate_sparc_bootstrap.py --mode full-production --project-root <project-root> --source-root <source-root>
```

## `run_sparc_lite.py` Policy

For paper reproduction, `run_sparc_lite.py` is not required.

For validator full-production preflight, the user must supply a source root containing `vendor/h1_src/run_sparc_lite.py` and the expected SPARC rotation-curve files.

For any future full-rerun bundle, inclusion of `run_sparc_lite.py` requires licensing/provenance review, especially if it contains SPARC-derived embedded galaxy parameter records.

## Outputs

When `--output-dir <path>` is provided, the validator writes Markdown, checks CSV, file inventory CSV, and optional JSON. Without `--output-dir`, it prints a concise terminal summary and creates no files.

## Non-Claims

The validator is a file/provenance preflight. It does not certify scientific interpretation, model validation, or physical conclusions.