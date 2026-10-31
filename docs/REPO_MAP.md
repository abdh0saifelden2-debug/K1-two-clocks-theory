# Repository map

This file is the rule for what may be touched in the v1.x line. It is
descriptive, not a refactor plan: **no file moves or renames are part of v1.x.**

## Invariants

- The paper builds from the repository root: [`paper0_two_clocks.tex`](../paper0_two_clocks.tex)
  and [`preamble.sty`](../preamble.sty). [`paper.yml`](../.github/workflows/paper.yml)
  runs XeLaTeX on the root file.
- Table 9 commands run from the root. The 22 `run_*.py` files are the runners;
  the paper cites 14 of them.
- Tests import the NR modules by filename (for example
  `import new_relationships45 as R`). Renaming them breaks imports and report
  links.
- Generated reports (`REPORT_CLOSURE.md`, `REPORT_ASOS.md`, `REPORT_STABILITY.md`,
  and the other `run_*.py` outputs) must be edited in their generator, not only
  in the report.
- [`AUDIT.md`](../AUDIT.md) keeps the pre-split `general_two_clocks/**` paths as
  history; [`tools/check_repo_paths.py`](../tools/check_repo_paths.py) exempts it
  and fails on any other stale reference.

## Counts at HEAD

- 468 tracked files; 184 root-level tracked files.
- 81 report files: 80 `REPORT_*.md` plus `REPORT.md`.
- 155 files under [`figures/`](../figures).
- 49 NR scripts: 46 `new_relationships*.py` plus 3 `nr*.py`.
- 22 `run_*.py` runners.
- 78 test files; 689 collected tests (688 passed, 1 skipped at HEAD).
- 7 analysis packages under `closure/`, `boussinesq/`, `compressible/`,
  `neon_pt/`, `asos/`, `reanalysis/`, `subglacial/`.

## Classes

| Class | Members | Rule |
|---|---|---|
| Paper surface | [`README.md`](../README.md), [`AUDIT.md`](../AUDIT.md), [`CLAIM_MAP.md`](../CLAIM_MAP.md), [`paper0_two_clocks.tex`](../paper0_two_clocks.tex), [`preamble.sty`](../preamble.sty), [`claims/`](../claims), [`tools/check_claim_map.py`](../tools/check_claim_map.py), [`paper.yml`](../.github/workflows/paper.yml) | Paper numbers are gated by `CLAIM_MAP.md`; do not change a gated number without the artifact and lint. |
| Paper runners | the 14 `run_*.py` commands in Table 9 | Must remain runnable from the root with fixed seeds. |
| Supporting runners | the other 8 `run_*.py` files and `closure_aposteriori*.py` | Supporting evidence; not all are cited by the paper. |
| Evidence reports | 80 `REPORT_*.md` plus `REPORT.md`; index in [`REPORTS.md`](REPORTS.md) | Do not rewrite historical numbers; annotate and supersede. |
| Exploratory | 49 NR scripts and their reports; `glaciers/`, `data/nr*` caches | Outside the paper's claim set; indexed as exploratory. |
| Analysis libraries | `closure/`, `boussinesq/`, `compressible/`, `neon_pt/`, `asos/`, `reanalysis/`, `subglacial/` | Imported by runners and tests; `AUDIT.md` records provenance. |
| Data and artifacts | [`figures/`](../figures), [`data/MANIFEST.md`](../data/MANIFEST.md) and 14 caches, [`claims/fc15_winter.json`](../claims/fc15_winter.json) | Raw data are not vendored; caches are derived. |
| Infrastructure | [`tests/`](../tests), [`tools/`](../tools), `.github/workflows/`, `pyproject.toml`, `requirements.txt` | CI runs the claim map, path guard, full pytest, and the PDF build. |

## Where the front-door claims live

- [`docs/FINDINGS.md`](FINDINGS.md) is the curated evidence list linked from the
  README. It is not the manuscript claim set; the manuscript is.
- [`docs/REPORTS.md`](REPORTS.md) is the complete report index, including the
  exploratory NR series.
- [`CLAIM_MAP.md`](../CLAIM_MAP.md) is the single numerical ledger. Do not add a
  second `CLAIMS.md`.
