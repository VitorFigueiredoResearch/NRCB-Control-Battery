# User Data Schema Draft

This is a proposed strict input contract for future user-supplied radial-profile support. The current production engine does not yet implement this generic CSV interface.

## Required CSV Columns

| Column | Type | Required | Description |
|---|---:|---:|---|
| `object_id` | string | yes | Stable object, galaxy, or profile-group identifier. |
| `radius` | numeric | yes | Strictly positive radial coordinate. Units must be documented by the user. |
| `profile_value` | numeric | yes | Scalar radial-profile or residual-like quantity to analyze. |
| `radial_template_covariate` | numeric | yes | Radial-template or ordering covariate used for diagnostic alignment tests. |

## Recommended Optional Columns

| Column | Type | Description |
|---|---:|---|
| `profile_id` | string | Optional profile label when one object has multiple profiles. |
| `uncertainty` | numeric | Optional measurement uncertainty. |
| `radius_unit` | string | Unit label for `radius`; documented but not physically interpreted. |
| `value_unit` | string | Unit label for `profile_value`. |
| `velocity_observed` | numeric | Optional upstream rotation-curve column if residuals are computed externally. |
| `velocity_model` | numeric | Optional upstream model/comparator column if residuals are computed externally. |
| `residual_value` | numeric | Optional explicit residual. If used, wrapper rules must state whether this replaces `profile_value`. |

## Grouping Rules

- A diagnostic group is defined by `object_id` plus `profile_id` if present.
- Each group must contain one ordered radial profile.
- Radius sorting must be deterministic.
- Duplicate radii must be rejected or resolved by documented future wrapper rules.

## Numeric Validity Rules

- `radius` must be finite and strictly positive.
- Required numeric columns must be finite after masking.
- Nonfinite rows must be retained in validation reports and excluded from valid empirical calculations according to documented rules.
- The wrapper must report emitted rows, valid rows, invalid rows, and invalid reasons.

## Branch Eligibility Rules

- Circular-shift controls require at least 5 valid radial bins.
- Exact circular-shift offsets are all non-identity offsets `1..n_valid-1`.
- Shuffle controls require enough valid rows for the selected statistic; exact minimum must be verified in the wrapper implementation.
- Spectral controls require adequate finite sampling for the implemented spectral representation; exact minimum and interpolation rules are `FUTURE_IMPLEMENTATION_REQUIRED`.
- Fixed references require documented fitted or supplied reference definitions.

## Units and Interpretation

- Units must be documented for reproducibility.
- The workflow does not physically interpret units or infer galaxy-dynamics meaning from them.
- User data outputs are computational control summaries, not physical model verdicts.

## Implementation Gap

The current paper engine does not yet accept this schema. A future adapter must map this schema into the internal diagnostic vectors and branch-specific control families.
