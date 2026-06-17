# Nisa Radial Control Battery Paper-Reproduction Release Candidate

This release candidate supports paper reproduction for the Astronomy & Computing computational-methods manuscript:

**A Reproducible Control-Validation Workflow for Circular-Shift and Surrogate Tests of Galactic Radial Profiles**

The implemented workflow is referred to here as the Nisa Radial Control Battery (NRCB). The NRCB is a branch-separated suite of shuffle, exact circular-shift, surrogate, and fixed-reference controls for radial-profile diagnostics.

## Release Modes

1. Paper Reproduction Mode: ready. Compile the manuscript, inspect final figure files, and verify compact results and provenance ledgers without rerunning production.
2. Example / Smoke-Test Mode: planned. A small example dataset and wrapper script are future implementation items.
3. User-Supplied Data Mode: planned. Generic user-data wrappers are not implemented in v1.0, and arbitrary data support is not claimed.
4. Full Production Rerun Mode: preflight support is provided by `src/validate_sparc_bootstrap.py`; raw SPARC files and full source dependencies are not bundled.

## Scope

This package documents a computational workflow and compact paper-reproduction artifacts. It does not make physical interpretation claims, does not claim model validation, and does not include raw external data by default.

## Where Things Are

- `manuscript/`: LaTeX manuscript source and bibliography.
- `figures/`: final figure PDFs.
- `figures/source/`: figure-generation script and figure metadata.
- `results/`: compact QC-accepted result files.
- `provenance/`: selected reproducibility records, final release status, and checksums.
- `src/`: paper-pipeline scripts and SPARC bootstrap validator.
- `data/`: data-policy placeholders and future example/user-data folders.

## SPARC and Full-Rerun Dependency Boundary

Paper reproduction does not require raw SPARC files or `run_sparc_lite.py`. Full production preflight requires a user-supplied source root containing official SPARC rotation-curve files and `vendor/h1_src/run_sparc_lite.py`. Inclusion of that vendor/source file in a future full-rerun bundle requires licensing and provenance review, especially if it contains SPARC-derived embedded parameter records.

## Citation

Citation metadata is in `CITATION.cff`. Please cite:

- the **manuscript** for the method (NRCB workflow and its definitions);
- the **archived software release** for the implementation.

Final DOI metadata (repository URL and Zenodo DOI) will be added to
`CITATION.cff` after archival deposit; they are intentionally omitted until
real values exist.

## License

This release uses a component-based dual licence (see `LICENSE.md` and the
full texts in `LICENSES/`):

- **Software** (`src/`, `figures/source/`): `GPL-3.0-only`.
- **Manuscript, documentation, original figures, provenance, and compact
  derived results**: `CC-BY-4.0`.
- **Raw SPARC data**: not distributed and not licensed by this repository
  (see `DATA_AVAILABILITY.md`).

Authorship and copyright: see `AUTHORS.md` (Copyright (C) 2026 Vitor M. F.
Figueiredo).