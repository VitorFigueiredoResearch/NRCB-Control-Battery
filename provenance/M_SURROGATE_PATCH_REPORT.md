# M-Surrogate Production Summary Patch Report

## 1. Patch Executive Status

The surgical production summary patch completed successfully. Production was not rerun. Existing production realization rows were streamed read-only, and only the authorized derived summaries and execution report were regenerated.

Production terminology upgrade remains unauthorized until a production-QC rerun passes.

## 2. Bug Identified

The previous empirical mid-rank calculation allowed approximate-tie controls to overlap with the less-than count. In near-degenerate random-phase groups, the overlap produced empirical percentiles above 1 and negative doubled equal-tail p-values.

## 3. Main Script Modification

`src/run_m_surrogate_extension.py` now:

- partitions controls into disjoint less-than, approximate-tie, and greater-than counts using `tol = 1e-12`;
- verifies that the three counts equal the valid realization count;
- clamps empirical percentiles and p-values to `[0,1]` only as a final numerical guard;
- applies the requested tolerance to random-tier and exact circular-shift two-sided p-values;
- preserves degenerate phase-blind and fixed-reference statuses;
- generates production-appropriate remaining-requirement wording.

## 4. Patch Script Created

Created `src/patch_production_summaries.py`.

The script streams `per_realization_controls.csv`, retains only memory-conscious per-galaxy/tier numeric aggregates, preserves observed statistics from the pre-patch summary, validates empirical bounds, and atomically replaces authorized derived files.

## 5. Files Backed Up

Copied, not moved, the four pre-patch derived files to:

`results/m_surrogate_extension_v1_summary_patch_backup_20260613_032640/`

Backed-up files:

- `per_galaxy_null_summary.csv`
- `global_control_battery_summary.csv`
- `figure2_source_data.csv`
- `execution_report.md`

All backup hashes matched their source files before patch execution.

## 6. Realization File Protection

Protected file: `results/m_surrogate_extension_v1/per_realization_controls.csv`

- Pre-patch size: `130239638` bytes
- Post-patch size: `130239638` bytes
- Pre-patch SHA256: `793197491D901E7C24DCBACDE348CD540FAC1286799E2D6E85B61AD4E2745820`
- Post-patch SHA256: `793197491D901E7C24DCBACDE348CD540FAC1286799E2D6E85B61AD4E2745820`

The realization file was opened read-only only and was not modified.

## 7. Summary Files Regenerated

Regenerated from existing production realization rows:

- `per_galaxy_null_summary.csv`: 916 rows
- `global_control_battery_summary.csv`: 9 rows
- `figure2_source_data.csv`: 3436 rows
- `execution_report.md`: stale wording corrected and patch note added

All regenerated CSV schemas exactly match the frozen schemas. Existing observed-statistic strings were preserved. Frozen headline and fixed-reference values remain within `rel_tol=1e-6, abs_tol=1e-8` of their locked values.

`extension_run_manifest.csv` and `implementation_warnings.csv` were intentionally not modified. The manifest therefore retains its original pre-patch derived-output checksums and must be treated as a pre-patch production manifest during the production-QC rerun.

## 8. Empirical Statistic Bounds Check

Post-patch validation found:

- negative empirical p-values: `0`;
- empirical percentiles above 1: `0`;
- non-empty empirical percentiles outside `[0,1]`: `0`;
- non-empty empirical p-values outside `[0,1]`: `0`;
- fixed-reference rows with non-empty percentile or p-value: `0`.

The previously invalid random-phase summaries now use bounded degenerate-summary values. `DEGENERATE_PHASE_BLIND_STATISTIC` remains preserved where appropriate.

## 9. Invalid Row Accounting

The two retained invalid production realization rows remain accounted for in derived summaries:

- `UGC05918`, signed shuffle tier: 1000 emitted, 999 valid;
- `UGC05918`, absolute shuffle tier: 1000 emitted, 999 valid.

No invalid realization was silently dropped.

## 10. Stale Wording Fix

The production execution report now states:

`Production outputs have been generated. A separate production-output QC is required before manuscript use or terminology upgrade.`

It also records that derived summaries were corrected after production QC and that realization rows were not regenerated or modified.

## 11. Memory Safety

The patch script streamed the realization CSV using Python's `csv` module. It did not use pandas and did not load all realization rows as dictionaries into memory. Per-galaxy/tier numeric aggregates were retained as permitted by the patch contract.

No production process or surrogate-generation process was executed.

## 12. What This Patch Allows

This patch allows a production-QC rerun of the corrected derived summaries and unchanged realization rows.

## 13. What This Patch Does Not Allow

- This patch does not authorize manuscript terminology upgrades.
- This patch does not authorize manuscript edits.
- This patch does not authorize figure generation.
- This patch does not perform physical interpretation.
- This patch does not emit an unsupported result statement.
- This patch does not itself accept production outputs for manuscript use.

## 14. Required Next Step

`M_SURROGATE_PRODUCTION_QC_RERUN`

The QC rerun must verify corrected empirical bounds, unchanged realization checksum and size, retained invalid-row accounting, the intentionally unchanged pre-patch manifest, and the corrected report wording.

## 15. Final Status

* Surgical production summary patch completed? YES
* Production rerun attempted? NO
* Main script empirical math fixed? YES
* Stale report wording generator fixed? YES
* Patch script created? YES
* Patch script executed? YES
* Derived summary backup created? YES
* per_realization_controls.csv opened read-only only? YES
* per_realization_controls.csv checksum unchanged? YES
* per_realization_controls.csv size unchanged? YES
* per_galaxy_null_summary.csv regenerated? YES
* global_control_battery_summary.csv regenerated? YES
* figure2_source_data.csv regenerated? YES
* execution_report.md stale wording fixed? YES
* Negative p-values eliminated? YES
* Percentiles above 1 eliminated? YES
* All non-empty empirical percentiles within [0,1]? YES
* All non-empty empirical p-values within [0,1]? YES
* Invalid realization rows retained/accounted? YES
* Large realization CSV fully loaded into memory? NO
* Manuscript edited? NO
* Physical interpretation emitted? NO
* Unsupported result statement emitted? NO
* Production terminology upgrade authorized? NO
* Patch report created? YES
* Ready for production QC rerun? YES
* Recommended next task = M_SURROGATE_PRODUCTION_QC_RERUN
