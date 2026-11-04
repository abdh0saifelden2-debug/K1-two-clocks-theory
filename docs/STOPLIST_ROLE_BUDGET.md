# Stop-list check for the role-budget program

**Status:** checked 2026-11-04, before the pre-specification freeze.
**Scope:** the four entries named in the role-budget discussion, the later
Perezhogin--Glazunov paper, and the closest 2025--2026 hit found during the
check.
**Verification level:** bibliographic metadata from Crossref; abstracts from
the publisher, Crossref, or arXiv; full text read for Tuteri et al. (2026).
The other entries were not read in full, so the statements below describe what
their abstracts and metadata establish, not a complete literature review.

## What was checked

| Entry | Verified citation | What it establishes (abstract-level) | Overlap with this program | Not done there |
|---|---|---|---|---|
| Perezhogin, Glazunov & Gritsun (2019) | *Russ. J. Numer. Anal. Math. Modelling* **34**(4), 197--213, doi:10.1515/rnam-2019-0017 | A priori analysis of subgrid forces in forced 2D turbulence; constructs deterministic (negative-viscosity) and stochastic (autoregressive) kinetic-energy backscatter closures; a proper combination improves spectra, lagged autocorrelations, and sensitivity to perturbations | The broad "what does randomness add beyond a deterministic closure?" question, and the deterministic-plus-stochastic composite | No held-out comparison of oracle versus operational noise calibration; no per-scale conditional-mean/residual distributional budget; no matched-amplitude random-phase versus phase-aligned reconstruction |
| Perezhogin & Glazunov (2023) | *J. Adv. Model. Earth Syst.* **15**(10), e2023MS003771, doi:10.1029/2023MS003771; arXiv:2304.06789 | Germano decomposition of subgrid fluxes in barotropic decaying turbulence: Leonard and Cross stresses carry enstrophy dissipation, Reynolds stress carries kinetic-energy backscatter; a three-part deterministic model reproduces energy and enstrophy transfer and improves a posteriori statistics | A role decomposition of the subgrid force, a priori and a posteriori, in 2D turbulence | The decomposition is by stress component (Leonard/Cross/Reynolds), not by conditional mean versus residual; no stochastic residual, no calibration-mode comparison, no matched-energy phase controls |
| Frederiksen & Kepert (2006) | *J. Atmos. Sci.* **63**(11), 3006--3019, doi:10.1175/JAS3795.1 | DNS-based stochastic backscatter, eddy drain viscosity, and net eddy viscosity for 2D barotropic turbulence on the sphere; LES with the DNS-calibrated parameterizations matches higher-resolution DNS spectra | The composite baseline: a deterministic drain plus calibrated random forcing, with the random part calibrated from high-resolution truth | Calibration is from DNS truth, not held out; no operational-versus-oracle calibration gap; no per-scale role budget or matched-energy phase comparison |
| Schumann (1995) | *Proc. R. Soc. Lond. A* **451**(1941), 293--318, doi:10.1098/rspa.1995.0126 | Stochastic SGS model with realizable random stresses built from Gaussian random fields; random components reduce stress--strain correlations to 0.16--0.5; backscatter requires finite temporal correlation; LES of isotropic turbulence reproduces expected decay | The stress--strain alignment measurement; the finite-correlation-time requirement; the stochastic-backscatter model itself | The alignment is reported as a correlation range, not a per-scale distributional budget; no exact-force decomposition; no oracle-versus-operational calibration comparison |
| Domaradzki & Saiki (1997); the "Domaradzki 1996" item | *Theor. Comput. Fluid Dyn.* **9**(2), 75--83, doi:10.1007/s001620050033. The 1996 item is the DTIC report *Subgrid Scale Models with Backscatter* (ADA317679), which lists the journal paper as submitted | Deterministic backscatter models derived from the statistics of interscale energy transfer | Deterministic backscatter, i.e. the "maximally aligned deterministic twin" is not a new idea | No stochastic residual, no calibration modes, no matched-amplitude phase comparison |
| Tuteri, Alexakis & Chibbaro (2026) | *J. Fluid Mech.* **1027**, A39, doi:10.1017/jfm.2025.11087; arXiv:2507.17575 | 3D DNS with Gaussian filtering; local energy flux conditioned on the Clark and Smagorinsky predictions; Clark captures the conditional mean flux, but fluctuations are of the order of the mean with fat tails; conditional PDFs, cumulants, and joint PDFs show non-Gaussian heavy tails; concludes that a stochastic framework is needed | **The closest prior art.** The core observation that a deterministic gradient model carries the conditional mean while the residual carries variance and heavy tails is already published, with conditional statistics, in 3D isotropic turbulence | No stochastic reconstruction, no oracle-versus-operational calibration, no matched-amplitude random-phase versus phase-aligned twin, no sharp-cutoff 2D exact-force benchmark; stationary statistics only, and the authors explicitly defer temporal correlations |

## What the check changes

1. **The broad question is not novel.** Perezhogin et al. (2019) already combine
   deterministic and stochastic backscatter and ask what the combination buys.
   A paper whose thesis is "deterministic versus stochastic" would be
   incremental.
2. **The mean/variance/tail role observation is not novel.** Tuteri et al.
   (2026) already show that the Clark model captures the conditional mean flux
   while the fluctuations around it are large, non-Gaussian, and heavy-tailed.
   That observation cannot be the headline.
3. **The stress--strain alignment measurement is not novel.** Schumann (1995)
   already reports the reduction of stress--strain correlations by random SGS
   motions, and already ties backscatter to finite correlation times.
4. **The "maximally aligned deterministic twin" is close to deterministic
   backscatter.** Domaradzki & Saiki (1997) derive deterministic backscatter
   models, and later ocean work combines deterministic and stochastic
   backscatter. A deterministic twin is a bound and a baseline, not a new
   closure principle.
5. **The stop-list citation "Domaradzki 1996" is a report, not the
   peer-reviewed paper.** The journal version is Domaradzki & Saiki (1997).
   Cite the 1997 paper and, if the report is used, label it as a report.

## What survives

The surviving contribution is narrow and should be written that way:

- a **held-out calibration-mode comparison**: oracle shell spectrum from the
  test realization versus operational shell spectrum from the calibration
  realization, with the gap between them reported as a quantity;
- a **matched-amplitude reconstruction hierarchy**: shell-spectrum Gaussian
  noise, per-mode-amplitude random-sign noise, and a phase/sign-aligned upper
  bound, which separates calibration, amplitude intermittency, and sign
  structure;
- the **sharp-cutoff 2D exact-force setting**, which is not the Gaussian-filtered
  3D setting of Tuteri et al. and which makes the sign structure of a
  solenoidal force a binary, exactly computable object;
- the **reproducible, claim-mapped package**, with the generator, artifact, and
  report committed together.

This is a benchmark and protocol contribution, not a new closure principle. If
the calibration gap is small and the random-sign reconstruction closes the
residual, the result is a negative/validation benchmark; that outcome is
pre-specified as acceptable.

## What is not claimed

- No exhaustive literature search. The searches were targeted, and "not found"
  is not evidence of absence.
- No full-text reading of Frederiksen & Kepert (2006), Schumann (1995),
  Perezhogin et al. (2019), Perezhogin & Glazunov (2023), or Domaradzki &
  Saiki (1997). Their descriptions above are abstract-level.
- No claim that the remaining contribution is sufficient for a stand-alone
  paper. The pre-specification defines the test and the kill conditions; the
  result decides whether the program continues.
