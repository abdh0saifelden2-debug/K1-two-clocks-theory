# Claim map and release lint

CI runs `python tools/check_claim_map.py` before `pytest`. The lint fails when a
checked paper number does not match its committed artifact or the verified
winter claim data in `claims/fc15_winter.json`.

| ID | Paper surface | Source of truth | Checked |
|---|---|---|---|
| F-C15 table | stability table, caption, footnote | `claims/fc15_winter.json`, `figures/01b_neon_seasonal.json`, `REPORT_STABILITY.md`, `neon_pt/stability.py` | class labels, bin edges, counts, medians, 5–95% brackets, ratios |
| F-C15 swing | §3 stability paragraph | `figures/01b_neon_seasonal.json` | winter `4.3x`, `0.77–3.28`; summer `5.9x`, `0.44–2.60` |
| F-C15 robustness | §3 parenthetical | `claims/fc15_winter.json` | coarse `±1.0` swing `5.6x`, counts `51/117/121/228/85` |
| O6 | §2 coherence, two locations | `figures/09b_asos_ci.json` | 12 h range, CAR/DSM/SEA 24 h values, surrogate thresholds |
| R3 | §5 cross-check | `figures/27b_reanalysis_crosscheck.json` | maximum relative difference `15.5%` |

The map is deliberately small: a claim is gated only if it appears above. When a
new claim is added, add its artifact and check to this table and to
`tools/check_claim_map.py` in the same change. A mismatch is a release blocker,
not a formatting issue.
