# Pre-specification: the role budget of a stochastic subgrid residual

**Status:** pre-specified. This is an internal, project-level pre-specification,
not an externally registered protocol. This file is frozen before the
first run of `run_role_budget.py`. The freeze record — commit, tag, and SHA-256
of this file — is in [`PRESPEC_ROLE_BUDGET.FREEZE.md`](PRESPEC_ROLE_BUDGET.FREEZE.md).
Any change to the protocol after the freeze is an amendment, recorded in a
separate file with its own hash and tag; the original text remains the
reference.

**Prior-art boundary.** The stop-list check is in
[`STOPLIST_ROLE_BUDGET.md`](STOPLIST_ROLE_BUDGET.md). In brief: Perezhogin,
Glazunov & Gritsun (2019) already combine deterministic and stochastic
backscatter; Perezhogin & Glazunov (2023) already decompose subgrid fluxes by
Germano components; Schumann (1995) already measures the reduction of
stress--strain alignment by random SGS motions; Domaradzki & Saiki (1997)
already derive deterministic backscatter; and Tuteri, Alexakis & Chibbaro
(2026) already show that a gradient model carries the conditional mean flux
while the residual carries large, non-Gaussian, heavy-tailed fluctuations.
This pre-specification does **not** claim those observations. It tests a
narrower object: a held-out, additive decomposition of the residual's
distributional error into calibration, amplitude/intermittency, and sign
structure, in a sharp-cutoff 2D exact-force benchmark.

## Summary

**Question.** Does a deterministic gradient closure already carry the mean
subgrid transfer, and which part of the residual's distributional error is
removed by (i) oracle calibration of the residual shell spectrum, (ii)
per-mode amplitude information, and (iii) the sign pattern?

**Data.** Three independent 2D DNS realizations (`n = 256`, `kc = 32`, seeds
`42/43/44`). Each direction is a three-way held-out split: fit on one,
calibrate the operational spectrum on a second, score on the third.

**Budget.** With `W1` the mode-wise Wasserstein distance between the true and
model local-transfer distributions,

```
E_total = W1(d + R_ops) / W1(d)
E_cal   = [W1(d + R_ops) - W1(d + R_shell)] / W1(d)
E_amp   = [W1(d + R_shell) - W1(d + R_mode)] / W1(d)
E_sign  = W1(d + R_mode) / W1(d)
```

The three components sum to `E_total`. `R_ops` is operational (no test truth);
`R_shell` and `R_mode` are oracle reconstructions; `R_exact` is the truth.

**Decision.** Report the ranking in the low- and high-`k` bands. A component is
material if it is at least `0.10 E_total` and its combined bootstrap/seed
interval lies above `0.05 E_total`. The ranking is robust only if it repeats in
all three held-out directions.

**Kill conditions.** Stop or narrow to a benchmark note if the residual is
below the `0.05` floor, if the sign component is negligible everywhere, if the
combined interval is unresolved, or if the ranking flips across directions.

## 1. Question

Given an exact subgrid force `m_true` and a deterministic closure `d`
calibrated on a held-out realization, how much of the error in the
**distribution of the local subgrid transfer** is removed by

1. matching the residual shell spectrum with oracle information from the test
   realization (**calibration**),
2. matching the residual per-mode amplitudes (**amplitude/intermittency**), and
3. matching the residual sign pattern (**sign structure**)?

The three parts are measured as an additive budget. The question is which part
dominates, and whether the answer is stable across held-out realizations.

## 2. Data and split

- 2D incompressible DNS, `n = 256`, sharp cutoff `kc = 32`, forced inverse
  cascade, same solver and parameters as `run_closure.py`.
- Three independent realizations, seeds `42` (`A`), `43` (`B`), `44` (`C`),
  each after `6000` spin-up steps. One snapshot per realization.
- Each held-out direction is a **three-way split**: fit the deterministic
  coefficients on one realization, measure the operational residual spectrum on
  a second, and score everything on the third. The three directions are the
  cyclic rotations

  | Direction | Fit `d` | Calibrate `E_ops` | Test |
  |---|---|---|---|
  | 1 (primary) | `A` | `B` | `C` |
  | 2 | `B` | `C` | `A` |
  | 3 | `C` | `A` | `B` |

  The test truth is never used for fitting or for the operational spectrum, and
  the operational spectrum is never measured in-sample with respect to the
  fitted coefficients.
- A component is called **robust** only if it is material and has the same rank
  in all three directions. No direction is selected after seeing the results.

The three snapshots are independent realizations, not three times from one
run. This is the available ensemble; the flow is statistically stationary and
the forcing is random, so realization-to-realization variation is the relevant
held-out uncertainty. A temporal-stationarity check is out of scope for this
cheap screen.

## 3. Exact force and deterministic arms

The exact force is

```
m_true = P[ (ubar . grad) ubar - filt( (u . grad) u ) ],
```

with the sharp spectral filter at `kc`, as implemented in
`closure.sgs.exact_sgs_force`. All fields are truncated to `|k| <= kc`; the
`k = 0` mode is zero.

Deterministic arms:

| Arm | Definition | Calibration |
|---|---|---|
| `D0` | zero | none |
| `D1` | Smagorinsky, `nu_t = (Cs Delta)^2 |Sbar|`, `Cs = 0.17`, `Delta = pi/kc` | fixed standard constant |
| `D2` | Clark/gradient, `tau_ij = C Delta^2 (d_k ubar_i)(d_k ubar_j)`, `m = P div tau` | `C` by least squares on the calibration realization: `C = <m_true . m_grad> / <|m_grad|^2>`; fixed `C = 1/12` reported as a sensitivity |
| `D3` | shell-wise spectral eddy viscosity, `m_par = -nu_t(k) k^2 uhat` | `nu_t(k)` by least squares to the calibration `T_true(k)`; signs reported, not constrained |

`D2` is the primary deterministic arm because it is the standard local
gradient model and the closest 2D analogue of the Clark model used by Tuteri
et al. (2026). `D1` and `D3` are baselines. All arms are solenoidal by
construction (the gradient and Smagorinsky forces are Leray-projected; the
spectral-EV force is parallel to `uhat`). The divergence axis is therefore not
tested here; it is degenerate in this incompressible benchmark and belongs to
the compressible experiment.

## 4. Residual reconstruction hierarchy

For a deterministic arm `d`, the residual is `r = m_true - d`. Its
streamfunction is `psi`, with `r = grad_perp psi`; in Fourier space
`rhat = (i ky, -i kx) psihat`. This representation makes every reconstruction
solenoidal by construction.

For each shell `k`, let `E_r(k) = sum_shell |rhat|^2`. The reconstructions are:

| Label | What is matched | Phases / signs | Information used |
|---|---|---|---|
| `R0` | nothing (`r = 0`) | — | none |
| `R_ops` | `E_r(k)` from the **calibration** realization, rescaled by `Z_test / Z_cal` | random streamfunction phase | operational: no test truth; uses the test resolved strain only for the scalar amplitude |
| `R_ops_raw` | `E_r(k)` from the calibration realization, no rescaling | random streamfunction phase | sensitivity: isolates the trivial realization-to-realization energy mismatch |
| `R_shell` | `E_r(k)` from the **test** realization | random streamfunction phase | oracle shell spectrum |
| `R_mode` | `|rhat|` per mode from the **test** realization | random streamfunction phase | oracle per-mode amplitudes |
| `R_pos` | `|rhat|` per mode from the test realization | all signs positive (maximal positive transfer) | diagnostic of the negative-transfer fraction |
| `R_exact` | `|rhat|` and signs from the test realization | exact | upper bound; `R_exact = r` |

The operational rescaling is `E_ops(k) = E_r^cal(k) * (Z_test / Z_cal)`, where
`Z = mean( |Sbar|^2 )` and `|Sbar|^2 = 2(S11^2 + S22^2 + 2 S12^2)` is the same
strain norm used by the Smagorinsky arm. It uses the test resolved strain but
never the test subgrid force. `R_ops_raw` is reported only as a sensitivity
check; the primary budget uses `R_ops`.

For `R_ops`, `R_shell`, and `R_mode`, the random phases are drawn from a real
Gaussian field so that Hermitian symmetry is preserved. `N_seed = 32` seeds are
used for each stochastic reconstruction; the seed list is committed in the
artifact.

In 2D the solenoidal subspace at each mode is one-dimensional, so a solenoidal
residual is parallel or antiparallel to `uhat`: the phase is a binary sign.
`R_mode` therefore randomizes signs while preserving every per-mode amplitude,
and `R_exact` restores the true signs. This is the exact 2D analogue of the
3D phase-randomization test, but it is **not** a continuous phase-angle test;
the continuous version requires the 3D benchmark and is not claimed here.

## 5. Metrics

For a shell `k` with `N_k` modes, the local transfer is

```
t = Re( uhat* . mhat ).
```

For the truth and for each reconstruction, form the array `t` over the modes in
the shell. The primary distance is the 1D Wasserstein-1 distance

```
W1(k) = (1/N_k) sum_i | sort(t_true)_i - sort(t_model)_i |,
```

normalized by `RMS_true(k) = sqrt( (1/N_k) sum_i t_true_i^2 )`. If
`RMS_true(k) = 0`, the shell is skipped and the count of skipped shells is
reported. The normalization makes `W1` dimensionless; a value of 1 means the
model's distribution is, on average, one truth-RMS away from the truth's
distribution.

Secondary metrics, reported per shell and in the band summaries:

- mean transfer `T(k) = sum_shell t` for truth, `d`, and the reconstruction;
- variance and standard deviation of `t`;
- 5th, 50th, and 95th percentiles of `t`;
- positive-tail mean `P_+ = mean( max(t, 0) )` and the positive fraction
  `f_+ = mean( t > 0 )`;
- sign alignment `A = sum_shell t / sum_shell |uhat| |mhat|` in `[-1, 1]` for
  the truth, `d`, and `r`. In 2D this is the amplitude-weighted mean sign.

Band summaries use `L = 1 <= k < kc/2` and `H = kc/2 <= k <= kc`, weighted by
`N_k`:

```
W_band = sum_k N_k W1(k) / sum_k N_k.
```

The additive budget is defined per shell, then averaged with the same weights.
Let

```
E_total = W1(model = d + R_ops) / W1(model = d)          (operational model error)
E_cal   = [W1(d + R_ops) - W1(d + R_shell)] / W1(d)     (calibration error)
E_amp   = [W1(d + R_shell) - W1(d + R_mode)] / W1(d)    (amplitude error)
E_sign  = W1(d + R_mode) / W1(d)                        (sign error)
```

Then `E_cal + E_amp + E_sign = E_total` exactly, by construction. `E_cal` is
positive when the oracle shell spectrum improves on the operational one;
`E_amp` is positive when per-mode amplitudes improve on the shell spectrum;
`E_sign` is the remaining error after all amplitude information is supplied,
which only the true sign pattern can remove. The identity is checked in the
test suite.

The components are **signed**. A negative component means that the more
informative reconstruction increased the distance on that test realization; it
is reported as adverse and is not clipped to zero. The accounting identity is
not a variance decomposition, and a negative component is a result about the
information ordering, not a numerical error. The material/negligible labels
below apply to positive components; a negative component is labelled
**adverse**.

`R_pos` is not part of the additive budget. Its `W1` and `C_pos = 1 -
W1(R_pos)/W1(d)` measure the cost of setting every sign positive, i.e. the
share of the transfer distribution carried by negative-transfer modes.

The **closure fraction** of any reconstruction is `C = 1 - W1(model)/W1(d)`.
`C = 0` means no improvement over `d`; `C = 1` means the reconstruction
reproduces the truth distribution exactly.

Uncertainty:

- the truth sampling uncertainty is a bootstrap over modes within each shell
  (200 resamples) for `W1(d)`, the percentiles, and the truth RMS;
- the stochastic reconstruction uncertainty is the 32-seed ensemble;
- the reported interval is the combined 5--95 range from 200 joint resamples
  (one mode bootstrap and one seed draw per resample). The point estimate is
  the mean over the 32 seeds;
- a component is **material** if its point estimate is at least
  `0.10 E_total` and its combined 5--95 range lies entirely above
  `0.05 E_total`. It is **negligible** if its point estimate is below
  `0.05 E_total`. Otherwise it is **unresolved**. If `E_total <= 0`, the
  operational reconstruction improves on `d`; the budget is reported with its
  signs but the material labels are not applied;
- the budget is interpreted only where `W1(d) > 0.05` (i.e. the deterministic
  model leaves at least 5% of a truth-RMS of distributional error). Below that
  floor the residual is too small for the decomposition to be meaningful; the
  report says so and stops;
- `R_ops_raw` is reported as a sensitivity check. If the primary `R_ops`
  budget differs materially from `R_ops_raw`, the difference is attributed to
  the resolved-strain rescaling, not to calibration skill.

## 6. Hypotheses and decision rules

| ID | Statement | Decision |
|---|---|---|
| H1 | `D2` captures the shell-mean transfer better than `D1` | compare the mean-transfer error in bands `L` and `H`; report, do not gate |
| H2 | the deterministic model leaves a material residual distribution (`W1(D2) > 0.05`) | if false in both bands, the residual budget is moot; report a validation/negative result and stop |
| H3 | calibration is material: `E_cal >= 0.10 E_total` | if true and robust, the oracle-versus-operational gap is the primary result |
| H4 | amplitude/intermittency is material: `E_amp >= 0.10 E_total` | if true and robust, a shell-spectrum-only stochastic model is insufficient; per-mode amplitude information matters |
| H5 | sign structure is material: `E_sign >= 0.10 E_total` | if true and robust, the 2D sign pattern is a first-order part of the residual; if false, a phase-aware closure is not justified in this benchmark |
| H6 | the ranking of the material components is the same in all three held-out directions | if false, report the directions separately and claim no universal ranking |

The expected outcome is not fixed in advance. A plausible outcome is that
`E_amp` and `E_sign` dominate and `E_cal` is small, because the residual
spectrum is a smooth quantity while the per-mode amplitudes and signs carry the
intermittency. The opposite outcome — calibration dominates — would make the
paper about operational calibration rather than about phase structure. Both are
reportable under this protocol.

## 7. Kill conditions

The program stops, or narrows to a benchmark note, if any of the following
holds:

1. **Prior art.** A stop-list paper already reports this held-out additive
   calibration/amplitude/sign budget in a comparable exact-force setting. Cite
   it and stop.
2. **No residual.** `W1(D2) <= 0.05` in both bands for all three directions.
   The deterministic model already closes the distribution; there is no
   residual role to budget.
3. **No sign role.** `E_sign` is negligible in both bands and all three
   directions. The phase-aware closure is not justified in 2D; report the
   calibration/amplitude result and stop.
4. **Unresolved noise.** The combined 5--95 range of a component exceeds 50%
   of its mean in the primary direction. Increase `N_seed` or report the
   component as unresolved; do not rank it.
5. **Split instability.** The material components change rank across the three
   held-out directions. Report the directions separately; do not claim a
   universal partition.

A negative result under conditions 2 or 3 is a publishable benchmark only if
the package is complete (generator, artifact, report, tests); it is not a new
closure principle.

## 8. What is not claimed

- Not a new closure, a new scaling law, or a claim that stochastic backscatter
  is unnecessary in general.
- Not a Mori--Zwanzig memory measurement. The residual is defined relative to a
  chosen deterministic model; a nonzero residual mean or a nonzero `d`--`r`
  cross-spectrum indicates deterministic-model misspecification, not a memory
  kernel. No memory claim is made.
- Not a compressible or fast-wave result. The incompressible benchmark cannot
  test the solenoidality axis; the compressible leakage experiment is separate.
- Not an a posteriori LES skill result. The test is distributional and a
  priori; it does not integrate the model forward.
- Not a continuous 3D phase-alignment result. The 2D sign test is a reduction;
  the 3D phase angle is deferred.

## 9. Outputs and reproducibility

- `run_role_budget.py --out-dir figures --report REPORT_ROLE_BUDGET.md`
  generates `figures/31_role_budget.json`, `figures/31_role_budget.png`, and
  the report.
- The JSON contains the configuration, seeds, git commit, UTC timestamp,
  per-shell arrays, band summaries, the budget components, and the seed
  ensemble. The report is generated from the JSON; no number is hand-edited.
- `tests/test_role_budget.py` checks: the budget identity
  `E_cal + E_amp + E_sign = E_total`; divergence of every reconstruction below
  `1e-12`; `W1 >= 0`; `C <= 1`; and the JSON/report key consistency.
- The report and artifact are committed in the same change. The generator is
  deterministic given the seeds; the seed list is committed.
- Execution is on Kaggle, not on the laptop, per the repository's machine
  constraint.

## 10. Freeze

This pre-specification is frozen by an annotated git tag and the SHA-256 of
this file, recorded in `docs/PRESPEC_ROLE_BUDGET.FREEZE.md`. The freeze is made
before the first execution of `run_role_budget.py`. If the code reveals a
protocol error, the run is stopped and an amendment is filed; the original
freeze is not silently edited.
