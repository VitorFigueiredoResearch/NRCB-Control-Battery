# Quickstart

## 1. Environment

Minimal runtime dependencies are pinned in `requirements.txt`; full
verified version details are in `ENVIRONMENT.md`.

```bash
pip install -r requirements.txt
```

Verified environment facts:

- Python 3.12.7.
- NumPy 1.26.4.
- Matplotlib 3.9.2 (figure generation only)
- Code commit `c8a6c950bd9e`.

## 2. Compile the manuscript

From `release_candidate/manuscript/`:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## 3. Check figures and compact results

Final figure PDFs live in `figures/` and are also copied into `manuscript/figures/` for convenience.

Compact result files live in `results/m_surrogate_extension_v1/`.

## 4. SPARC bootstrap preflight

### Paper-reproduction preflight

Paper and figure reproduction do not require raw SPARC data. These modes
check that the bundled package is internally sufficient:

```bash
python src/validate_sparc_bootstrap.py --mode manuscript-reproduction --project-root .
python src/validate_sparc_bootstrap.py --mode figure-reproduction --project-root .
```

### External SPARC dependency preflight

Parameter extraction and full production are **not** supported by the
lightweight package alone; they require user-supplied SPARC source files
and additional source dependencies that are not bundled. These modes check
local availability and fail closed (with clear messages) when those
dependencies are absent, while paper reproduction remains available:

```bash
python src/validate_sparc_bootstrap.py --mode parameter-extraction --project-root . --sparc-extractor-root <your-sparc-root>
python src/validate_sparc_bootstrap.py --mode full-production --project-root . --source-root <your-source-root>
```

## 5. No production rerun required

The lightweight paper-reproduction path does not require raw external data, a full production run, or the large realization table.