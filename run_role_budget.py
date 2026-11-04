"""Run the frozen role-budget decomposition and write the artifact + report.

Protocol: ``docs/PRESPEC_ROLE_BUDGET.md`` (tag ``paper0-roles-prespec-v1``).
Execution is on Kaggle, not on the laptop, per the repository's machine
constraint.  The generator is deterministic given the seeds.

    python run_role_budget.py --out-dir figures --report REPORT_ROLE_BUDGET.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from compressible.ns import Spectral2D  # noqa: E402
from closure.role_budget import (  # noqa: E402
    BUDGET_KEYS,
    CLARK_FIXED,
    CS_SMAG,
    compute_direction,
    prepare_realization,
    summarise_decision,
)

N_DNS = 256
KC = 32
STEPS = 6000
DNS_SEEDS = (42, 43, 44)
N_SEED = 32
N_BOOT = 200
PROTOCOL_SHA256 = "c02735bb034ea704ec686aa419dbb14e0154252f9aa7c70007a6517acc4d4322"
PROTOCOL_TAG = "paper0-roles-prespec-v1"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def _json_safe(value):
    """Replace non-finite floats with None so the artifact is strict JSON."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


# ---------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------

def make_figure(data: dict, path: str) -> None:
    directions = data["directions"]
    bands = ("L", "H")
    colors = {"E_cal": "#1f77b4", "E_amp": "#ff7f0e", "E_sign": "#2ca02c"}
    labels = {"E_cal": "calibration", "E_amp": "amplitude", "E_sign": "sign"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for col, band in enumerate(bands):
        ax = axes[0, col]
        x = np.arange(len(directions))
        width = 0.24
        for i, key in enumerate(("E_cal", "E_amp", "E_sign")):
            vals = np.array([d["bands"][band]["budget"][key] for d in directions])
            lo = np.array([d["bands"][band]["interval"][key][0] for d in directions])
            hi = np.array([d["bands"][band]["interval"][key][1] for d in directions])
            yerr = np.vstack([np.maximum(vals - lo, 0.0), np.maximum(hi - vals, 0.0)])
            ax.bar(x + (i - 1) * width, vals, width, yerr=yerr, capsize=3,
                   color=colors[key], edgecolor="k", linewidth=0.5,
                   label=labels[key])
        ax.axhline(0.0, color="k", lw=0.6)
        ax.set_xticks(x, [f"dir {d['direction']}\n{d['fit']}/{d['cal']}/{d['test']}"
                          for d in directions])
        ax.set_ylabel("normalized budget component")
        ax.set_title(f"Additive budget, band {band}")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(fontsize=8)
        for d_i, d in enumerate(directions):
            ax.text(d_i, ax.get_ylim()[1] * 0.92,
                    f"$E_{{tot}}$={d['bands'][band]['budget']['E_total']:+.2f}",
                    ha="center", fontsize=8)

        ax = axes[1, col]
        names = ("ops", "shell", "mode", "pos", "exact")
        pretty = ("d+R_ops", "d+R_shell", "d+R_mode", "d+R_pos", "exact")
        vals = []
        err_lo = []
        err_hi = []
        for name in names:
            c = np.array([d["bands"][band]["closure"][name] for d in directions])
            vals.append(float(c.mean()))
            err_lo.append(float(c.mean() - c.min()))
            err_hi.append(float(c.max() - c.mean()))
        ax.bar(np.arange(len(names)), vals,
               yerr=np.vstack([err_lo, err_hi]), capsize=4,
               color=["#9467bd", "#1f77b4", "#ff7f0e", "#d62728", "black"],
               edgecolor="k", linewidth=0.5)
        ax.axhline(0.0, color="k", lw=0.6)
        ax.axhline(1.0, color="gray", lw=0.6, ls="--")
        ax.set_xticks(np.arange(len(names)), pretty, rotation=15, fontsize=8)
        ax.set_ylabel("closure fraction C = 1 - W1/W1(d)")
        ax.set_title(f"Closure fractions, band {band} (mean and range over directions)")
        ax.grid(True, axis="y", alpha=0.3)

    fig.suptitle("Role budget of the deterministic subgrid residual "
                 "(frozen protocol, 2D exact-force benchmark)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(path, dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _f(value: float, digits: int = 3) -> str:
    return "n/a" if value is None or not np.isfinite(value) else f"{value:+.{digits}f}"


def _u(value: float, digits: int = 3) -> str:
    return "n/a" if value is None or not np.isfinite(value) else f"{value:.{digits}f}"


def render_report(data: dict) -> str:
    cfg = data["config"]
    directions = data["directions"]
    decision = data["decision"]
    lines = []
    add = lines.append

    add("<!-- GENERATED by run_role_budget.py from figures/31_role_budget.json.")
    add("     Do not edit numbers by hand; re-run the generator instead. -->")
    add("")
    add("# Report: the role budget of a deterministic subgrid residual")
    add("")
    add(f"**Protocol:** [`{data['protocol']['file']}`]({data['protocol']['file']}) "
        f"(tag `{data['protocol']['tag']}`, SHA-256 "
        f"`{data['protocol']['sha256']}`).")
    add(f"**Generated (UTC):** {data['utc']}  ")
    add(f"**Git commit:** `{data['git_commit']}`  ")
    add(f"**Artifact:** [`figures/31_role_budget.json`](figures/31_role_budget.json)")
    add("")
    add("## Summary")
    add("")
    add(f"Frozen protocol, {cfg['n']}\u00b2 2D DNS, sharp cutoff `kc = {cfg['kc']}`, "
        f"three DNS realizations (seeds {cfg['dns_seeds']}), "
        f"{cfg['n_seed']} stochastic seeds and {cfg['n_boot']} bootstrap resamples.")
    add("The deterministic arm is D2 (Clark/gradient, coefficient fitted on the "
        "fit realization). The budget is")
    add("")
    add("```")
    add("E_total = W1(d + R_ops) / W1(d)")
    add("E_cal   = [W1(d + R_ops) - W1(d + R_shell)] / W1(d)")
    add("E_amp   = [W1(d + R_shell) - W1(d + R_mode)] / W1(d)")
    add("E_sign  = W1(d + R_mode) / W1(d)")
    add("```")
    add("")
    add(f"**Mechanical verdict:** `{decision['verdict']}`. "
        f"**Phase-aware closure:** `{decision['phase_aware_closure']}`.")
    add("")
    primary = directions[0]
    shares = []
    for band in ("L", "H"):
        b = primary["bands"][band]
        total = b["budget"]["E_total"]
        sign = b["budget"]["E_sign"]
        share = (sign / total if total not in (None, 0.0)
                 and sign is not None
                 and np.isfinite(total) and np.isfinite(sign) else None)
        shares.append(f"`{band}`: E_sign/E_total = {_u(share)}, "
                      f"C_ops = {_f(b['closure']['ops'])}")
    add("In the primary direction, " + "; ".join(shares) + ". "
        "`C_ops < 0` means the operational random-phase reconstruction is "
        "worse than the deterministic arm `d`; the budget then says which "
        "missing information the operational model failed to supply.")
    add("")
    add("## 1. Data and held-out split")
    add("")
    add("| direction | fit `d` | calibrate `E_ops` | test | D2 `C` | "
        "`Z_test/Z_cal` |")
    add("|---|---|---|---|---|---|")
    for d in directions:
        add(f"| {d['direction']} | {d['fit']} | {d['cal']} | {d['test']} | "
            f"{_f(d['clark_C'])} | {_u(d['Z_ratio'])} |")
    add("")
    add("The test truth is never used for fitting or for the operational "
        "spectrum. `R_ops` rescales the calibration residual shell spectrum by "
        "`Z_test/Z_cal`; `R_ops_raw` is the no-rescale sensitivity.")
    add("")
    add("The pre-spec's section 3 uses the phrase \"calibration realization\" "
        "for the coefficient fits. This implementation follows the section 2 "
        "three-way split: `C` and `nu_t(k)` are fitted on the fit realization, "
        "and the separate calibration realization supplies `E_r(k)` for "
        "`R_ops`. No test truth enters either stage.")
    add("")
    add("## 2. Deterministic arms")
    add("")
    add(f"D1 is Smagorinsky with `Cs = {cfg['cs_smag']}`. D2 is the Clark/"
        "gradient model with `C` fitted by least squares on the fit "
        f"realization; the fixed `C = 1/12 = {CLARK_FIXED:.6f}` is a "
        "sensitivity. D3 is the shell-wise spectral eddy viscosity fitted to "
        "the fit-realization transfer; its sign is unconstrained.")
    add("")
    add("| direction | arm | W1 L | W1 H |")
    add("|---|---|---|---|")
    for d in directions:
        for arm in ("D0", "D1", "D2", "D2_fixed", "D3"):
            add(f"| {d['direction']} | {arm} | "
                f"{_u(d['arm_w1'][arm]['L'])} | {_u(d['arm_w1'][arm]['H'])} |")
    add("")
    add("### H1: mean-transfer error")
    add("")
    add("Relative band-mean transfer error `|T_model - T_truth| / |T_truth|` "
        "(report, do not gate).")
    add("")
    add("| direction | band | D1 | D2 | D3 |")
    add("|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            row = d["bands"][band]["mean_transfer_error"]
            add(f"| {d['direction']} | {band} | {_u(row['D1'])} | "
                f"{_u(row['D2'])} | {_u(row['D3'])} |")
    add("")
    add("## 3. Residual floor (H2)")
    add("")
    add("The budget is interpreted only where `W1(d) > 0.05`.")
    add("")
    add("| direction | band | W1(d) | floor met |")
    add("|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            w = d["bands"][band]["W1"]["d"]
            met = w is not None and w > 0.05
            add(f"| {d['direction']} | {band} | {_u(w)} | "
                f"{'yes' if met else 'no'} |")
    add("")
    add("Skipped shells (zero truth RMS): " + ", ".join(
        f"dir {d['direction']} total {d['skipped_shells']['count']} "
        f"(L {d['bands']['L']['skipped_shells']}, "
        f"H {d['bands']['H']['skipped_shells']})"
        for d in directions) + ".")
    add("")
    add("## 4. Additive budget")
    add("")
    add("### Point estimates")
    add("")
    add("| direction | band | E_total | E_cal | E_amp | E_sign | ranking |")
    add("|---|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            b = d["bands"][band]
            ranking = decision["material_rankings"][band][d["direction"] - 1]
            add(f"| {d['direction']} | {band} | {_f(b['budget']['E_total'])} | "
                f"{_f(b['budget']['E_cal'])} | {_f(b['budget']['E_amp'])} | "
                f"{_f(b['budget']['E_sign'])} | "
                f"{', '.join(ranking) if ranking else 'none resolved material'} |")
    add("")
    add("### Unresolved components")
    add("")
    add("A component whose 5--95 width exceeds 50% of its point estimate is "
        "reported as unresolved and is excluded from the material ranking. "
        "The `unresolved_noise_primary` flag records any such component in the "
        "primary direction; `unresolved_material_primary` records the subset "
        "that is also labelled material, which is the condition that changes "
        "the verdict to `unresolved_noise`.")
    add("")
    add("| direction | band | unresolved components |")
    add("|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            keys = decision["unresolved_components"][band][str(d["direction"])]
            add(f"| {d['direction']} | {band} | "
                f"{', '.join(keys) if keys else 'none'} |")
    add("")
    add("### Intervals and labels")
    add("")
    add("The interval is the combined 5--95 range from the joint mode-bootstrap "
        "and seed draw. A negative component is reported as adverse and is not "
        "clipped. A component is **material** if its point estimate is at least "
        "`0.10 E_total` and its 5--95 range lies entirely above "
        "`0.05 E_total`; **negligible** if its point estimate is below "
        "`0.05 E_total`; otherwise **unresolved**. If `E_total <= 0` the "
        "material labels are not applied. Rankings list material components "
        "by point estimate, descending.")
    add("")
    add("| direction | band | component | estimate | 5--95 | label |")
    add("|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            b = d["bands"][band]
            for key in BUDGET_KEYS:
                lo, hi = b["interval"][key]
                add(f"| {d['direction']} | {band} | {key} | "
                    f"{_f(b['budget'][key])} | [{_f(lo)}, {_f(hi)}] | "
                    f"{b['labels'][key]} |")
    add("")
    add("### Closure fractions")
    add("")
    add("`C = 1 - W1(model)/W1(d)`. `C = 1` is exact distributional "
        "reproduction; `C = 0` is no improvement over `d`.")
    add("")
    add("| direction | band | R_ops | R_ops_raw | R_shell | R_mode | R_pos | "
        "R_exact |")
    add("|---|---|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            c = d["bands"][band]["closure"]
            add(f"| {d['direction']} | {band} | {_f(c['ops'])} | "
                f"{_f(c['ops_raw'])} | {_f(c['shell'])} | {_f(c['mode'])} | "
                f"{_f(c['pos'])} | {_f(c['exact'])} |")
    add("")
    add("## 5. Secondary distribution diagnostics")
    add("")
    add("### Band-mean transfer")
    add("")
    add("`T = sum_shell t` over the band, for the truth, the deterministic "
        "arm, and each reconstruction. `R_ops` is the operational model; "
        "`R_exact` is the truth by construction.")
    add("")
    add("| direction | band | truth | d | R_ops | R_shell | R_mode | R_pos | "
        "R_exact |")
    add("|---|---|---|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            t = d["bands"][band]["transfer"]
            add(f"| {d['direction']} | {band} | {_f(t['truth'])} | "
                f"{_f(t['d'])} | {_f(t['ops'])} | {_f(t['shell'])} | "
                f"{_f(t['mode'])} | {_f(t['pos'])} | {_f(t['exact'])} |")
    add("")
    add("### Transfer distribution")
    add("")
    add("Per-band statistics for the truth, deterministic arm, and true "
        "residual. `P+ = mean(max(t, 0))`; `f+ = mean(t > 0)`; `A` is the "
        "amplitude-weighted sign alignment in `[-1, 1]`. Per-shell arrays for "
        "`W1`, the budget, `T`, the percentiles, `P+`, `f+`, and `A` are in "
        "the JSON artifact.")
    add("")
    add("| direction | band | field | mean | std | P+ | p05 | p50 | p95 | f+ | A |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            b = d["bands"][band]
            for field in ("truth", "d", "r"):
                s = b["stats"][field]
                add(f"| {d['direction']} | {band} | {field} | "
                    f"{_f(s['mean'])} | {_u(s['std'])} | {_u(s['p_plus'])} | "
                    f"{_f(s['p05'])} | {_f(s['p50'])} | {_f(s['p95'])} | "
                    f"{_u(s['f_plus'])} | {_f(b['alignment'][field])} |")
    add("")
    add("Reconstruction statistics (mean over the 32 stochastic seeds):")
    add("")
    add("| direction | band | field | mean | std | P+ | f+ | A |")
    add("|---|---|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            b = d["bands"][band]
            for field in ("r", "ops", "shell", "mode"):
                s = b["stats"][field]
                add(f"| {d['direction']} | {band} | {field} | "
                    f"{_f(s['mean'])} | {_u(s['std'])} | {_u(s['p_plus'])} | "
                    f"{_u(s['f_plus'])} | {_f(b['alignment'][field])} |")
    add("")
    add("Truth bootstrap intervals (5--95, mode resampling):")
    add("")
    add("| direction | band | RMS | p05 | p50 | p95 |")
    add("|---|---|---|---|---|---|")
    for d in directions:
        for band in ("L", "H"):
            ti = d["bands"][band]["truth_interval"]
            add(f"| {d['direction']} | {band} | "
                f"[{_u(ti['rms'][0])}, {_u(ti['rms'][1])}] | "
                f"[{_f(ti['p05'][0])}, {_f(ti['p05'][1])}] | "
                f"[{_f(ti['p50'][0])}, {_f(ti['p50'][1])}] | "
                f"[{_f(ti['p95'][0])}, {_f(ti['p95'][1])}] |")
    add("")
    add("## 6. Decision and kill conditions")
    add("")
    add("The prior-art stop condition was checked before the freeze in "
        "[`docs/STOPLIST_ROLE_BUDGET.md`](docs/STOPLIST_ROLE_BUDGET.md); no "
        "located paper reports this held-out additive budget in a comparable "
        "exact-force setting.")
    add("")
    add("| condition | value |")
    add("|---|---|")
    for key, value in decision["kill_conditions"].items():
        add(f"| {key} | {value} |")
    add("")
    for band in ("L", "H"):
        add(f"- **Band {band} material rankings by direction:** "
            f"{decision['material_rankings'][band]}")
    add(f"- **Primary-direction ranking:** "
        f"L = {decision['primary_ranking']['L']}, "
        f"H = {decision['primary_ranking']['H']}")
    add(f"- **Phase-aware closure:** `{decision['phase_aware_closure']}`")
    add("")
    add("Split-instability and phase-aware labels are evaluated only in "
        "direction/band cells that meet the `W1(d) > 0.05` floor; if no cell "
        "meets it, the phase-aware label is `no_go`. The ranking table above "
        "lists all directions for transparency.")
    add("")
    add("## 7. Scope")
    add("")
    add("- Frozen-field, a-priori, distributional test. It does not integrate "
        "the model forward and is not an a posteriori LES skill result.")
    add("- 2D incompressible benchmark. The solenoidal subspace is "
        "one-dimensional, so the sign test is binary, not a continuous 3D "
        "phase-angle test.")
    add("- Not a Mori--Zwanzig memory measurement. A nonzero residual mean or "
        "`d`--`r` cross-spectrum would indicate deterministic-model "
        "misspecification, not a memory kernel.")
    add("- No new closure principle is claimed. The result is the measured "
        "partition under the frozen protocol.")
    add("")
    add("## 8. Reproducibility")
    add("")
    add("```bash")
    add("python run_role_budget.py --out-dir figures --report REPORT_ROLE_BUDGET.md")
    add("python -m pytest -q tests/test_role_budget.py")
    add("```")
    add("")
    add("The JSON contains the configuration, DNS and reconstruction seeds, git "
        "commit, UTC timestamp, per-shell arrays, band summaries, budget "
        "components, seed ensemble, and divergence audit. The report is "
        "generated from the JSON.")
    add("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="figures")
    ap.add_argument("--report", default="REPORT_ROLE_BUDGET.md")
    ap.add_argument("--n", type=int, default=N_DNS)
    ap.add_argument("--kc", type=int, default=KC)
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--dns-seeds", type=int, nargs=3, default=list(DNS_SEEDS))
    ap.add_argument("--n-seed", type=int, default=N_SEED)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--git-commit", default=None,
                    help="commit SHA to record (default: git rev-parse HEAD)")
    args = ap.parse_args()

    if len(set(args.dns_seeds)) != 3:
        ap.error("--dns-seeds must be three distinct seeds")
    if args.n_seed < 1 or args.n_boot < 1:
        ap.error("--n-seed and --n-boot must be positive")

    os.makedirs(args.out_dir, exist_ok=True)
    sp = Spectral2D(args.n)
    kc = args.kc

    print(f"Role budget: n={args.n}, kc={kc}, steps={args.steps}, "
          f"DNS seeds={args.dns_seeds}, n_seed={args.n_seed}, "
          f"n_boot={args.n_boot}")
    realizations = {}
    for seed in args.dns_seeds:
        print(f"  DNS realization seed={seed} ...")
        realizations[seed] = prepare_realization(sp, kc, seed, args.steps)
        print(f"    Z={realizations[seed].strain_z:.4e}")

    rotations = [
        (0, args.dns_seeds[0], args.dns_seeds[1], args.dns_seeds[2]),
        (1, args.dns_seeds[1], args.dns_seeds[2], args.dns_seeds[0]),
        (2, args.dns_seeds[2], args.dns_seeds[0], args.dns_seeds[1]),
    ]
    directions = []
    for direction_index, fit, cal, test in rotations:
        print(f"  direction {direction_index + 1}: fit={fit}, cal={cal}, "
              f"test={test} ...")
        result = compute_direction(
            sp, kc, realizations, fit, cal, test,
            n_seed=args.n_seed, n_boot=args.n_boot,
            direction_index=direction_index,
        )
        directions.append(result)
        for band in ("L", "H"):
            b = result["bands"][band]
            print(f"    band {band}: W1(d)={b['W1']['d']:.3f} "
                  f"E_total={b['budget']['E_total']:+.3f} "
                  f"E_cal={b['budget']['E_cal']:+.3f} "
                  f"E_amp={b['budget']['E_amp']:+.3f} "
                  f"E_sign={b['budget']['E_sign']:+.3f}")
        worst = max(result["divergence"].values())
        print(f"    max reconstruction divergence = {worst:.2e}")

    decision = summarise_decision(directions)

    data = {
        "what": ("role-budget decomposition of a deterministic subgrid "
                 "closure's residual, frozen protocol"),
        "protocol": {
            "file": "docs/PRESPEC_ROLE_BUDGET.md",
            "sha256": PROTOCOL_SHA256,
            "tag": PROTOCOL_TAG,
        },
        "config": {
            "n": args.n,
            "kc": kc,
            "steps": args.steps,
            "dns_seeds": list(args.dns_seeds),
            "n_seed": args.n_seed,
            "n_boot": args.n_boot,
            "reconstruction_seeds": list(range(args.n_seed)),
            "cs_smag": CS_SMAG,
            "clark_fixed": CLARK_FIXED,
            "bands": {"L": "1 <= k < kc/2", "H": "kc/2 <= k <= kc"},
        },
        "git_commit": args.git_commit or _git_commit(),
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "directions": directions,
        "decision": decision,
    }
    raw_data = data
    data = _json_safe(data)

    json_path = os.path.join(args.out_dir, "31_role_budget.json")
    with open(json_path, "w") as fh:
        json.dump(data, fh, indent=2, allow_nan=False)
        fh.write("\n")
    print(f"  -> {json_path}")

    png_path = os.path.join(args.out_dir, "31_role_budget.png")
    make_figure(raw_data, png_path)
    print(f"  -> {png_path}")

    with open(args.report, "w") as fh:
        fh.write(render_report(data))
    print(f"  -> {args.report}")
    print(f"  verdict: {decision['verdict']}; "
          f"phase-aware: {decision['phase_aware_closure']}")


if __name__ == "__main__":
    main()
