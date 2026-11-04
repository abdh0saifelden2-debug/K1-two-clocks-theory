# Pre-specification freeze record

**File:** `docs/PRESPEC_ROLE_BUDGET.md`
**SHA-256:** `c02735bb034ea704ec686aa419dbb14e0154252f9aa7c70007a6517acc4d4322`
**Frozen (UTC):** 2026-11-04T21:11:33Z
**Tag:** `paper0-roles-prespec-v1`
**Tag target:** the commit that adds this record. The tag is annotated and its
message repeats the hash.
**Status:** frozen before the first execution of `run_role_budget.py`.

The hash is of the pre-specification file as committed. To verify:

```bash
sha256sum docs/PRESPEC_ROLE_BUDGET.md
```

Any protocol change after this freeze is an amendment in a new file with its own
hash and tag. The original pre-specification remains the reference. The freeze
covers the protocol only; the generator may be corrected for bugs that do not
change the protocol, and any such correction is recorded in the report.

## What is frozen

- the three-way held-out split (`fit` / `calibrate` / `test`);
- the deterministic arms `D0`--`D3` and their calibration rules;
- the reconstruction hierarchy `R_ops`, `R_ops_raw`, `R_shell`, `R_mode`,
  `R_pos`, `R_exact`;
- the Wasserstein-1 metric and its normalization;
- the additive budget `E_cal + E_amp + E_sign = E_total`;
- the material/negligible/adverse labels and the combined bootstrap interval;
- the hypotheses and kill conditions.

## What is not frozen

- the implementation details of the generator, provided the protocol is
  unchanged;
- the figure layout and report prose;
- the seed list, which is committed in the artifact but is not part of the
  protocol;
- the optional 3D follow-up, which is a separate pre-specification.
