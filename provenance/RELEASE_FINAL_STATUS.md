# Release Final Status

## Current Release Status

This release candidate is the current compact paper-reproduction package for the Nisa Radial Control Battery (NRCB) manuscript.

## Included Release-Facing Artifacts

The release-facing computational artifacts are the compact, QC-accepted summary files under:

```text
results/m_surrogate_extension_v1/
```

These compact summaries are the artifacts used for paper reproduction, figure/value verification, and manuscript-facing numerical traceability.

## Large Realization Table

The full production realization table `per_realization_controls.csv` is not included in this lightweight release candidate. It is an optional large artifact for deep streaming QC or derived-summary regeneration.

## Historical Manifest Interpretation

Historical production manifests are preserved as provenance. Some manifest status or checksum fields may reflect pre-patch production accounting. The release-facing compact summaries are the post-patch artifacts documented by the patch and QC provenance files.

## Release Repair Boundary

No production rerun was performed during this release repair. No figures were regenerated during this release repair. No raw SPARC files were bundled. No physical interpretation or model-validation claim is introduced by this release status note.

## Full-Rerun Boundary

Paper reproduction does not require raw SPARC data or `run_sparc_lite.py`. Full production preflight requires user-supplied official SPARC files and a compatible source root, as checked by `src/validate_sparc_bootstrap.py`.
