# Extended findings

This is the detailed findings list moved out of the README after the v1.0.3
release. The manuscript (`paper0_two_clocks.tex`, v1.0.3) is the authoritative
claim set; this file preserves supporting and exploratory material that does
not belong in a one-page entry point.

Evidence labels follow the README legend: **theorem**, **numerical identity**,
**solver test**, **observational**, **exploratory**. Compound labels such as
`[theorem + solver test]` mean both apply.

**Pre-specified** means thresholds were fixed in the analysis code before the
final analysis; this repository has no external registration. Figure references
such as `figures/01–08` are descriptive ranges; individual files are in
[`figures/`](../figures).

---

## 1. The observation

**Temperature is a local, slow, parabolic field. Pressure is a global, fast,
elliptic field. They cannot be modelled as one coupled scalar.**

| Evidence | Data | Report | Figures |
|---|---|---|---|
| Temporal two clocks: temperature is a clean 24 h diurnal signal; pressure is multi-day synoptic + a 12 h global tide; bulk P–T daily coupling is r ≈ +0.07 (essentially decoupled) | NEON eddy-flux, WREF, 30-min | [`REPORT.md`](../REPORT.md) | `figures/01–08` |
| Latitude gradient: the 12 h pressure tide weakens monotonically equator→pole (1.10 → 0.34 hPa, EYW→SEA) while the diurnal temperature peak is the same everywhere — pressure knows the *whole atmosphere's* geometry, temperature only the sun overhead | ASOS 1-min, 8 stations 24.6–47.4°N, Q1 2020 | [`REPORT_ASOS.md`](../REPORT_ASOS.md) | `figures/09–12` |
| The same two clocks in real winds: divergent (fast/elliptic) vs rotational (slow/local) wind components separate cleanly in reanalysis | NCEP/NCAR Reanalysis 1 | [`REPORT_REANALYSIS.md`](../REPORT_REANALYSIS.md) (`run_reanalysis.py`) | `figures/25–27` |
| **Rossby-number two clocks**: the divergent (fast) wind fraction scales `KE_div/KE_rot ~ Ro² ∝ f⁻²` (extratropical slope −2.1) and is 26× larger in the tropics — the rotating analog of `KE_dil/KE_sol ~ M²` (Rossby↔Mach). Thinker/Builder | NCEP/NCAR Reanalysis 1 | [`REPORT_ROSSBY_CLOCKS.md`](../REPORT_ROSSBY_CLOCKS.md) (`run_rossby_clocks.py`) | `figures/68` |
| **Two clocks in TIME**: the divergent (fast) wind decorrelates in ~6 h vs ~18 h for the rotational (slow) wind (3× at 500 hPa) — the fast/slow clocks tick at different rates, measured in 6-hourly winds. Thinker/Builder | NCEP/NCAR Reanalysis 1 | [`REPORT_TEMPORAL_CLOCKS.md`](../REPORT_TEMPORAL_CLOCKS.md) (`run_temporal_clocks.py`) | `figures/69` |

## 2. The implications

- **Spatial decoupling [solver test]** — in Rayleigh–Bénard DNS both fields
  share the roll wavelength, but the *small scales* diverge: pressure's Taylor
  microscale is **2.4×** the buoyancy's and its high-k spectral power is ~**10⁴×**
  smaller. ∇²p = f is a global low-pass filter; temperature is torn into local
  filaments. [`REPORT_RB.md`](../REPORT_RB.md), `figures/13–15`.
- **K-theory breakdown [observational]** — single-Prandtl K-theory fails on
  NEON stability classes precisely where the two clocks decouple.
  [`REPORT_STABILITY.md`](../REPORT_STABILITY.md), `figures/06–08`.
- **Geometry → global pressure [solver test]** — a single localized bump in
  the boundary reshapes the *whole-domain* elliptic pressure response but only
  the *local* parabolic temperature response.
  [`REPORT_ELLIPTIC_PRESSURE.md`](../REPORT_ELLIPTIC_PRESSURE.md), `figures/39`
  (`run_elliptic_demo.py`).
- **Timescale separation = the singular-perturbation parameter [solver test]** — one
  number read two ways: the elliptic pressure constraint is instantaneous (Leray
  projection drives ‖∇·u‖ to 1e-14 in a single step, τ_fast→0) while parabolic
  transport relaxes at finite κk² (τ_slow=1/(κk²)), so ε=τ_fast/τ_slow=κk/c_s ∝ c_s⁻¹
  → 0 — the Mach→0 singular limit (ω=c_s·k recovered to 1.000). Unifies the two-clocks
  timescale separation with the singular-perturbation theory of transport decoupling.
  [`REPORT_TIMESCALE_SEPARATION.md`](../REPORT_TIMESCALE_SEPARATION.md)
  (`timescale_separation.py`, 3 tests).
- **The crossover is dynamical, not metaphysical [solver test]** — with finite
  sound speed pressure is hyperbolic; as c→∞ it becomes elliptic. The two clocks
  emerge in the incompressible limit. [`REPORT_COMPRESSIBLE.md`](../REPORT_COMPRESSIBLE.md),
  [`REPORT_NS.md`](../REPORT_NS.md), `figures/16–21`.
- **The regularity face of the two clocks [solver test]** — at the
  velocity-gradient-tensor level, discarding the nonlocal (anisotropic) pressure
  Hessian is exactly the restricted-Euler model → finite-time blowup (the
  Vieillefosse tail); restoring it regularizes. The Mach→0 singular limit
  *installs* that nonlocal Hessian (local EOS `c²Hess(ρ)` → nonlocal elliptic,
  `~M²`), bridging the compressible DNS to the regularity picture.
  [`REPORT_REGULARITY.md`](../REPORT_REGULARITY.md),
  [`REPORT_MACH_REGULARITY.md`](../REPORT_MACH_REGULARITY.md), `figures/65–66`
  (`restricted_euler_regularity.py`, `mach_regularity_bridge.py`).
- **A conditional Clay-problem attack [exploratory]** — a rigorous
  conditional program: restricted-Euler blowup (rigorous) ⇄ Beale–Kato–Majda
  vorticity-integral ⇄ Constantin–Fefferman geometric depletion (measured in a real
  3D NS DNS: vorticity aligns with the intermediate strain eigenvector, depleting
  self-stretching to `δ≈0.30`). Reduces 3D-NS regularity to a single depletion
  inequality on the nonlocal pressure Hessian; the open core is stated explicitly.
  [`REPORT_CLAY_REGULARITY.md`](../REPORT_CLAY_REGULARITY.md), `figures/67`
  (`clay_regularity_program.py`).
- **The molecular foundation [theorem + solver test]** — the bottom of the
  Newton→Boltzmann→compressible-NS→incompressible-NS ladder. A 2-D hard-disk gas is
  *regular by construction* (momentum/energy conserved to `~1e-14`, no finite-time
  singularity), relaxes to Maxwell–Boltzmann (H-theorem; `v_x` kurtosis 1→3,
  equipartition), and makes pressure by collisions (the EOS). But the rigorous
  hydrodynamic limit (Golse–Saint-Raymond 2004; Deng–Hani–Ma 2025, Hilbert's 6th)
  lands at **Leray weak** solutions — so the molecular origin **relocates** the Clay
  problem to "does regularity survive the limit", it does not solve it (Tao-2014
  averaged-NS blowup shows energy arguments alone cannot close it). The surviving
  payoff: the nonlocal pressure Hessian is the continuum remnant of the molecular
  incompressibility constraint. [`REPORT_MOLECULAR_REGULARITY.md`](../REPORT_MOLECULAR_REGULARITY.md),
  `figures/70` (`molecular_regularity.py`).
- **Energy conservation ⇏ regularity [theorem + solver test]** — the runnable
  version of the molecular note's central premise. The classical dyadic (shell) model
  (Katz–Pavlović 2005) conserves energy *exactly* (telescoping inter-shell flux,
  `max|dE/dt|=4.7e-10`) yet cascades to a **finite-time singularity**: `H¹` grows
  `>10⁴×` with energy conserved to `2e-5`, and the cascade-front time `t_front(N)`
  converges geometrically to `t*≈0.844` as `N→∞` (finite-time blowup, not a truncation
  artifact). NS dissipation (`γ=1`) regularizes (`H¹` bounded ~3.2); supercritical
  dissipation does not (Cheskidov 2008) — so *structure*, not the energy budget,
  carries regularity. This is Tao-2016 "same energy identity, still blows up" in a
  model you can run; a 1-D caricature, not a statement about 3-D NS.
  [`REPORT_DYADIC_BLOWUP.md`](../REPORT_DYADIC_BLOWUP.md), `figures/71`
  (`dyadic_blowup.py`).
- **Projection *is* the two clocks [solver test]** — the projection method of
  incompressible solvers is exactly the fast-clock elimination; the SPDE limit
  follows. `run_boussinesq.py`, `figures/22–24`.
- **New derived cross-relationships NR16–NR21 [numerical identity + solver test]** — linking the four new
  papers to each other + mainstream. NR16: power-law bursts (Paper 3) ⇒ 1/f^γ spectrum
  with γ=3−α (Lowen–Teich). NR17: power-law spectrum ⇒ growing temporal memory
  τ_int (Wiener–Khinchin), chaining Paper 3 → Paper 4. NR18: exact identity —
  Paper 2's exchange fraction = √⟨kₓ²/k²⟩ (buoyancy spectral anisotropy, verified to
  3e-16). NR19: Taylor/Green–Kubo — Paper 4's integrated memory time *is* an eddy
  diffusivity (dispersion vs autocovariance-integral agree to 1.6%, both match exact
  AR(1) theory). NR20: additive diffusivity D_total=D_fast+D_slow, with the slow clock
  carrying ~21× the transport at equal energy. NR21: DFA/Hurst exponent = (γ+1)/2,
  so the burst exponent predicts Paper 4's long-range-dependence H = (4−α_burst)/2.
  [`REPORT_NEW_RELATIONSHIPS.md`](../REPORT_NEW_RELATIONSHIPS.md)
  (`new_relationships.py`).
  The NR series continues to NR72; see [`REPORTS.md`](REPORTS.md) for the full index.
- **Non-Markovian multiscale ocean memory [observational, 3/4 pre-specified]** — ocean validation of
  the Mori–Zwanzig memory thesis on 28 long-record N. Atlantic Argo floats
  (temperature at 1000 dbar, ~7.5 yr each). The deseasonalized autocorrelation needs
  **two separated timescales** (τ_fast≈19 d, τ_slow≈165 d, ΔAIC=52, sep 8.9×) and
  decays slower than any AR(1); the Chapman–Kolmogorov excess C(3)−C(1)³>0 is robust
  (p=0.002). Lag-2 excess positive but marginal (p=0.044, reported honestly). A local
  Markov model is structurally insufficient — exactly what MZ predicts.
  [`REPORT_NONMARKOV_ARGO.md`](../REPORT_NONMARKOV_ARGO.md), `figures/75`
  (`nonmarkov_argo.py`, `run_nonmarkov_argo.py`).
- **Cascade lifetime & power-law energy transport [observational, 4/4 pre-specified]** —
  burst lifetimes of the fine-scale turbulent-activity envelope at WREF 2020.
  Pressure bursts are a scale-free **power law** (α≈2.0 over ~2.2 decades, preferred
  over exponential by ΔAIC≈1600, tail ≫ phase-randomized surrogate) with super-linear
  energy transport (E∝τ^β, β≈1.6) — 4/4 pre-specified. Temperature is **not** a clean
  power law (exponential-favored, ~2 hr characteristic convective scale) — an honest
  falsification; super-linear energy transport (β>1) still holds for both. The
  scale-free pressure clock vs the scaled temperature clock.
  [`REPORT_CASCADE_LIFETIME.md`](../REPORT_CASCADE_LIFETIME.md), `figures/74`
  (`cascade_lifetime.py`, `run_cascade_lifetime.py`).
- **Diagonal-band cascade structure [observational]** — the surface
  layer (a stratified turbulent fluid) builds a *local, intermittent* cross-scale
  cascade, measured as a band-coupling matrix φ_ij = corr(log envelope of octave i,
  octave j) on WREF 2020 1-min pressure + air temperature. φ is diagonal-band
  (diagonal-dominant, half-coupling within ~4–5 octaves) and far above its
  phase-randomized surrogate (φ(1) ≈ 0.29/0.38 vs ≈ 0) — the time-domain "energy yes,
  structure no". The two clocks differ: temperature is a clean local cascade
  (Spearman −0.99), pressure couples more broadly with a synoptic enhancement (the
  global clock). [`REPORT_CASCADE_STRUCTURE.md`](../REPORT_CASCADE_STRUCTURE.md),
  `figures/73` (`cascade_band_structure.py`, `run_cascade_structure.py`).
- **In-place pressure-mediated buoyancy exchange [solver test]** —
  a falsification-driven probe of *how* incompressible stratified flow moves
  buoyancy: the elliptic pressure splits the buoyancy force `F=(0,b')` into a removed
  gradient part and a surviving baroclinic torque `∂_x b'`. Pure vertical
  stratification is held statically in place (solenoidal fraction `2.3e-16`); the
  pressure response is non-local (`r50` ratio `1.84`); developed convection has zero
  net vertical mass flux but positive buoyancy flux (warm up / cold down); the
  mediation is an instantaneous linear elliptic functional (superposition `2.5e-16`,
  scaling slope `1.000`). [`REPORT_PRESSURE_BUOYANCY.md`](../REPORT_PRESSURE_BUOYANCY.md),
  `figures/72` (`pressure_buoyancy_exchange.py`).

## 3. The proofs and measured coefficients (the repair)

- **The theory [theorem]** — Mori–Zwanzig / projected-FDT closure generalizes
  K-theory at the operator level; K-theory is the memoryless, down-gradient,
  no-backscatter truncation. [`REPORT_THEORY.md`](../REPORT_THEORY.md).
- **The closure benchmark [solver test]** — 256² filtered DNS, exact SGS force vs
  three closures. Smagorinsky: transfer correlation **0.071**, purely dissipative
  (no backscatter), spectral cusp. Projected-FDT **oracle**: correlation **1.000**,
  solenoidal by construction, correct forward/backscatter partition — "energy AND
  structure". The projected-FDT eddy viscosity is measured from the truth, so it is
  an oracle, not a predictive closure; see `closure_aposteriori.py` for the
  predictive comparison. [`REPORT_CLOSURE.md`](../REPORT_CLOSURE.md),
  `figures/28–30` (`run_closure.py`).
- **The same verdicts in 3D, with vortex stretching active [solver test]** — Part 9c
  re-runs the identical benchmark in a 128³ forced incompressible DNS (convergence-
  checked at 128–192³): Smagorinsky stays purely dissipative, the spectrum-matched
  surrogate keeps the right energy but breaks solenoidality, and the projected-FDT
  oracle matches spectrum + divergence + transfer (as an oracle, not as a predictive
  closure). The 3D-only diagnostics — positive
  stretching production (`⟨ωSω⟩* = 0.168`, identically `0.000` in 2D),
  intermediate-eigenvector alignment (`e₂ ≈ 0.65`), and a backscatter volume
  fraction of **0.480** that Smagorinsky's positive eddy viscosity cannot
  represent (**0.000**) — are the structural features through which the
  singularity mechanism is expected to operate; the benchmark measures the
  diagnostics, not regularity. The `0.480` is the fraction of points with
  `Π<0` (the Gaussian-law form `Φ(−μ/σ)`); the 4.9% figure is the separate ratio
  `μ/σ`, not a fraction of injection. [`REPORT_CLOSURE3D.md`](../REPORT_CLOSURE3D.md),
  `figures/61–64` (`run_closure3d.py`).
- **RESULT 12 [solver test]** — the memory coefficient is real: `τ_c ≈ 0.02–0.03`,
  sign **+**, measured from the SGS eddy-diffusivity autocorrelation; bath weights
  closed (slow:fast = Stefan number). [`REPORT_GLE_COEFFICIENTS.md`](../REPORT_GLE_COEFFICIENTS.md),
  `figures/53` (`gle_coefficients.py`).
- **RESULT 13 [solver test]** — `τ_c` is a property of the *turbulence*, not of the
  scalar: identical across heat and salt despite a 100× molecular-diffusivity
  contrast (Le sweep). [`REPORT_SCALAR_CLOCK.md`](../REPORT_SCALAR_CLOCK.md),
  `figures/55` (`scalar_clock_universality.py`).
- **RESULT 15 [solver test]** — the clock-mismatch (CMN)
  correction `−τ_c·∇·(∂_t K_u ∇θ)` reduces transient error and vanishes in steady
  state, run inside an actual transient K-theory solver.
  [`REPORT_CMN_SOLVER.md`](../REPORT_CMN_SOLVER.md), `figures/60` (`cmn_solver_demo.py`).
- **Down-gradient / backscatter repair [theorem + solver test]** — the spatial companion of
  RESULT 15. [`nonlocal_flux_correction.py`](../nonlocal_flux_correction.py) makes the
  "down-gradient, no-backscatter truncation" failure concrete and drops in the fix.
  **THEOREM (proved + tested):** any local closure with a non-negative eddy
  diffusivity, `F = −κ(x)∇C` with `κ ≥ 0` (scalar or PSD tensor), has `F·∇C ≤ 0`
  *pointwise*, so the alignment `C_G = ⟨F·∇C⟩/⟨|F||∇C|⟩` is pinned at `−1` — it
  **cannot** represent the counter-gradient flux (`C_G > −1`) measured in RESULT 11
  ([`REPORT_CG_BUOYANCY.md`](https://github.com/abdh0saifelden2-debug/K2-subglacial-cavity/blob/792cbed31b3677bad51f1cfe4473405e5e877978/REPORT_CG_BUOYANCY.md) in `K2-subglacial-cavity`). The
  correction is a scale-dependent (nonlocal) eddy diffusivity `κ̂(k)` —
  `F̂ = −κ̂(k)(ik)Ĉ` — that admits backscatter (`κ̂ < 0` in a band); it reproduces the
  counter-gradient truth exactly while reducing to local Fick when `κ̂` is constant
  (the safe default). `tests/test_nonlocal_flux_correction.py`.
