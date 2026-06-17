# Release Build Report

## Executive Status

Release candidate surgically rebuilt in place after a timestamped copy backup. The package now includes the NRCB naming layer, SPARC bootstrap validator support, cleaned bibliography metadata, repaired release documentation, final release status, and checksum provenance.

Classification: RELEASE_SURGICAL_FIX_PASS_WITH_MINOR_WARNINGS.

## Release Folder

- Folder: release_candidate/
- Existing folder handling: timestamped copy backup was created before in-place rebuild because moving the existing folder was blocked by a locked placeholder directory.
- Raw SPARC files included: NO.
- Large realization table included: NO.

## Smoke Checks

- Manuscript compile status: PASS.
- Active cited keys: 14.
- Python syntax check status: PASS.
- Compact CSV parse status: PASS.
- Private path scan hits: 0.
- Internal term scan hits: 0.
- Excluded-file hits: 0.
- Overfull hbox warnings from compile log: 3.

## Figure Script

The release-copy figure-generation script discovers the release root by locating `results/m_surrogate_extension_v1/` and writes `_rev1` figure filenames if run. Figure regeneration was not performed during this surgical fix.


## SPARC Validator

The release includes src/validate_sparc_bootstrap.py and docs/SPARC_BOOTSTRAP_VALIDATOR_README.md. Paper reproduction does not require raw SPARC files. Full production preflight requires user-supplied official SPARC files and source dependencies.

## Final Status

Ready for master release reaudit, with minor warnings limited to release-folder lock fallback, unexecuted figure regeneration, and nonblocking layout warnings.

