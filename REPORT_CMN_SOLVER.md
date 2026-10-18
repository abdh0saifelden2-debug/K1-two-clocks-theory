# RESULT 15 — §H.3 clock-mismatch (CMN) correction, run in a transient K-theory thermal solver

**Status:** the §G.5 correction term `−CMN·∇·(∂_t K_u ∇θ)` with `CMN = +τ_c` is
**[VERIFIED — synthetic K-theory solver]** as *error-reducing in transients and
null in steady state* — the §H.3 forecast, which was previously flagged
"not runnable here (implement in ISSM/GlaDS)". Harness `cmn_solver_demo.py` →
`figures/60_cmn_solver_demo.json` (+ `.png`), tests `tests/test_cmn_solver_demo.py`
(4/4). No external data; no GPU.

## What was open

§G.5 derived the exact commutator identity and pinned the coefficient:

- **Identity [DERIVED, exact]:** `[∂_t, D]θ = ∇·((∂_t K_u)∇θ)`, with
  `D[θ] = ∇·(K_u ∇θ)`. Verified numerically (identity, steady null, linearity,
  dimensional signature) by [`cmn_synthetic.py`](https://github.com/abdh0saifelden2-debug/K2-subglacial-cavity/blob/792cbed31b3677bad51f1cfe4473405e5e877978/validation/synthetic/cmn_synthetic.py) in `K2-subglacial-cavity`.
- **Coefficient [DERIVED + MEASURED]:** dimensional analysis forces `CMN ≡ τ_c`
  (a time, not an `O(1)` constant); `τ_c` is measured `≈0.02–0.03` with
  `sign(τ_c)=+` (RESULT 12, `gle_coefficients.py`).

What was **not** earned was the §H.3 claim itself — the *operational* statement
that **adding the term to a transient temperature solve reduces the spurious
error, and vanishes for steady turbulence**. §H.3 deferred this to an external
ice-sheet model (ISSM/GlaDS). This result settles the model-side question in a
self-contained solver here.

## The test

The physical content of §G.5 is the **two-clocks lag**: the turbulence that sets
`K_u` at time `t` is communicated to the heat equation with a finite
decorrelation lag `τ_c`. So the faithful ("truth") diffusive flux uses the
**lagged** diffusivity `K_u(x, t−τ_c)`, whereas a naive K-theory closure freezes
it at `K_u(x, t)`. The first-order Taylor identity

> `K_u(t) − τ_c ∂_t K_u(t) = K_u(t−τ_c) + O(τ_c²)`

shows the §G.5 correction with `CMN = +τ_c` is *exactly* the first-order
reconstruction of the lagged-clock truth. `cmn_solver_demo.py` advances three
solvers with an **identical** RK4 spectral stepper, grid and `θ_0` over one
transient cycle `T = 2π/ω` of `K_u(x,t) = K₀(1+κ cos x)(1+ε sin ωt)`; only the
diffusivity field in the flux differs:

| solver | flux diffusivity | meaning |
|---|---|---|
| truth | `K_u(x, t−τ_c)` | lagged clock (faithful) |
| naive | `K_u(x, t)` | frozen clock (plain K-theory) |
| corrected | `K_u(x, t) − τ_c ∂_t K_u` | §G.5 term, `CMN = +τ_c` |
| wrongsign | `K_u(x, t) + τ_c ∂_t K_u` | `CMN = −τ_c` (sign control) |

Because all four share the discretisation, the (common) numerical-diffusion error
cancels in the truth-vs-closure comparison — isolating the **modelling** (clock)
error.

## What this result establishes

Production run (`n=96`, `dt=5×10⁻⁴`, `K₀=0.2`, `κ=0.3`, `ε=0.5`, `ω=2`):

### A. The correction cuts the transient error ~15×
At `τ_c=0.05` the time-max relative error vs the lagged-clock truth is
**naive `9.07×10⁻³`** → **corrected `6.05×10⁻⁴`** (a **15×** reduction). Over the
cycle the naive error is a spurious oscillation tracking `∂_t K_u ∝ cos ωt`; the
correction removes it (left panel of the figure).

### B. Leading-order error is removed (`τ_c¹` → `τ_c²`)
Sweeping `τ_c ∈ {0.0125, 0.025, 0.05, 0.1}`, the time-max error scales as a clean
power law: **naive log–log slope `1.03` (`∝τ_c`)**, **corrected slope `2.00`
(`∝τ_c²`)**. This is the rigorous statement of "the correction removes the
leading clock-mismatch term": the residual is one order higher in the small
parameter `τ_c`.

### C. Identically null for steady turbulence
With `ε=0` (`∂_t K_u=0`) the correction term is identically zero *and* the lagged
and frozen clocks coincide, so all three solvers are **bit-identical** — measured
max error `0.0` (exactly) for both naive and corrected. This is the §G.5
"maximal in transients, zero in steady state" property, end-to-end in the solver
(not just in the term).

### D. The `+τ_c` sign is the error-reducing one
The wrong-sign run (`CMN = −τ_c`) gives time-max error `1.77×10⁻²` — **worse than
the naive** `9.07×10⁻³` (it doubles the lag instead of cancelling it). So the
positive sign of §G.5/RESULT 12 is not only an autocorrelation-time fact; it is
the *unique* sign that makes the commutator term reduce a transient solve.

## Honest scope

This is a **synthetic model verification**, in the spirit of §V.3 (plant a known
structure, check recovery), not a claim about any specific operational model. The
"truth" is the minimal faithful representation of §G.5's own stated mechanism (a
`τ_c` lag in the eddy-diffusivity clock); the result is that *given that
mechanism*, the §G.5 term is its exact first-order correction and demonstrably
reduces the transient error with the predicted order and sign. The remaining
[HYP] is unchanged: whether a **real** K-theory thermal solver (ISSM/GlaDS) on a
**real** surge/plume transient shows the same improvement — a model-side test that
still needs that external solver, now with a quantified expectation (`τ_c`-order
error reduction, steady-state null, `+` sign).
