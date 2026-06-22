# Data Availability

## Raw SPARC data

Raw SPARC rotation-curve tables and mass-model files are **not
redistributed** in this release and are **not covered by this repository's
licence grant**. Users must obtain them from the official SPARC sources
under the applicable third-party terms.

- Official SPARC source URL/DOI: Official SPARC database:
https://astroweb.case.edu/SPARC/

Data reference:
Lelli, F., McGaugh, S. S., & Schombert, J. M. (2016),
The Astronomical Journal, 152, 157.
https://doi.org/10.3847/0004-6256/152/6/157

## Repository and archived release

Public repository:
https://github.com/VitorFigueiredoResearch/NRCB-Control-Battery

Version-specific archived release DOI:
https://doi.org/10.5281/zenodo.20726321

Concept DOI for all versions:
https://doi.org/10.5281/zenodo.20726320

Citation metadata:
https://github.com/VitorFigueiredoResearch/NRCB-Control-Battery/blob/main/CITATION.cff

## What is included for reproduction

- **Paper and figure reproduction** use the compact derived summary files
  in `results/m_surrogate_extension_v1/` (per-galaxy and global control
  summaries, figure source data, run manifest, warnings, execution
  report). These are sufficient to compile the manuscript and regenerate
  the figures without raw SPARC data.
- The **full per-realization table** (`per_realization_controls.csv`) is
  **not included** in this lightweight release. It is needed only for deep
  streaming QC or derived-summary regeneration (see
  `large_artifacts_optional/README.md`).

## Optional full-production pathway

Re-running the full production pipeline (beyond paper/figure reproduction)
requires **external SPARC source files and additional source
dependencies** that are not bundled here. The preflight validator
(`src/validate_sparc_bootstrap.py`) checks local availability and fails
closed with clear messages when those dependencies are absent, while paper
and figure reproduction remain available.

## Rights in underlying materials

This repository grants no rights in third-party or SPARC-derived
underlying materials. Redistribution of raw SPARC files or SPARC-derived
artifacts requires separate licensing review and is not authorized here.
