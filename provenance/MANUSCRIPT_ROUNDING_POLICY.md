# Manuscript Rounding Policy

## Purpose

This policy separates manuscript-facing precision from machine-readable audit
precision. Full-precision values remain in the figure-value ledger and
QC-accepted summary tables.

## Rules

- Report correlation-like and concentration-like quantities to three decimal
  places in main prose unless a tighter precision is methodologically needed.
- Report interval endpoints to three decimal places in main prose.
- Keep sample sizes and realization counts as exact integers.
- Keep full precision in machine-readable ledgers, source tables, and
  reproducibility checks.
- Do not print long machine-precision decimals in manuscript prose.
- Keep values used only for audit checks out of the main narrative.
- Use an approximation marker when a rounded value is not exact, for example
  `approximately 0.509` or `\(\simeq 0.509\)`.
- Do not round values before computing aggregates, intervals, empirical
  percentiles, or empirical p-values.

## Applied Drafting Examples

- observed absolute partial-rank median: approximately `0.509`;
- shuffle control median-of-medians: approximately `0.182`;
- exact circular-shift median-of-medians: approximately `0.532`;
- residual spectral-concentration median: approximately `0.676`.

## Status

Applied to `methods_demonstration_skeleton_v2.md` and
`methods_demonstration_latex_stub_v2.tex`. Human review remains required before
controlled manuscript integration.
