# User Manual Outline

## README.md

- Project name and one-paragraph scope.
- Three user modes: paper reproduction, example smoke test, user-supplied data.
- What is included and excluded.
- Citation instructions.
- License and data-availability pointers.
- No physical-interpretation or model-validation claim.

## QUICKSTART.md

- Environment setup.
- Compile manuscript.
- Verify final figures.
- Run lightweight release integrity checks once implemented.
- Where compact results and provenance live.

## REPRODUCING_PAPER.md

- Manuscript compile sequence.
- Figure files and figure-generation script.
- Compact result files required.
- Ledger/value consistency checks.
- Explanation that large realization table is optional for deep audit only.

## USER_DATA_FORMAT.md

- Required columns.
- Optional columns.
- Units.
- Grouping.
- Finite-value and radius rules.
- Branch eligibility.
- Example valid and invalid rows.

## RUNNING_ON_YOUR_DATA.md

- Current status statement: future wrapper required unless implemented.
- Folder layout for user CSVs.
- Validation command.
- Diagnostic command.
- Output interpretation boundaries.
- Common failure modes.

## TROUBLESHOOTING.md

- Missing dependencies.
- LaTeX/BibTeX issues.
- Missing compact results.
- Missing external data for production rerun.
- User CSV schema errors.
- Invalid rows and branch ineligibility.
- Large artifact handling.

## DATA_AVAILABILITY.md

- Public repository, Zenodo version DOI, concept DOI, and citation metadata.
- Official external SPARC source pointer and citation requirement.
- Optional large artifact retrieval instructions.
- Statement that raw/external data redistribution depends on license review.

## ENVIRONMENT_LOCK.md or environment file

- Python version.
- Package versions.
- LaTeX engine and BibTeX requirements.
- Operating-system notes.
- Commit or release tag.

## EXAMPLE_DATA_README.md

- Whether example data are synthetic or externally sourced.
- Exact schema.
- Expected smoke-test outputs.
- No scientific interpretation of example outputs.
