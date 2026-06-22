# Nisa Radial Control Battery (NRCB)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20726320.svg)](https://doi.org/10.5281/zenodo.20726320)
[![GitHub release](https://img.shields.io/github/v/release/VitorFigueiredoResearch/NRCB-Control-Battery)](https://github.com/VitorFigueiredoResearch/NRCB-Control-Battery/releases)
[![Code License: GPL-3.0-only](https://img.shields.io/badge/code%20license-GPL--3.0--only-blue.svg)](LICENSE.md)
[![Docs License: CC BY 4.0](https://img.shields.io/badge/docs%20license-CC%20BY%204.0-lightgrey.svg)](LICENSE.md)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--7358--4622-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0004-7358-4622)

This release package supports paper reproduction for the Astronomy & Computing computational-methods manuscript:

**A Reproducible Control-Validation Workflow for Circular-Shift and Surrogate Tests of Galactic Radial Profiles**

The implemented workflow is referred to here as the Nisa Radial Control Battery (NRCB). The NRCB is a branch-separated suite of shuffle, exact circular-shift, surrogate, and fixed-reference controls for radial-profile diagnostics.

## Name

The name Nisa Radial Control Battery reflects the author's research base in Nisa, Portugal, and the workflow's role as a controlled battery of radial-profile validation tests.

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
- `data/`: data-policy documentation and future example/user-data folders.

## SPARC and Full-Rerun Dependency Boundary

Paper reproduction does not require raw SPARC files or `run_sparc_lite.py`. Full production preflight requires a user-supplied source root containing official SPARC rotation-curve files and `vendor/h1_src/run_sparc_lite.py`. Inclusion of that vendor/source file in a future full-rerun bundle requires licensing and provenance review, especially if it contains SPARC-derived embedded parameter records.

## Citation

Version-specific citation for the exact archived package used:

Figueiredo, V. M. F. (2026). Nisa Radial Control Battery (v1.0.1). Zenodo. https://doi.org/10.5281/zenodo.20726321

Concept DOI for all versions:

https://doi.org/10.5281/zenodo.20726320

Repository:

https://github.com/VitorFigueiredoResearch/NRCB-Control-Battery

Citation metadata:

https://github.com/VitorFigueiredoResearch/NRCB-Control-Battery/blob/main/CITATION.cff

Cite the version DOI for the exact archived package used. Cite the concept DOI when referring to the project across all versions.

Author ORCID: https://orcid.org/0009-0004-7358-4622

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
