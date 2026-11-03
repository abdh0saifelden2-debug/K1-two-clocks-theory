# Changelog

Release history for the paper0 manuscript and the K1 analysis repository. The
manuscript PDF is attached to each `paper0-v*` release. Entries describe what
changed between releases; the committed reports and `docs/FINDINGS.md` remain
the detailed record.

## Unreleased

### Added

- `run_closure.py` computes a 40-seed surrogate ensemble and writes
  `figures/28b_closure_seed_ensemble.json`; the closure report cites the
  median, standard deviation, and range instead of leaving the spread
  unmeasured.

### Changed

- The manuscript title now says **unconstrained** spectrum-matched closures, and
  the abstract, introduction, and Section 4.2 state that solenoidality is standard
  stochastic-backscatter practice rather than an overlooked constraint. New
  references: Leith (1990), Mason & Thomson (1992), Shutts (2005), Berner et al.
  (2009), Mémin (2014), Debussche, Hug & Mémin (2023), Kraichnan (1976), and
  Frederiksen & Kepert (2006).
- `REPORT_CLOSURE.md` labels the Otis, biomedical, and subglacial application
  section as speculative (no data), and qualifies the Smagorinsky `T(k) ≤ 0`
  statement to the reported realization.

### Fixed

- The cascade-structure and channel-closure generators now emit the same
  "load-bearing" wording as their checked-in reports. The wording lint scans
  the `run_*.py` report runners, so generator text cannot drift from the
  reports again.

## paper0 v1.0.4 — 2026-11-02

The first release after the hygiene cleanup. It includes the report, doc, and
tooling work below plus one manuscript erratum.

### Erratum

- Abstract: the divergent fraction is now stated as at most `4.0%` of the
  **rotational** kinetic energy in Reanalysis 1 (`4.5%` in the Reanalysis 2
  cross-check), not "`≤4%` of the kinetic energy". Table 5 and the results text
  already reported the ratio correctly; only the abstract's denominator and
  bound were wrong. `tools/check_claim_map.py` now gates this sentence against
  `figures/27b_reanalysis_crosscheck.json`.
- Abstract, introduction, and discussion: "proves" → "shows" for the 2-D
  surrogate demonstration, matching the scope paragraph.

Release PDF SHA-256: `84d023728b06f11a80d6f132ff3207e5ce6b139cdbc77fc88a582430c1bcd19c`.

### Changed

- Closure wording is conservative: the `0.907` transfer correlation is one
  fixed realization (`seed=7`), not a seed average, and the 3D convergence runs
  span `−0.276` to `+0.268`.
- Argo, cascade-lifetime, cascade-structure, pressure-buoyancy, and subglacial
  tests now use criteria-based labels instead of "pre-registered"; the
  thresholds are hard-coded and no external registry exists.
- ASOS P–T wording reports the measured range (`−0.56` to `−0.05`, median
  `−0.48`) instead of "close to zero", and says "consistent with" rather than
  "exactly as expected".
- `REPORT_THEORY.md` reports relative `RMS(∇·m)` and records that the
  `T(k)`-uncorrelated sub-prediction is not tested by a single seed.
- Singularity wording names the Constantin–Fefferman geometric-depletion
  diagnostics instead of a "recently-proved singularity mechanism".

### Added

- `docs/REPORTS.md`: all 81 report files, with a `runner`/`static` status column.
- `docs/REPO_MAP.md`: the v1.x invariants and checked counts.
- `tools/check_report_wording.py`: a CI guard for retired claim wording and
  report-index completeness.
- `Makefile` targets `check`, `test`, and `paper`.
- A leave-one-out calibration test for the R1/R2 reanalysis cross-check in
  `tests/test_reanalysis_crosscheck.py`.
- Figure-writing tests are isolated in `tmp_path`, so pytest no longer
  rewrites tracked `figures/*.json`.

## paper0 v1.0.3 — 2026-10-30

PDF layout/text fixes found by reading the released v1.0.2 PDF. No claim,
number, or figure changed.

- Fixed a clipped table row and a split footnote.
- Removed duplicate coherence text.

## paper0 v1.0.2 — 2026-10-30

Closed the submission-review items and extended the CI claim gate from three to
five checks.

- Kept the archive SHA-256 copyable in the PDF.
- Corrected the Fig. 14 same-level qualification and the channel-filter
  cutoff-units disclosure.

## paper0 v1.0.1 — 2026-10-23

Corrected claims identified by an independent audit and added the claim-map CI
gate.

- Fixed the F-C15 stability-bin labels.
- Added `tools/check_claim_map.py`, which checks gated prose numbers against
  committed artifacts.

## paper0 v1.0 — 2026-10-23

First CI-built PDF of `paper0_two_clocks.tex`.
