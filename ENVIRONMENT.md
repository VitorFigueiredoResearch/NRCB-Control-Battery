# Environment Record

Versions below were queried directly from the tested release environment.
No versions are invented and no local paths are recorded.

## Runtime

| Component | Verified version |
|---|---|
| Python | 3.12.7 |
| NumPy | 1.26.4 |
| Matplotlib | 3.9.2 |

NumPy is required by the core workflow; Matplotlib is required only for
figure generation. SciPy is present in the development environment but is
**not imported** by any included script and is therefore not a dependency
(see `requirements.txt`).

## Manuscript build

| Component | Verified version |
|---|---|
| pdfTeX engine | MiKTeX-pdfTeX 4.24 (MiKTeX 26.1) |
| BibTeX | MiKTeX-BibTeX 4.2 (MiKTeX 26.1) |
| Bibliography style | `elsarticle-harv` |

## Platform and provenance

- Operating system used for the tested release: Windows 10.
- Tested code commit identifier: `c8a6c950bd9e` (as recorded in
  `manuscript/sections/reproducibility.tex` and the production provenance).

## Notes

- `pip install -r requirements.txt` installs the minimal runtime
  dependencies.
- A complete machine-generated lock is intentionally avoided to exclude
  unrelated/private environment packages.
