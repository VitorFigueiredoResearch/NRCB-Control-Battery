# Reproducing the Paper Package

This lightweight package is intended for manuscript and figure/source verification of the NRCB paper-reproduction artifacts.

## Steps

1. Compile the manuscript from `manuscript/` using `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
2. Confirm the three final `_rev1` figure PDFs are present in `figures/`.
3. Confirm compact result files are present in `results/m_surrogate_extension_v1/`.
4. Compare rounded manuscript-facing values against `provenance/FIGURE_VALUE_LEDGER.csv` and the compact summary tables.
5. Review `provenance/RELEASE_FINAL_STATUS.md` and `provenance/SHA256SUMS.txt` for release-facing status and checksums.

## What Is Not Required

Paper reproduction does not require raw SPARC files, `run_sparc_lite.py`, a full production rerun, or `per_realization_controls.csv`.

## Figure Regeneration Note

The final `_rev1` PDFs are fixed manuscript artifacts. The script in `figures/source/` is path-robust within this release layout and writes `_rev1` filenames if run, but figure regeneration is not required for paper reproduction.

## Full Rerun Boundary

Full production preflight is supported by `src/validate_sparc_bootstrap.py`. Users must supply official SPARC files and a compatible source root themselves. Redistribution of raw SPARC/source-derived data requires licensing review.