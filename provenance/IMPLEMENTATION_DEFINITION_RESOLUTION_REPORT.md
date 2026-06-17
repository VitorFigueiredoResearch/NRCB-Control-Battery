# Implementation Definition Resolution Report

## 1. Resolution Executive Status

The radius-conditioning coordinate and circular-shift implementation were
traced to their implementation sources. The radius coordinate is now fully
defined from observed rotation-curve radii. A manuscript-safe operational
justification for cyclic wrap-around was written, but the methodological choice
still requires human approval before controlled integration.

Resolution classification:
`IMPLEMENTATION_DEFINITIONS_PARTIAL_HUMAN_JUSTIFICATION_REQUIRED`.

## 2. Files Read

- The v2 reaudit, revision report, and method-definition table.
- The isolated v2 Markdown and LaTeX skeletons.
- `src/run_m_surrogate_extension.py` and the summary-patch script, read-only.
- The dynamically discovered read-only reconstruction adapter.
- The read-only upstream reconstruction function that creates `r_frac`.
- The read-only observed-profile loader used by reconstruction.

No production run or scientific recomputation was performed.

## 3. Radius-Conditioning Coordinate Finding

`r_frac` construction was verified.

1. The observed-profile loader reads radius and velocity from columns 0 and 1
   of each observed rotation-curve file.
2. It excludes rows with nonfinite or nonpositive radius or velocity before
   returning the observed vectors.
3. Reconstruction defines `Rmax` as the maximum retained observed radius.
4. Reconstruction returns `r_frac = r_obs / Rmax`.
5. The adapter sorts the observed vectors, applies its post-reconstruction
   joint validity mask, and returns the retained `r_frac`.
6. The neutral engine uses that same returned vector for branch reconstruction
   and partial-rank radius conditioning.

Therefore, `r_frac` is dimensionless and equals observed radius divided by the
maximum retained observed radius for the same galaxy. It is not constructed
from the reconstructed radial grid.

Correctly constructed finite values lie in `0 < r_frac <= 1`. The adapter
nevertheless applies a permissive `r_frac <= 1.1` check. The upstream
reconstruction also evaluates its supporting radial profile out to
`1.10 * Rmax`, but still returns the observed-radius fraction. Source comments
do not state the original rationale for choosing the permissive `1.1` guard;
its verified implementation effect is only that a looser upper check is
applied after construction. It does not change the normalization or admit an
additional correctly constructed observed-radius fraction.

## 4. Radius-Conditioning Manuscript Definition

For galaxy \(g\), let \(R_{gi}\) be a retained observed rotation-curve radius
after excluding nonfinite or nonpositive radius and velocity rows, and let
\(R_{\max,g}=\max_i R_{gi}\). The dimensionless radius-conditioning coordinate
is

\[
r_{gi}=R_{gi}/R_{\max,g}.
\]

The same retained coordinate is used in the post-reconstruction validity mask
and in partial-rank residualization. Correctly constructed values lie in
\(0<r_{gi}\leq1\). The adapter's permissive \(r_{gi}\leq1.1\) check is a
looser post-construction bound and does not redefine the normalization. The
source does not explicitly document why `1.1` was selected.

## 5. Circular-Shift Implementation Finding

The implementation was verified:

- The shifted vector is the normalized radial covariate.
- The radius-conditioning vector and residual profile remain fixed.
- The frozen reconstructed vectors and validity mask are reused.
- `np.roll` performs the cyclic shift.
- Production offsets are exactly `1, 2, ..., n_valid - 1`.
- Offset zero is excluded.
- Duplicate offsets are explicitly rejected.
- Each shifted covariate is transformed by the same radial-template function
  before recomputing the same radius-conditioned partial-rank statistic.
- Invalid statistic rows are emitted and retained with an invalid reason.
- Exact-shift status is assigned only when the full nontrivial offset set is
  present.

## 6. Cyclic Boundary Justification

Cyclic wrap-around is an operational randomization convention, not a physical
radial boundary claim. It preserves the finite sample size, frozen validity
mask, and ordered covariate sequence under every offset while changing the
alignment between the radial-template covariate and the fixed residual
profile. Evaluating every non-identity cyclic offset defines an exact finite
randomization space conditional on this convention.

The comparison tests sensitivity to radial ordering and alignment. It does not
imply that the innermost and outermost radial bins are physically adjacent.
Because this is a methodological design choice rather than a fact encoded by
the data, the wording should receive human approval before controlled
integration.

## 7. Limitations Wording

Non-cyclic boundary conventions, block shifts, edge-truncated shifts,
alternative detrending controls, residualization against smooth radial
profiles, and alternative radial templates are possible designs. They were not
tested in the current demonstration.

## 8. Skeleton Patch Status

Created:

- `manuscript/drafts/methods_demonstration_skeleton_v3.md`
- `manuscript/drafts/methods_demonstration_latex_stub_v3.tex`

The v3 files preserve v2 except for:

- the resolved radius-conditioning coordinate passage;
- the cyclic-boundary operational justification;
- directly related limitation and integration-guard wording;
- the v3 identifier.

`manuscript/main.tex` and `manuscript/references.bib` remained untouched.

## 9. Remaining Risks

- The historical source does not explicitly explain why the permissive adapter
  guard is `1.1`; v3 states only its verified effect and distinguishes it from
  the coordinate normalization.
- The cyclic-boundary justification is manuscript-safe and implementation-
  grounded but remains a methodological choice requiring human approval.
- Alternative boundary and detrending controls were not tested.

## 10. What This Resolution Allows

The v3 isolated skeletons may proceed to referee-style reaudit. The coordinate
definition is now reproducible, and the exact circular-shift distribution is
explicitly conditional on an operational cyclic convention.

## 11. What This Resolution Does Not Allow

This resolution does not authorize controlled manuscript integration,
production reruns, new controls, physical interpretation, or claims beyond the
locked computational-methods scope.

## 12. Required Next Step

`REFEREE_STYLE_METHODS_DEMONSTRATION_V3_REAUDIT`

The reaudit should assess whether the operational cyclic-boundary wording is
acceptable for controlled integration.

## 13. Final Status

- `r_frac` construction verified: **YES**
- Radius-coordinate definition written: **YES**
- Circular-shift implementation verified: **YES**
- Cyclic-boundary justification written: **YES**
- Cyclic-boundary human approval still required: **YES**
- v3 skeletons created: **YES**
- Manuscript main edited: **NO**
- References bibliography edited: **NO**
- Ready for referee-style v3 reaudit: **YES**
