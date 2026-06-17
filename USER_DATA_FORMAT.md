# User Data Format Draft

Generic user-supplied data mode is not implemented in v1.0. This file records a future interface contract only.

The NRCB release currently supports paper reproduction and SPARC dependency preflight for the official paper pathway. It does not claim arbitrary radial-profile data support.

Future user-data wrappers should require, at minimum:

- `object_id` or `galaxy_id` group identifier;
- strictly positive radius values;
- finite observed residual/profile values;
- optional uncertainty columns;
- optional template/covariate columns;
- one object/profile per group;
- documented units;
- enough finite radial points for the requested diagnostic branch.

Validation rules and example files must be implemented before this mode is described as runnable.

Outputs would be computational control summaries only and would not imply physical interpretation.