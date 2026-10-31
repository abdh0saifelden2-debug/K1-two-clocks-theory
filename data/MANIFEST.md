# Data manifest

Every external input used by the committed results, where it comes from, which
subset is used, and whether it is stored in this repository.

**No raw field, reanalysis, Argo, or simulation data are vendored.** The
repository ships derived JSON caches and figures only. Each section below gives
the public source and the window used, so the caches can be rebuilt.

---

## 1. External inputs

| ID | Dataset | Subset used | Access | Vendored |
|---|---|---|---|---|
| NEON | NEON bundled eddy covariance, product `DP4.00200.001` | Site `WREF` (45.820 N, 121.952 W, 351 m), months `2020-01` and `2020-07`, 30-min records | <https://data.neonscience.org/data-products/DP4.00200.001> | No (`.h5` bundle) |
| ASOS | IEM 1-minute ASOS archive (`tmpf`, `pres1`) | 8 stations `EYW, MIA, MSY, DFW, PHX, DSM, CAR, SEA`; 2020-01-01 to 2020-04-01 UTC | <https://mesonet.agron.iastate.edu/request/asos/1min.phtml> | No (CSV) |
| NCEP-R1 | NCEP/NCAR Reanalysis 1 | 2021 daily means, `t0=100`, `nt=24`, levels 850/500/250 hPa; one 6-hourly snapshot at 850 hPa | <https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis> | No (OPeNDAP) |
| NCEP-R2 | NCEP-DOE Reanalysis 2 | Same window, levels, and variables as R1 | <https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis2> | No (OPeNDAP) |
| WELL | The Well `rayleigh_benard`, 2D RB, `Pr = 1`, test split | `Ra = 1e6, 1e7, 1e8`; grid 512 x 128; 5 trajectories x 200 steps per Ra | <https://github.com/PolymathicAI/the_well> · <https://polymathic-ai.org/the_well/datasets/rayleigh_benard/> | No (`rb_Ra*_Pr1_test.hdf5`) |
| ARGO | Argo core profile files from the public GDAC | 28 North Atlantic floats, 25-45 N / 20-65 W; temperature at 1000 dbar; one value per ~10-day cycle | <https://doi.org/10.17882/42182> · <https://ftp.ifremer.fr/ifremer/argo> | No (`*_prof.nc`) |

Notes:

- **NEON.** The winter entry in `figures/01b_neon_seasonal.json` was regenerated
  from NEON release 2026; the summer entry is the earlier 2020-07 artifact. See
  `REPORT_NEON_SEASONS.md` for the 0.03 m sensor-depth difference.
- **ASOS.** `asos/fetch_iem.py` downloads the eight-station ladder; the committed
  three-station table in `REPORT_ASOS.md` is the original subset.
- **NCEP.** `reanalysis/ncep.py` fetches on demand and caches under
  `data_reanalysis/` (git-ignored). `run_reanalysis_r2.py` uses the same window
  (`YEAR, T0, NT = 2021, 100, 24`).
- **The Well.** Files are read from `--data-dir`; see `run_rb.py` and
  `run_rb_ra_sweep.py`.
- **Argo.** `run_nonmarkov_argo.py` reads `$ARGO_FLOATS_DIR` (default
  `data/argo_floats`). The GDAC DOI above is the dataset-level DOI; add the
  monthly snapshot key for a fully pinned citation.

## 2. Derived caches in `data/`

These files are committed so tests and reports run without network access.

| File | Produced by | Upstream source |
|---|---|---|
| `atl15_lake_dh_cache.json` | `new_relationships40.py` | ATL15 lake dynamic height (NSIDC) |
| `nr39_eeg_gate_cache.json` | `nr39_eeg_gate.py` | EEG gate series |
| `nr42_gb_archive_cache.json` | `nr42_gb_archive.py` | Geomagnetic observatory archive |
| `nr45_andro_gser_cache.json` | `new_relationships22.py` | ANDRO Argo displacements |
| `nr46_solar_cache.json` | `new_relationships23.py` | Solar / space-weather series |
| `nr47_memory_phase_cache.json` | `new_relationships24.py` | Derived phase series |
| `nr48_minphase_cache.json` | `new_relationships25.py` | Derived minimum-phase series |
| `nr52_odd_spin_cache.json` | `new_relationships34.py` | Derived spin series |
| `nr53_spin_bands_cache.json` | `new_relationships30.py` | Derived spin-band series |
| `nr54_spin_drift_cache.json` | `new_relationships31.py` | Derived spin-drift series |
| `nr56_stokes_cache.json` | `new_relationships33.py` | Derived Stokes series |
| `nr68_msis_cache.json` | `new_relationships45.py` | MSIS model output |
| `nr71_iri_cache.json` | `build_nr71_iri_cache.py` | IRI model output |
| `nr72_f2peak_cache.json` | `build_nr72_f2peak_cache.py` | Ionospheric F2-peak series |

The NR-series items are exploratory; see `docs/FINDINGS.md` and the matching
`REPORT_*.md` files.

## 3. Gated artifacts

These four artifacts are referenced by `CLAIM_MAP.md` and checked by
`tools/check_claim_map.py`. Hashes pin the exact bytes used for the v1.0.3
release.

| Artifact | SHA-256 | MD5 |
|---|---|---|
| `claims/fc15_winter.json` | `6f2271d46c926820d35a9df267de220e0226df5fdc3e81abed8bc459ac8db7ef` | `88cc3abd90395064fa8c72e56629a957` |
| `figures/01b_neon_seasonal.json` | `74050a2b1953d6a04e6e3a89df986e8acfc42cf1d02a348f827aaaaaa5b9009f` | `ce9f880de4d51a3590cefd2c6de9fafb` |
| `figures/09b_asos_ci.json` | `194402c65692ca16b60a2231769321bd28f9b768db12032285ac1a82217b0e07` | `2096e35effafcc342a7de2c9609e6094` |
| `figures/24b_spde_common_phase.json` | `49e6aa9a3f8927ea41321c303c9f50739002ec129094d073c6669f8f14fefe55` | `a15bb735db31a076c0d43fd15ee20300` |

Verify with:

```bash
sha256sum claims/fc15_winter.json figures/01b_neon_seasonal.json \
          figures/09b_asos_ci.json figures/24b_spde_common_phase.json
```

## 4. Known gaps

- **Argo float IDs are not archived.** The 28 float WMO IDs used for
  `REPORT_NONMARKOV_ARGO.md` were not saved, so the exact float set cannot be
  reconstructed from this repository. The selection rule is recorded (North
  Atlantic, 25-45 N / 20-65 W, long records, temperature at 1000 dbar); a rerun
  on today's GDAC may select a different set. Do not treat the reported 28-float
  ensemble as a permanently pinned sample.
- **Raw-input checksums are not recorded.** The NEON HDF5 bundle, ASOS CSVs,
  NCEP OPeNDAP extracts, The Well HDF5 files, and Argo NetCDF files were not
  retained, so their byte-level hashes are unavailable. Only the committed
  derived artifacts are pinned (section 3).
- **Paper DOI.** No Zenodo DOI has been minted for the manuscript; cite the
  `paper0-v1.0.3` release URL until one exists.
