# Troubleshooting

## Missing TeX

Install a LaTeX distribution before compiling the manuscript. The package does not install TeX.

## Missing Python Packages

Install the pinned runtime dependencies with `pip install -r requirements.txt`; verified version details are in `ENVIRONMENT.md`.

## Missing Figure Files

The manuscript expects the three final `_rev1` PDFs. Restore them from the release package; do not regenerate figures unless performing a dedicated figure-source audit.

## Missing Compact Results

Paper reproduction requires compact CSVs under `results/m_surrogate_extension_v1/`.

## Raw SPARC Not Included

This is expected. Raw SPARC files are not bundled by default. Users must obtain official SPARC files themselves for parameter extraction or full production preflight.

## `run_sparc_lite.py` Missing

For paper reproduction, this is not a problem. For full production preflight, provide a source root containing `vendor/h1_src/run_sparc_lite.py` and the expected SPARC rotation-curve files.

## User-Data Wrappers Not Implemented

Generic user-supplied data wrappers are future implementation items.