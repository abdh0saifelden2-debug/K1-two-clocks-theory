"""Fail CI when a checked paper number disagrees with committed artifacts."""

from __future__ import annotations

import ast
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper0_two_clocks.tex"
REPORT = ROOT / "REPORT_STABILITY.md"
STABILITY = ROOT / "neon_pt" / "stability.py"


class ClaimError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClaimError(message)


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def number(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -number(node.operand)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return number(node.operand)
    if isinstance(node, ast.Attribute) and node.attr == "inf":
        return math.inf
    if isinstance(node, ast.Name) and node.id == "inf":
        return math.inf
    raise ClaimError(f"unsupported boundary expression: {ast.dump(node)}")


def stability_bins():
    tree = ast.parse(STABILITY.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "STABILITY_BINS" not in names:
            continue
        bins = []
        for element in node.value.elts:
            require(isinstance(element, ast.Call), "STABILITY_BINS is not a call list")
            require(isinstance(element.func, ast.Name) and element.func.id == "StabilityBin",
                    "STABILITY_BINS uses an unexpected constructor")
            label = element.args[0].value
            bins.append((label, number(element.args[1]), number(element.args[2])))
        return bins
    raise ClaimError("STABILITY_BINS not found")


def paper_text() -> str:
    return PAPER.read_text(encoding="utf-8")


def table_body(text: str) -> tuple[str, list[list[str]]]:
    marker = "\\label{tab:stability}"
    start = text.index(marker)
    mid = text.index("\\midrule", start) + len("\\midrule")
    end = text.index("\\bottomrule", mid)
    body = text[mid:end]
    rows = []
    for raw in body.split("\\\\"):
        row = raw.strip()
        if not row:
            continue
        cells = [cell.strip() for cell in row.split("&")]
        require(len(cells) == 6, f"stability row does not have six cells: {row!r}")
        rows.append(cells)
    require(len(rows) == 5, f"expected five stability rows, got {len(rows)}")
    return body, rows


def range_numbers(cell: str) -> list[float]:
    return [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", cell)]


def bracketed(cell: str) -> tuple[float, float, float]:
    match = re.fullmatch(r"([0-9.]+)\s*\[([0-9.]+)--([0-9.]+)\]", cell.replace("$", "").strip())
    require(match is not None, f"cannot parse median/range cell: {cell!r}")
    return float(match.group(1)), float(match.group(2)), float(match.group(3))


def report_medians() -> dict[str, tuple[float, float]]:
    out = {}
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        label = cells[0].lower()
        if label in {"strongly unstable", "unstable", "near-neutral", "stable", "strongly stable"}:
            out[label] = (float(cells[2]), float(cells[3]))
    require(len(out) == 5, f"expected five report rows, got {len(out)}")
    return out


def check_fc15() -> None:
    text = paper_text()
    body, rows = table_body(text)
    bins = stability_bins()
    claims = load_json(ROOT / "claims" / "fc15_winter.json")
    claim_rows = {row["class"]: row for row in claims["rows"]}
    medians = report_medians()

    expected = [
        ("strongly unstable", -math.inf, -0.5),
        ("unstable", -0.5, -0.1),
        ("near-neutral", -0.1, 0.1),
        ("stable", 0.1, 0.5),
        ("strongly stable", 0.5, math.inf),
    ]
    require([(label, lo, hi) for label, lo, hi in bins] == expected,
            f"code stability bins changed: {bins!r}")
    require(claims["edges"] == [-0.5, -0.1, 0.1, 0.5],
            "claim-map bin edges are not [-0.5, -0.1, 0.1, 0.5]")

    for cells, (label, lo, hi) in zip(rows, bins):
        paper_label = label[0].upper() + label[1:]
        require(cells[0] == paper_label, f"class label changed: {cells[0]!r} != {paper_label!r}")
        expected_edges = []
        if math.isfinite(lo):
            expected_edges.append(lo)
        if math.isfinite(hi):
            expected_edges.append(hi)
        got_edges = range_numbers(cells[1])
        require(len(got_edges) == len(expected_edges) and all(close(a, b) for a, b in zip(got_edges, expected_edges)),
                f"{label}: paper range {got_edges!r} != code edges {expected_edges!r}")

        row = claim_rows[label]
        require(int(cells[2]) == row["n"], f"{label}: paper count {cells[2]} != claim {row['n']}")
        median, low, high = bracketed(cells[3])
        require(close(median, row["median_r_uw"], 5e-4),
                f"{label}: paper r_uw median {median} != claim {row['median_r_uw']}")
        require(close(low, round(row["p05_r_uw"], 2), 1e-9),
                f"{label}: paper r_uw p05 {low} != claim {round(row['p05_r_uw'], 2)}")
        require(close(high, round(row["p95_r_uw"], 2), 1e-9),
                f"{label}: paper r_uw p95 {high} != claim {round(row['p95_r_uw'], 2)}")
        require(close(median, medians[label][0], 5e-4),
                f"{label}: paper r_uw median {median} != report {medians[label][0]}")

        median, low, high = bracketed(cells[4])
        require(close(median, row["median_abs_r_wT"], 5e-4),
                f"{label}: paper |r_wT| median {median} != claim {row['median_abs_r_wT']}")
        require(close(low, round(row["p05_abs_r_wT"], 2), 1e-9),
                f"{label}: paper |r_wT| p05 {low} != claim {round(row['p05_abs_r_wT'], 2)}")
        require(close(high, round(row["p95_abs_r_wT"], 2), 1e-9),
                f"{label}: paper |r_wT| p95 {high} != claim {round(row['p95_abs_r_wT'], 2)}")
        require(close(median, medians[label][1], 5e-4),
                f"{label}: paper |r_wT| median {median} != report {medians[label][1]}")

        ratio = float(cells[5])
        require(close(ratio, round(row["transport_ratio"], 2), 1e-9),
                f"{label}: paper ratio {ratio} != claim {round(row['transport_ratio'], 2)}")

    artifact = load_json(ROOT / "figures" / "01b_neon_seasonal.json")
    winter, summer = artifact[0], artifact[1]
    for label, row in claim_rows.items():
        require(winter["class_counts"][label] == row["n"],
                f"{label}: artifact count != claim")
        require(close(winter["transport_ratio_by_class"][label], row["transport_ratio"]),
                f"{label}: artifact ratio != claim")
    require(close(winter["transport_ratio_swing"], 4.269428380033081),
            "winter artifact swing changed")
    require(f"{winter['transport_ratio_swing']:.1f}" == "4.3", "winter swing does not round to 4.3")
    ratios = list(winter["transport_ratio_by_class"].values())
    require(f"{min(ratios):.2f} to {max(ratios):.2f}" == "0.77 to 3.28",
            "winter ratio endpoints changed")
    require(f"{summer['transport_ratio_swing']:.1f}" == "5.9", "summer swing does not round to 5.9")
    summer_ratios = list(summer["transport_ratio_by_class"].values())
    require(f"{min(summer_ratios):.2f} to {max(summer_ratios):.2f}" == "0.44 to 2.60",
            "summer ratio endpoints changed")

    coarse = claims["coarse_pm10"]
    require(coarse["n"] == [51, 117, 121, 228, 85], "coarse counts changed")
    require(f"{coarse['transport_ratio_swing']:.1f}" == "5.6",
            "coarse swing does not round to 5.6")
    require("5.6$\\times$" in text, "paper lacks the 5.6x binning-robustness parenthetical")
    require("51/117/121/228/85" in text, "paper lacks the coarse bin counts")
    require("factor of 4.3" in text, "paper lacks the 4.3x winter swing")
    require("(0.77 to 3.28)" in text, "paper lacks the 0.77--3.28 winter endpoints")
    require("5.9 in summer" in text, "paper lacks the 5.9x summer swing")
    require("(0.44 to 2.60)" in text, "paper lacks the 0.44--2.60 summer endpoints")
    require("Medians with measured 5--95\\% ranges over usable periods" in text,
            "paper caption is not the measured 5--95% wording")
    require("The bin edges are $-0.5$, $-0.1$, $0.1$, and $0.5$." in text,
            "paper footnote lacks the verified bin edges")
    require("-1.0" not in body and "1.0$" not in body,
            "paper stability table still contains a +/-1.0 label")


def check_o6() -> None:
    text = paper_text()
    artifact = load_json(ROOT / "figures" / "09b_asos_ci.json")
    stations = {station["station"]: station for station in artifact["stations"]}
    s2 = [station["coh_S2"] for station in artifact["stations"]]
    require(f"{min(s2):.2f}--{max(s2):.2f}" == "0.82--0.98",
            "ASOS 12 h coherence range changed")
    require("0.82--0.98" in text, "paper lacks the 0.82--0.98 12 h range")
    for name, station in stations.items():
        require(station["coh_S2"] > station["coh_S2_surr95"],
                f"{name}: 12 h coherence is no longer above its surrogate threshold")
    listed = re.search(r"CAR, DSM, and SEA \(([^)]*)\)", text)
    require(listed is not None, "paper lacks the CAR/DSM/SEA 24 h coherence list")
    printed = [float(value) for value in re.findall(r"0\.\d+", listed.group(1))]
    require(len(printed) == 3, "paper CAR/DSM/SEA list does not have three values")
    for name, paper_value in zip(("CAR", "DSM", "SEA"), printed):
        value = stations[name]["coh_S1"]
        require(value < stations[name]["coh_S1_surr95"],
                f"{name}: 24 h coherence is no longer below its surrogate threshold")
        require(close(value, paper_value, 6e-4),
                f"{name}: paper 24 h coherence {paper_value} != artifact {value}")
    for name, station in stations.items():
        if name in {"CAR", "DSM", "SEA"}:
            continue
        require(station["coh_S1"] > station["coh_S1_surr95"],
                f"{name}: 24 h coherence is now below its surrogate threshold")

    off = [station["coh_offline"] for station in artifact["stations"]]
    off_surr = [station["coh_offline_surr95"] for station in artifact["stations"]]
    require(f"{min(off):.2f}--{max(off):.2f}" == "0.09--0.30",
            "off-line coherence range changed")
    below = sum(value <= level for value, level in zip(off, off_surr))
    require(below == 4, f"off-line coherence is at or below the surrogate level at {below}/8 stations")
    require(max(value - level for value, level in zip(off, off_surr)) <= 0.12,
            "off-line coherence exceeds the surrogate level by more than 0.12")
    require("0.09--0.30: at or below the phase-randomized-surrogate 95\\% level "
            "at four of eight stations, and within 0.12 of it at the rest." in text,
            "paper lacks the verified off-line coherence sentence")
    require("above the phase-randomized-surrogate 95\\% level at all eight stations" not in text,
            "paper still claims off-line coherence is above the surrogate level everywhere")


def check_fc2() -> None:
    text = paper_text()
    artifact = load_json(ROOT / "figures" / "24b_spde_common_phase.json")
    common = artifact["checks"]["common_phase_cross_spectrum_preserving"]
    require(artifact["n"] == 128, "F-C2 control resolution changed")
    require(f"{common['div_star_rms']:.2e}" == "2.75e-02",
            "F-C2 uncorrected divergence changed")
    require(f"{common['div_surrogate_rms']:.2e}" == "3.66e-02",
            "F-C2 common-phase divergence changed")
    require(f"{common['surrogate_div_ratio']:.2f}" == "1.33",
            "F-C2 common-phase ratio changed")
    require(f"{common['cross_spectrum_rel_err']:.0e}" == "2e-16",
            "F-C2 cross-spectrum error changed")
    require(f"{artifact['div_proj_rms']:.1e}" == "2.2e-15",
            "F-C2 projection error changed")
    for phrase in ("2.75\\times10^{-2}", "3.66\\times10^{-2}",
                   "\\sim2\\times10^{-16}", "2.2\\times10^{-15}",
                   "1.33\\times"):
        require(phrase in text, f"paper lacks the F-C2 value {phrase}")


def check_disclosures() -> None:
    text = " ".join(paper_text().split())
    require("not a clean all-level comparison" in text,
            "paper lacks the Fig. 14 same-level qualification")
    require("consistent with time-averaging acting" in text,
            "Fig. 14 caption overclaims the low-pass comparison")
    require("not a bandwidth-matched calibration" in text,
            "paper lacks the channel-filter cutoff-units disclosure")
    require("All figures and numerical results are regenerated from the analysis modules" in text,
            "paper reproducibility sentence does not identify the analysis modules")
    digest = "ef637ff5f912a5d1404f677429f9429eccc8102a8cab23cee79cf055bbf1220"
    require(f"\\texttt{{\\footnotesize SHA-256: {digest}}}" in text,
            "paper archive SHA-256 is not on the copyable single-font line")
    require(f"{digest[:8]}\\allowbreak" not in text,
            "paper archive SHA-256 is still broken with \\allowbreak")


def check_reanalysis_ratio() -> None:
    text = " ".join(paper_text().split())
    require("divergent-to-rotational kinetic-energy ratio of" in text,
            "abstract lacks the 850 hPa ratio wording")
    require("at 850~hPa" in text and "in the R2 cross-check" in text,
            "abstract lacks the 850 hPa ratio values")
    require("leq4" not in text,
            "abstract still states a share as leq4")
    require("850 hPa & 4.0" in text and "& 4.5" in text,
            "Table 5 850 hPa row changed")


def check_r3() -> None:
    text = paper_text()
    artifact = load_json(ROOT / "figures" / "27b_reanalysis_crosscheck.json")
    value = artifact["max_rel_diff"]
    require(artifact["minimum_at_500_in_both"] is True, "R1/R2 500 hPa minimum changed")
    require(f"{value * 100:.1f}%" == "15.5%", "R3 maximum changed")
    require("approximately 15\\% (maximum 15.5\\%)" in text,
            "paper lacks the corrected R3 wording")
    require("15\\% or less" not in text, "paper still contains the old R3 bound")


def main() -> int:
    checks = [
        ("F-C15 stability table", check_fc15),
        ("O6 coherence", check_o6),
        ("F-C2 common-phase control", check_fc2),
        ("manuscript disclosures", check_disclosures),
        ("R3 abstract ratio", check_reanalysis_ratio),
        ("R3 cross-check", check_r3),
    ]
    failures = 0
    for name, check in checks:
        try:
            check()
        except ClaimError as error:
            failures += 1
            print(f"FAIL {name}: {error}", file=sys.stderr)
        else:
            print(f"ok   {name}")
    if failures:
        print(f"claim-map lint: {failures} failure(s)", file=sys.stderr)
        return 1
    print(f"claim-map lint: {len(checks)} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
