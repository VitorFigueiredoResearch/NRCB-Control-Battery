# Citation Verification Report

## 1. Citation Verification Executive Status

The minimum citation set is verified with limited scope. The paper now has verified support for SPARC data provenance, surrogate-data lineage, permutation-distribution methodology, and rank-correlation permutation testing. No close rotation-curve or radial-profile control precedent was verified.

Classification: `CITATION_VERIFICATION_PASS_WITH_LIMITED_SCOPE_READY_FOR_DRAFTING`.

## 2. Files Read

- `notes/CITATION_LOCK.md`
- `notes/CITATION_LOCK_CHECKS.csv`
- `notes/citation_candidates.md`
- `manuscript/references.bib`
- requested figure, terminology, value-ledger, and production-QC context files

No manuscript or production-output file was modified.

## 3. Verification Method

Metadata were checked against DOI/Crossref records and primary arXiv records. Claim scope was checked against the primary-record abstract or record description rather than search snippets alone.

Primary records used include DOI records for the journal articles and book, plus arXiv records for SPARC, Schreiber--Schmitz reviews, the permutation-method papers, and the astronomy-side examples.

## 4. Minimum Citation Set Status

- SPARC/data context: **SATISFIED**
- Surrogate-data lineage: **SATISFIED**
- At least two permutation/correlation baseline references: **SATISFIED WITH BOUNDED WORDING**
- Close radial-profile/rotation-curve control precedent: **NOT SATISFIED**

The minimum set is sufficient for a limited-scope Methods/Demonstration draft. Motivation must not claim common published rotation-curve shuffle-null practice.

## 5. SPARC/Data Context Citations

`Lelli2016` is verified for the SPARC catalogue and data context. The verified record describes a public sample of 175 nearby galaxies with 3.6-micron photometry and high-quality rotation curves.

`TODO_RAR_context` is dropped because it is unnecessary for the methods/control paper and would broaden scope.

## 6. Surrogate-Data Lineage Citations

`Theiler1992` is verified as formative surrogate-data lineage, with limited-use wording to avoid an unsupported sole-priority claim.

`SchreiberSchmitz2000` is the primary verified review for established surrogate methods, constrained randomization, and practical caveats. `SchreiberSchmitz1996` is verified for a constrained iterative surrogate variant, but it must not be described as identical to the implemented random-phase control.

`Lancaster2018` is verified as a broad modern review, limited to general physical-systems context. `Raeth2012` is verified as an astronomy-relevant caution about surrogate algorithms retaining unintended Fourier-phase correlations.

## 7. Permutation/Shuffle Baseline Citations

`PhipsonSmyth2010` is verified for permutation reference distributions and finite Monte Carlo empirical-p-value calculation.

`YuHutson2022` is verified for permutation testing in rank-correlation inference. Together these support the bounded claim that permutation procedures are established tools in general statistical and correlation testing.

`FeigelsonBabu2012` is verified only for broad astronomy resampling and nonparametric context. It does not prove common permutation use in rotation-curve work.

`CornishSampson2016` is a verified specialized astronomy example of deliberately scrambled controls, but it is remote from radial profiles. `ManolopoulouPlionis2017` is verified bibliographically and excluded from the intended baseline claim because its record supports Monte Carlo mock-cluster testing, not a shuffle/permutation correlation baseline.

## 8. Radial-Profile/Relevance Citations

No close verified rotation-curve or radial-profile control precedent was established. The introduction must therefore use conservative general-method motivation and must not claim common published rotation-curve shuffle-null practice.

## 9. Optional/Drop Candidates

- `TODO_RAR_context`: dropped.
- `TODO_astronomy_surrogate_use`: dropped as a placeholder; bounded verified examples are recorded separately.
- `SantoroWaghmarePanaretos2026_candidate`: dropped from the current citation set. The arXiv record exists, but the claimed PNAS status was not verified and the optional conceptual citation is not needed.

## 10. BibTeX Patch Candidates

`notes/BIBTEX_PATCH_CANDIDATES.bib` contains only records classified `VERIFIED_USE` or `VERIFIED_LIMITED_USE`. It is a candidate patch for human review and was not merged into `manuscript/references.bib`.

## 11. Claims Now Safe To Cite

- SPARC supplies the rotation-curve data context and contains 175 galaxies.
- Surrogate-data and constrained-randomization methods are established methodological tools with control-family-specific caveats.
- Permutation procedures create empirical reference distributions and require explicit finite-sample empirical-p-value handling.
- Permutation testing is an established approach for rank-correlation inference.
- Astronomy uses resampling methods and, in specialized settings, scrambled controls.

## 12. Claims Still Unsafe

- Common published rotation-curve shuffle-null practice.
- A close radial-profile control precedent.
- Equivalence between every cited surrogate variant and the implemented control families.
- Any physical, model-comparison, or result-support claim based solely on methodological citations.
- Any claim that fixed references are stochastic distributions.

## 13. Remaining Citation Risks

- No close radial-profile precedent was verified.
- Astronomy-side scrambled-control examples are specialized and must not be overgeneralized.
- The optional geometry-aware candidate was dropped because its claimed venue/status was not verified.

## 14. What This Verification Allows

- A limited-scope Methods/Demonstration drafting skeleton.
- Use of the verified BibTeX candidate file after human review.
- Conservative statements that permutation and surrogate methods are established general methodological tools.

## 15. What This Verification Does Not Allow

- It does not authorize edits to the manuscript or bibliography.
- It does not authorize a field-specific common-practice claim for rotation curves.
- It does not authorize physical interpretation, model-comparison claims, or unsupported result statements.

## 16. Required Next Step

`METHODS_DEMONSTRATION_DRAFTING_SKELETON`

## 17. Final Status

- Minimum citation set: **SATISFIED WITH LIMITED SCOPE**
- Citation-unblocked for Methods/Demonstration drafting: **YES**
- Radial-profile precedent: **NOT VERIFIED**
- Manuscript edited: **NO**
- Unsupported citation details invented: **NO**
