# M-Surrogate Production QC Rerun

## 1. Executive Verdict

The patched production outputs pass the production-QC rerun with nonblocking warnings. The previous empirical-summary blocker is fixed: every non-empty empirical percentile and p-value is bounded within `[0,1]`, while the production realization file remains byte-for-byte unchanged.

QC classification: `PRODUCTION_QC_RERUN_PASS_WITH_WARNINGS_TERMINOLOGY_UPGRADE_ELIGIBLE`.

## 2. Files Audited

- `notes/M_SURROGATE_PATCH_REPORT.md`
- `notes/M_SURROGATE_PRODUCTION_QC.md`
- `notes/M_SURROGATE_PRODUCTION_QC_CHECKS.csv`
- `notes/M_SURROGATE_PRODUCTION_RUN_OPERATOR_REPORT.md`
- all listed production outputs and console log
- `src/patch_production_summaries.py`
- all listed reference contracts and prior audits
- `notes/temp_qc_streaming_audit_rerun.py`

## 3. Patch Report Audit

PASS. The patch report contains all required declarations: the summary patch completed, production was not rerun, the main empirical math and report generator were fixed, the patch script and backup were created, the realization file remained read-only with unchanged checksum and size, derived summaries were regenerated, empirical-bound failures were eliminated, invalid rows remain accounted, and terminology upgrade remained unauthorized pending this rerun.

## 4. Realization File Protection Audit

PASS. Chunked hashing and file metadata confirm:

- size: `130239638` bytes, matching the patch report;
- SHA256: `793197491D901E7C24DCBACDE348CD540FAC1286799E2D6E85B61AD4E2745820`, matching the patch report;
- production console timestamp remains `2026-06-13T01:40:13.9659885Z`;
- realization timestamp remains `2026-06-13T01:40:11.6144091Z`.

Production was not rerun, and the realization file was not modified by the patch or this QC rerun.

## 5. Empirical Bounds Audit

PASS. Across `per_galaxy_null_summary.csv`:

- non-empty empirical percentiles: 688;
- percentile minimum: `0`;
- percentile maximum: `1`;
- percentiles outside `[0,1]`: `0`;
- non-empty empirical p-values: 688;
- p-value minimum: `0.000999000999000999`;
- p-value maximum: `1`;
- p-values outside `[0,1]`: `0`;
- negative p-values: `0`;
- percentiles above 1: `0`.

All 228 fixed-reference summaries retain empty percentile and p-value fields.

## 6. Random-Phase Spectral Rerun Audit

PASS WITH EXPECTED CAVEAT.

- Residual random-phase tier: 76 galaxies x 1,000 realization rows.
- Radial-template random-phase tier: 76 galaxies x 1,000 realization rows.
- All 152 random-phase summary rows have bounded empirical values.
- All 152 retain `DEGENERATE_PHASE_BLIND_STATISTIC`.
- No random-phase summary has an out-of-range percentile or p-value.

Random-phase equality for spectral concentration can be by construction because spectral concentration depends on preserved spectral amplitudes. This is a statistical caveat, not physical evidence.

## 7. Invalid Row Audit

PASS WITH WARNING. The same two invalid realization rows remain retained and explained:

1. `galaxy_id=G0101`; `canonical_galaxy_name=UGC05918`; `sample_branch=partial_rank_134`; `control_tier=shuffle_surrogate_partial_rank`; `realization_type=shuffle_surrogate`; `iteration=190`; `statistic_name=partial_rank`; `invalid_reason=NONFINITE_PARTIAL_RANK`; notes: `Frozen mask; only normalized radial covariate permuted`.
2. `galaxy_id=G0101`; `canonical_galaxy_name=UGC05918`; `sample_branch=partial_rank_134`; `control_tier=shuffle_surrogate_partial_rank_absolute`; `realization_type=shuffle_surrogate`; `iteration=190`; `statistic_name=absolute_partial_rank`; `invalid_reason=NONFINITE_PARTIAL_RANK`; notes: `Frozen mask; only normalized radial covariate permuted; Derived absolute statistic shares the seed of the signed surrogate realization.`

The corresponding summaries remain 1,000 emitted and 999 valid for both tiers. No invalid row was silently dropped.

## 8. Summary File Audit

PASS.

- `per_galaxy_null_summary.csv`: 916 rows.
- `global_control_battery_summary.csv`: 9 rows.
- `figure2_source_data.csv`: 3,436 rows.
- All schemas exactly match the frozen design.
- Observed absolute partial-rank and residual spectral-concentration medians match locked values using `rel_tol=1e-6, abs_tol=1e-8`.
- Fixed references remain non-stochastic.
- Global summaries remain explicitly descriptive and are not pooled empirical tests.

## 9. Manifest Audit with Patch-Aware Checksum Rule

PASS WITH EXPECTED PATCH WARNING. The intentionally pre-patch manifest contains nine numeric tier rows, correct selected/emitted sample scopes, reconciled valid/invalid counts, and `PRODUCTION_COMPLETED_QC_PENDING` status.

Its output checksums differ from current bytes only for:

- `per_galaxy_null_summary.csv`;
- `global_control_battery_summary.csv`;
- `execution_report.md`.

These mismatches are classified `EXPECTED_PATCH_WARNING` because the patch report documents their regeneration, the realization checksum is unchanged, the patched summaries pass schemas and bounds, and the execution report documents the patch. `figure2_source_data.csv` was regenerated but remained byte-identical, so its checksum still matches.

## 10. Warning Audit

PASS WITH WARNINGS. `implementation_warnings.csv` remains unchanged and contains 152 informational phase-blind-statistic notices and zero error rows. The notices are expected and nonblocking.

## 11. Language Lock Audit

PASS. `execution_report.md` contains:

`Production outputs have been generated. A separate production-output QC is required before manuscript use or terminology upgrade.`

The stale test-mode-before-production sentence is absent. The report also records that realization rows were not regenerated or modified and retains:

- manuscript edited: NO;
- physical interpretation emitted: NO;
- unsupported result statement emitted: NO;
- production terminology upgrade authorized: NO, QC_REQUIRED.

This rerun report does not edit or directly authorize manuscript prose. It establishes limited eligibility for carefully qualified future terminology.

## 12. Figure Source Audit

PASS. `figure2_source_data.csv` contains 3,436 branch-labelled rows and is approximately 0.475% of the realization-file size. It separates `partial_rank_controls` / `partial_rank_134` from `spectral_controls` / `spectral_control_76`. It contains no physical interpretation or manuscript conclusion.

## 13. Circular-Shift Exactness Audit

PASS. Streaming audit of 268 galaxy/tier groups found:

- every offset set equals exactly `1..n_valid_radii-1`;
- no offset 0;
- no duplicate offset;
- no conflicting `n_valid_radii`;
- zero group failures.

All 268 circular-shift summary rows use `FINITE_EXACT_SHIFT`, contain empirical p-values, and contain no `TEST_SUBSET_NOT_EXACT` labels.

## 14. Seed and Determinism Audit

PASS WITH WARNING.

- SHA256 deterministic seed logic remains present.
- Python's built-in `hash()` is not used.
- Streaming audit found 420,000 unique randomized seed tuples.
- Missing seeds: 0.
- Duplicate seed tuples: 0.
- Seed-formula mismatches: 0.
- Missing absolute-statistic lineage notes: 0.

Independent two-run checksum evidence remains `PENDING_MANUAL`; this is nonblocking.

## 15. QC Memory-Safety Audit

PASS. This QC rerun used `notes/temp_qc_streaming_audit_rerun.py` for realization-row auditing. The helper streams with Python's `csv` module, retains only compact counters/sets and two invalid-row records, and computes SHA256 in 1 MiB chunks.

No pandas full load, `Path.read_bytes()`, `read_text()`, or `list(csv.DictReader(...))` was used on the realization CSV during this rerun.

## 16. Production QC Rerun Classification

`PRODUCTION_QC_RERUN_PASS_WITH_WARNINGS_TERMINOLOGY_UPGRADE_ELIGIBLE`

The previous empirical-bound blockers are corrected. Remaining findings are nonblocking: expected pre-patch manifest checksum drift, phase-blind notices, two explained retained invalid rows, and pending independent two-run determinism evidence.

## 17. What This QC Allows

- Production outputs are QC-accepted for computational use.
- Future manuscript drafting may use carefully qualified control/surrogate-distribution terminology.
- Exhaustive circular-shift groups may be described as exact circular-shift randomization distributions.
- Random-phase spectral distributions must carry the phase-blind/by-construction caveat.
- A separate figure-generation task may begin.
- Citation lock should proceed before Methods/Demonstration prose.

## 18. What This QC Does Not Allow

- This QC does not directly edit or authorize specific manuscript prose.
- This QC does not authorize physical interpretation.
- This QC does not authorize model-validation, discovery, model-comparison, field-correction, or final-conclusion claims.
- Random-phase equality must not be presented as physical evidence.
- Methods/Demonstration drafting should wait until figure-source and citation-lock tasks are aligned.

## 19. Required Next Step

`FIGURE_SOURCE_GENERATION_AND_CITATION_LOCK`

Generate figures in a separate task using the branch-labelled source data and lock the required citations before beginning Methods/Demonstration drafting.

## 20. Final Status

* M-surrogate production QC rerun completed? YES
* Production rerun attempted? NO
* Large realization CSV fully loaded into memory during QC rerun? NO
* Streaming QC helper script created? YES
* Patch report passed? YES
* Realization checksum unchanged? YES
* Realization size unchanged? YES
* Empirical bounds passed? YES
* Negative p-values eliminated? YES
* Percentiles above 1 eliminated? YES
* Random-phase spectral audit passed? YES
* Invalid rows retained and explained? YES
* Summary files passed? YES
* Manifest patch-aware audit passed? YES
* Warning audit passed? YES
* Language lock passed? YES
* Figure source audit passed? YES
* Circular-shift exactness passed? YES
* Seed and determinism audit passed? YES
* QC memory-safety passed? YES
* Manifest derived-output checksum mismatch treated as expected patch warning? YES
* Stale wording eliminated? YES
* Manuscript edited? NO
* Physical interpretation emitted? NO
* Unsupported result statement emitted? NO
* Production terminology upgrade eligible? YES
* Control/surrogate-distribution wording authorized for future drafting? LIMITED
* Number of failures = 0
* Number of warnings = 4
* QC classification = PRODUCTION_QC_RERUN_PASS_WITH_WARNINGS_TERMINOLOGY_UPGRADE_ELIGIBLE
* Ready for figure-generation task? YES
* Ready for citation-lock task? YES
* Ready for Methods/Demonstration drafting? NO
* Recommended next task = FIGURE_SOURCE_GENERATION_AND_CITATION_LOCK
