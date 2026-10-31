# K1 — Two clocks: pressure–temperature decoupling across scales

Code, data artifacts, and manuscript for **paper0**, *Why spectrum-matched
stochastic closures fail the elliptic test: operator-level pressure–temperature
decoupling across scales*.

**Current release:** [`paper0-v1.0.3`](https://github.com/abdh0saifelden2-debug/K1-two-clocks-theory/releases/tag/paper0-v1.0.3)
(2026-10-30, commit `a0b6a45`). The released PDF is attached to that release.

**Thesis.** Temperature is a local, slow, parabolic field. Pressure, in the
incompressible limit, is the Lagrange multiplier of the divergence-free
constraint: a global, boundary-aware elliptic field. Matching the power
spectrum of an elliptic correction does not reproduce its action as a
constraint. Spectral equivalence is not dynamical equivalence.

## The paper in one table

| Setting | Result | Evidence |
|---|---|---|
| Field data: NEON WREF and ASOS | Daily P–T correlation is weak and regime-dependent (+0.07 in winter, −0.49 in summer). The 12 h pressure tide decays monotonically from 1.10 hPa at 24.6°N to 0.34 hPa at 47.4°N across eight stations. | Observational |
| Rayleigh–Bénard DNS, `Ra = 10^6–10^8`, `Pr = 1` | Pressure and buoyancy share the integral scale, but pressure's Taylor microscale is 2.6–4.5× larger; the high-wavenumber gap widens by about 70× across the sweep. | Solver test |
| Linear acoustics | The compressible pressure relaxes to the Poisson field with `t90 ≈ 2.3 L/c` under the fixed damping-per-crossing convention `γ = 1.5c/L`. The final state is independent of `c`. | Solver test |
| Nonlinear compressible sweep | The dilatational energy fraction scales as `M²`; the acoustic-averaged pressure approaches the elliptic solution. | Solver test |
| NCEP/NCAR Reanalysis 1 and 2 | The divergent-to-rotational kinetic-energy ratio is 4.0–4.5% at 850 hPa, with a minimum at 500 hPa (R1 0.7%, R2 0.8%). | Observational |
| Surrogate test: 2D Boussinesq, plus 3D and wall checks | A phase-randomized field with the identical power spectrum leaves RMS divergence `3.7 × 10⁻²` versus `2.7 × 10⁻²` for the uncorrected drift; the true projection reaches `2 × 10⁻¹⁵`. The common-phase control still leaves `3.66 × 10⁻²` (`1.33×`). | Solver test |
| Lean 4 ledger | Finite-dimensional DFT/Parseval, antipodal-phase, and discrete-Leray statements are machine-checked; the spectral divergence ledger is exact. | Theorem |

**Scope.** The central surrogate demonstration is two-dimensional and periodic.
A three-dimensional periodic DNS and a wall-bounded channel operator test extend
the verdict beyond the box, but the paper makes no 3-D regularity claim and no
forecast-skill claim. The reanalysis is model-assimilated and limited to
spherical-harmonic degree `l ≤ 35`.

## Evidence levels

| Level | Meaning |
|---|---|
| **Theorem** | Proved analytically or machine-checked in Lean 4. |
| **Numerical identity** | Exact discrete or algebraic identity checked to floating-point precision. |
| **Solver test** | Deterministic numerical experiment: DNS, acoustics, or a closure benchmark. |
| **Observational** | Field or reanalysis data, with sample size, site, period, and confidence intervals reported. |
| **Exploratory** | Outside the manuscript's claim set; indexed in [`docs/FINDINGS.md`](docs/FINDINGS.md). |

## Repository map

- `paper0_two_clocks.tex` — the manuscript. CI builds it with XeLaTeX and attaches the PDF to `paper0-v*` releases.
- `CLAIM_MAP.md` — claim-to-code/test/artifact map; `tools/check_claim_map.py` is the CI gate.
- [`docs/FINDINGS.md`](docs/FINDINGS.md) — the detailed findings moved out of this README.
- [`docs/REPO_MAP.md`](docs/REPO_MAP.md) — what belongs to the paper surface, the evidence reports, and the exploratory tail.
- [`docs/REPORTS.md`](docs/REPORTS.md) — index of all 81 report files.
- `run_*.py` — reproduction runners; Table 9 of the paper lists the command for every result.
- `closure/`, `boussinesq/`, `compressible/`, `neon_pt/`, `asos/`, `reanalysis/` — analysis libraries.
- `figures/`, `data/`, `claims/`, `tests/` — artifacts, caches, gated claim data, and the test suite.
- `REPORT_*.md` — 80 reports, plus `REPORT.md` (81 report files total); see [`docs/REPORTS.md`](docs/REPORTS.md).

## Reproduce

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m pytest            # 688 passed, 1 skipped at HEAD (683 passed at v1.0.3)
python run_closure.py --out-dir figures
```

Raw inputs are listed in [`data/MANIFEST.md`](data/MANIFEST.md); no raw
NEON, ASOS, NCEP, or Argo data are vendored. To rebuild the PDF, run `xelatex`
twice on `paper0_two_clocks.tex`.

## Status and provenance

- **Paper:** v1.0.3, released from `a0b6a45`; PDF SHA-256 `03e629b145dd6fbbf47b98488fbcd25fd1f3ca2f400691998149bbdc6865e9e4`.
- **Lean:** the finite-dimensional surrogate slice is frozen at `249e357` (Parseval freeze) and audited against `553d5c2` in [`K1-lean`](https://github.com/abdh0saifelden2-debug/K1-lean).
- **Audit:** the public code and claim audit is [`paper0-audit`](https://github.com/abdh0saifelden2-debug/paper0-audit).
- **Provenance:** split from the K monorepo; the pristine archive SHA-256 is `ef637ff5f912a5d1404f677429f9429eccc8102a8cab23cee79cf055bbf1220`. Split details are in [`AUDIT.md`](AUDIT.md).

## Citation

Cite the `paper0-v1.0.3` release and this repository. A Zenodo DOI has not been
minted; use the release URL until one exists.
