# M-Surrogate Extension Execution Report

## Executive summary

- Execution mode: production mode.
- Execution status: PRODUCTION_COMPLETED_QC_PENDING.
- This is a statistical-hygiene implementation run.
- Separate QC is required before manuscript terminology changes.

## Input files used

- `notes\M_SURROGATE_EXTENSION_DESIGN.md`
- `notes\EVIDENCE_LOCK.md`
- `notes\SAMPLE_ATTRITION_134_TO_76.csv`
- `notes\HEADLINE_VALUE_RECOMPUTE.csv`
- `notes\REALIZATION_CENSUS.csv`

## Source scripts/data read

- Read-only reconstruction adapter located dynamically.
- Frozen parameters, numerical constant, and rotation-curve files read without modification.

## Reconciliation accounting

- Selected galaxies: 134.
- Reconstructed galaxies: 134.
- Galaxies with emitted rows: 134.
- Invalid-only galaxies: [].
- Missing galaxies: [].
- Missing tiers: [].
- Emitted rows: 426166; valid rows: 426164; invalid rows: 2.

## Tier accounting

- `shuffle_surrogate_partial_rank`: requested=134000, emitted=134000, valid=133999, invalid=1, status=COMPLETE; Strategy: Random surrogate ensemble.
- `shuffle_surrogate_partial_rank_absolute`: requested=134000, emitted=134000, valid=133999, invalid=1, status=COMPLETE; Strategy: Random surrogate ensemble.
- `circular_shift_control_partial_rank`: requested=2969, emitted=2969, valid=2969, invalid=0, status=COMPLETE; Strategy: Exhaustive N-1 circular shifts.
- `circular_shift_control_partial_rank_absolute`: requested=2969, emitted=2969, valid=2969, invalid=0, status=COMPLETE; Strategy: Exhaustive N-1 circular shifts.
- `random_phase_surrogate_residual`: requested=76000, emitted=76000, valid=76000, invalid=0, status=COMPLETE; Strategy: Random surrogate ensemble.
- `random_phase_surrogate_radial_template`: requested=76000, emitted=76000, valid=76000, invalid=0, status=COMPLETE; Strategy: Random surrogate ensemble.
- `smooth_profile_exponential_reference`: requested=76, emitted=76, valid=76, invalid=0, status=COMPLETE; Strategy: Fixed reference, not stochastic.
- `smooth_profile_linear_reference`: requested=76, emitted=76, valid=76, invalid=0, status=COMPLETE; Strategy: Fixed reference, not stochastic.
- `smooth_profile_quadratic_reference`: requested=76, emitted=76, valid=76, invalid=0, status=COMPLETE; Strategy: Fixed reference, not stochastic.

## Circular-shift status

- Production requests exhaustive nontrivial offsets and checks completeness before completion.

## Smooth-reference status

- Exponential, linear, and quadratic references are fixed, not stochastic.

## Runtime and storage estimate

- Measured runtime: 484.138 seconds.
- Compressed CSV or Parquet may be useful; final figure source should remain lightweight.

## Output files created

- `per_realization_controls.csv`
- `per_galaxy_null_summary.csv`
- `global_control_battery_summary.csv`
- `figure2_source_data.csv`
- `extension_run_manifest.csv`
- `execution_report.md`
- `implementation_warnings.csv`

## Language lock

- Manuscript edited: NO.
- Physical interpretation emitted: NO.
- Unsupported result statement emitted: NO.
- Production terminology upgrade authorized: NO, QC_REQUIRED.
- Production execution: YES, QC_REQUIRED.
- Production M=1000 language requires separate production QC.

## Remaining requirement

- Production outputs have been generated. A separate production-output QC is required before manuscript use or terminology upgrade.

## Derived summary patch

- Derived summary outputs were corrected after production QC; realization rows were not regenerated or modified.
- Production terminology upgrade remains unauthorized until a production-QC rerun passes.
