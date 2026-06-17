# SPARC Bootstrap Validator Test Summary

## Test Output Location

Validator test outputs were written under:

```text
notes/bootstrap_validation_test_outputs/
```

This folder contains positive-mode validation reports and two negative-test report sets. These are validator test artifacts only.

## Positive Tests

| Mode | Exit Code | JSON Status | Blocking Errors | Warnings |
|---|---:|---|---:|---:|
| manuscript-reproduction | 0 | PASS | 0 | 0 |
| figure-reproduction | 0 | PASS | 0 | 0 |
| parameter-extraction | 0 | PASS | 0 | 0 |
| test-mode | 0 | PASS | 0 | 0 |
| full-production | 0 | PASS | 0 | 0 |

## Negative Tests

| Test | Exit Code | Expected Result | Observed Blocking Check |
|---|---:|---|---|
| missing parameter-extraction table path | 1 | fail closed | `SPARC001_TABLE1_MISSING` |
| missing source-root path for full-production | 1 | fail closed | source, vendor, gravity, adapter, and selected-rotmod failures |

## Non-Operations Confirmed

- Downloads attempted: NO
- Production rerun attempted: NO
- Figures regenerated: NO
- Manuscript modified: NO
- Raw SPARC files moved/copied/deleted: NO

## Notes

The validator reports local path details in runtime validation outputs because those paths are supplied for local diagnosis. Public-facing documentation uses placeholders and does not include private absolute paths.
