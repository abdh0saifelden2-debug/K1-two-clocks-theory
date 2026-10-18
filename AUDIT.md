# Split audit — K1-two-clocks-theory

How this repository was carved out of the pristine **K** monorepo. Regenerate the classification with [`K-audit` v1.0](https://github.com/abdh0saifelden2-debug/K-audit/tree/v1.0) — `python3 classify.py --mono K K1-two-clocks-theory` — and re-check the import graph with `python3 verify_repo.py --mono K K1-two-clocks-theory` (both run from a clone of `K-audit` against a clone of the monorepo).

## Claim cluster

the observation, the two-clocks theory, and the closure benchmarks.

Source: `general_two_clocks/**` (theory + closure + observations + its 81-test suite, minus 3 relocated to K2) plus six files vendored from `glaciers/**` that the theory cluster imports.

## Composition

| | files |
|---|---|
| traced to a monorepo file | 451 |
| byte-identical copies | 448 |
| modified (see *Edits*) | 3 |
| new (not in the monorepo) | 1 |

The counts above are the split-time classification. The link fixes applied after the split (listed under *Edits*) change the byte-identity of additional report files but not the traced/new composition.

Source directories, by file count:

- `general_two_clocks/` — 173
- `general_two_clocks/figures/` — 153
- `general_two_clocks/tests/` — 78
- `general_two_clocks/data/` — 14
- `general_two_clocks/closure/` — 7
- `general_two_clocks/neon_pt/` — 4
- `general_two_clocks/reanalysis/` — 4
- `glaciers/subglacial/` — 4
- `(monorepo root)`/ — 3
- `general_two_clocks/asos/` — 3
- `general_two_clocks/compressible/` — 3
- `general_two_clocks/boussinesq/` — 2
- `glaciers/validation/synthetic/` — 2
- …plus 1 file(s) that sit alone in their source directory (top-level scripts, one-off reports)

## Vendored files

Copied byte-for-byte from the monorepo paths below (this is what makes the repo import-clean on its own):

- `repo root/*` (176 files)
- `asos/__init__.py`
- `asos/fetch_iem.py`
- `asos/loader.py`
- `boussinesq/__init__.py`
- `boussinesq/solver.py`
- `closure/*` (7 files)
- `compressible/__init__.py`
- `compressible/ns.py`
- `compressible/solver.py`
- `data/*` (14 files)
- `figures/*` (153 files)
- `neon_pt/__init__.py`
- `neon_pt/analysis.py`
- `neon_pt/loader.py`
- `neon_pt/stability.py`
- `reanalysis/__init__.py`
- `reanalysis/ncep.py`
- `reanalysis/rossby_clocks.py`
- `reanalysis/temporal_clocks.py`
- `subglacial/__init__.py`
- `subglacial/candidate2_doublediff.py`
- `subglacial/elliptic_demo.py`
- `subglacial/flow.py`
- `tests/*` (78 files)

## Edits

- `README.md` — rewritten to stand alone: no `../` links into sibling monorepo folders, run commands given from the repo root, and a Provenance section pointing at the archive.
- `pyproject.toml` — rewritten for this repo: `testpaths`/`pythonpath` scoped to this repo instead of all five monorepo domains, and the dependency list trimmed to the libraries this claim cluster imports.
- `requirements.txt` — rewritten for this repo: `testpaths`/`pythonpath` scoped to this repo instead of all five monorepo domains, and the dependency list trimmed to the libraries this claim cluster imports.
- Link fixes after the split: the `../papers/CROSS_RELATIONSHIPS_INDEX.md` links in 31 reports were un-linked (the text stays; the index is archive-only); the Bushuk links in `REPORT_NEW_RELATIONSHIPS26/28.md` now target the repo-local `glaciers/` copies; `REPORT_RB_RA_SWEEP.md` and `REPORT_BOUSSINESQ.md` bare figure names now point at `figures/`; `REPORT_SCALAR_CLOCK.md` points at the repo-local `subglacial/candidate2_doublediff.py`; `REPORT_CMN_SOLVER.md` and `REPORT_CLOSURE.md` link the K2-owned modules at their merge-commit permalinks.
- `REPORT_NEW_RELATIONSHIPS15.md`, `REPORT_NEW_RELATIONSHIPS18.md`, `REPORT_NEW_RELATIONSHIPS35.md` — relocation notes added, pointing NR33–NR35 at `K2-subglacial-cavity` at merge commit `792cbed`.

## Runtime note

- `new_relationships26.py` (NR49) and `new_relationships28.py` (NR51) read the author-provided Bushuk adjustment arrays from a path that is **not committed to the monorepo either** — they are unchanged by the split and have no tests.

## Relocated to K2

- `new_relationships10.py`, `new_relationships11.py`, `new_relationships12.py`
- `REPORT_NEW_RELATIONSHIPS10.md`, `REPORT_NEW_RELATIONSHIPS11.md`, `REPORT_NEW_RELATIONSHIPS12.md`
- `tests/test_new_relationships10.py`, `tests/test_new_relationships11.py`, `tests/test_new_relationships12.py`
- plus their `figures/nr3{3,4,5}_*` artifacts.
- — these three claim chains load `../glaciers/validation/**` figures and reports that belong to the K2 validation cluster, and the paper chain depends on their numbers (paper4a §6.4), so they now live in [`K2-subglacial-cavity`](https://github.com/abdh0saifelden2-debug/K2-subglacial-cavity/tree/792cbed31b3677bad51f1cfe4473405e5e877978) (merged at `792cbed`); K2's `AUDIT.md` records the relocation.

## Test-suite accounting

`tests/` carries **78 test files** (general_two_clocks/tests (81) − 3 relocated to K2); the whole monorepo has 136 test files across the five repos (78+39+15+2+2 = 136).

## Verification

[`K-audit`](https://github.com/abdh0saifelden2-debug/K-audit/tree/v1.0) `verify_repo.py` walks the **AST import graph** of every Python file in this repo, expands each unqualified import against every `sys.path` root the file would actually see, and reports any import that resolves only outside the repository. Result:

```
OK K1-two-clocks-theory: no external edges
```

## Provenance

Pristine snapshot taken **before** any edit: `K-monorepo-archive.tar.gz`, SHA-256 `ef637ff55f912a5d1404f677429f9429eccc8102a8cab23cee79cf055bbf1220` (also recorded in [`README.md`](README.md) and `K-monorepo-archive.sha256`). The archive is and remains the **frozen pre-edit reference** — no split or relocation edit is ever applied to it. `FUTURE_WORK.md` / `PAPER_OUTLINE.md` were deliberately left in the archive.
