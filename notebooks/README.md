# NRCB quickstart notebook

This folder contains `NRCB_quickstart.ipynb`, a lightweight notebook for paper and figure reproduction from the release package.

Scope:

- reproduces headline values from compact CSV tables;
- checks branch sizes and control tiers;
- regenerates figures in notebook-local `_outputs/` folders only;
- runs SPARC bootstrap validator manuscript and figure modes;
- demonstrates full-production fail-closed behavior when external SPARC/source dependencies are absent.

The notebook does not rerun full production, does not require raw SPARC files, does not download data, and does not provide generic user-supplied data support.

Suggested launch locations:

```bash
jupyter notebook notebooks/NRCB_quickstart.ipynb
```

or open the notebook from inside the `notebooks/` folder. The notebook locates the release root from relative paths.
