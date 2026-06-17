# Citation Scope Reaudit

## 1. Executive Verdict
Citation/scope reaudit completed after controlled citation integration. The expansion from 5 to 14 active cited keys is safe: all active cited keys are verified or verified-limited-use within their documented claim scope, optional/dropped/unverified keys are absent, BibTeX resolves, and no new scope-risk claim was introduced.

Final classification: CITATION_SCOPE_REAUDIT_PASS_WITH_MINOR_WARNINGS.

Minor warnings remain for layout/provenance hygiene: the LaTeX log contains seven underfull hbox notices, and `references.bib` still contains stale comments describing entries as stubs/TODO-verification items even though the active bibliography compiles and citation locks record verification status.

## 2. Citation Count and Key Audit
Active manuscript cited keys: 14.

Active cited keys:

- `Courteau2014`
- `deBlok2008`
- `FeigelsonBabu2012`
- `Harris2020`
- `Lancaster2018`
- `Lelli2016`
- `PhipsonSmyth2010`
- `Sandve2013`
- `SchreiberSchmitz1996`
- `SchreiberSchmitz2000`
- `SofueRubin2001`
- `Theiler1992`
- `Wilson2014`
- `YuHutson2022`

`manuscript/references.bib` contains 14 entries. No duplicate BibTeX keys were found. The compiled `.bbl` contains all active cited keys. No uncited bibliography entries remain after the expansion.

## 3. Omitted-Citation Audit
The following keys are absent from active manuscript citations and `references.bib`:

- `McGaughLelliSchombert2016`
- `KimOharaKurokawa2026`
- `Hunter2007`
- `Keylock2006`
- `TODO_*` citation keys

No optional, dropped, or unverified citation key was added.

## 4. Section-by-Section Claim-Scope Audit
Introduction rotation-curve context: PASS. The new sentence states that rotation curves and radial profiles are widely used observational diagnostics and cites broad rotation-curve review, high-resolution survey, and galaxy-mass review references. It does not claim that circular-shift controls are standard in rotation-curve work, and it does not introduce model-comparison framing.

Introduction methodological context: PASS. The expanded citation cluster supports general statistical/correlation-testing context and broad astronomy-statistics practice. The manuscript explicitly preserves the non-claim that no particular control family is common published practice in rotation-curve analysis.

Methods constrained-surrogate caveat: PASS. `SchreiberSchmitz1996` is used only to state that more constrained surrogate families can preserve additional data properties. The text immediately limits the present random-phase tier to amplitude preservation and does not imply algorithmic equivalence.

Reproducibility context: PASS. `Wilson2014` and `Sandve2013` support documentation of entry points, inputs, outputs, environment details, and provenance. `Harris2020` supports NumPy as a software dependency. None of these citations is used to support empirical conclusions.

## 5. Scope and Terminology Audit
Risky terms were searched in the active manuscript body. Contexts are acceptable:

- `control-validation` appears as the workflow label and title language.
- `model-validation`, `discovery`, and `physical interpretation` appear only in explicit disclaimers.
- Scope-lock scan found no forbidden manuscript terminology in active manuscript prose.\n
No forbidden terminology was introduced by the citation expansion.

## 6. Rotation-Curve Precedent Audit
The manuscript still does not claim a close rotation-curve circular-shift precedent. The added rotation-curve references support observational/radial-profile context only.

The manuscript continues to state that the control families are not claimed as common published rotation-curve practice. This professional softening is retained and remains appropriate.

## 7. Bibliography Integrity Audit
BibTeX compile status: PASS. `main.blg` reports `warning$ -- 0`. No undefined citations appear in the final LaTeX log. No duplicate BibTeX keys were found.

Minor bibliography-hygiene warning: `references.bib` still contains old comments such as `stub entries only` and `%TODO: verify all fields against publisher record`. These comments are stale relative to the citation-lock state and should be cleaned in a later bibliography-polish pass, but they do not affect compilation or active claim scope.

## 8. Numerical and Result Stability Audit
Citation integration did not change reported numerical values, sample sizes, `M=1000`, figure references, availability wording, AI declaration wording, or result summaries.

The files containing values and figures (`main.tex`, `data.tex`, `demonstration.tex`, and final figure PDFs) retained their pre-integration timestamps. The citation integration diff summary records only changes to `introduction.tex`, `methods.tex`, `reproducibility.tex`, and `references.bib`, plus standard compile artifacts.

Methods equations were not changed. The only `methods.tex` change was the bounded constrained-surrogate caveat sentence near the random-phase discussion.

## 9. Layout and Compile Audit
Final compile artifacts indicate PASS:

- LaTeX/BibTeX command sequence exited successfully in the prior integration task.
- Final `main.log` reports output written to `main.pdf` with 12 pages.
- Undefined citations: 0.
- BibTeX warnings: 0.
- Overfull boxes: 0.
- Underfull boxes: 7.

The underfull hbox notices are minor layout warnings, mostly in bibliography formatting and the existing introduction contribution paragraph.

## 10. Referee Vulnerability Audit
The previous too-few-references vulnerability is substantially reduced. The paper now has a stronger but still conservative bibliography spanning rotation-curve context, SPARC/data context, surrogate/permutation methodology, broad astronomy-statistics context, reproducible computing, and NumPy.

Remaining vulnerabilities:

- MINOR: `references.bib` comments still describe entries as stubs/TODO verification despite verified citation-lock records.
- MINOR: seven underfull hbox layout notices remain.
- NONBLOCKING: no close rotation-curve circular-shift precedent is cited; the manuscript already avoids making that claim.

No blocking or major citation/scope risk was found.

## 11. Required Revisions
Before final release or submission, perform a small bibliography-polish pass to remove or replace stale verification comments in `references.bib`.

A later layout polish may address underfull hbox warnings if desired, but they do not block the citation/scope state.

## 12. What Is Safe To Keep
The 14-key active citation set is safe to keep. The added Introduction, Methods, and Reproducibility citation insertions are bounded and consistent with verified scope.

The explicit non-claim about common rotation-curve practice should remain.

## 13. What Must Be Removed or Softened
No manuscript citation or claim must be removed for citation-scope reasons.

Stale `references.bib` comments should be softened or removed in a later non-science bibliography-polish task.

## 14. Final Classification
CITATION_SCOPE_REAUDIT_PASS_WITH_MINOR_WARNINGS.

## 15. Final Status
Citation/scope reaudit completed: YES. Ready for release-package refresh: YES. Ready for release-package build: NO.
