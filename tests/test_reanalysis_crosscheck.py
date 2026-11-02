"""Test the committed R1-vs-R2 Helmholtz ratio cross-check (P0-R7)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "figures", "27b_reanalysis_crosscheck.json")


def test_crosscheck_artifact():
    with open(ART) as fh:
        d = json.load(fh)
    assert d["minimum_at_500_in_both"] is True
    assert d["max_rel_diff"] < 0.30
    for lev, row in d["levels_hPa"].items():
        assert 0.001 < row["R1"] < 0.10
        assert 0.001 < row["R2"] < 0.10
    # ordering identical: 500 < 250 < 850 in both
    r1 = {k: v["R1"] for k, v in d["levels_hPa"].items()}
    r2 = {k: v["R2"] for k, v in d["levels_hPa"].items()}
    assert sorted(r1, key=r1.get) == sorted(r2, key=r2.get) == ["500", "250", "850"]


def test_leave_one_out_calibration():
    """A single R2/R1 offset calibrated on two levels predicts the held-out third.

    This is a held-out check on the committed cross-check artifact, not a new
    analysis: it asks whether one multiplicative assimilation offset learned
    from two pressure levels transfers to the third level within 10%.
    """
    with open(ART) as fh:
        d = json.load(fh)
    levels = ["850", "500", "250"]
    ratios = {lev: d["levels_hPa"][lev]["R2"] / d["levels_hPa"][lev]["R1"]
              for lev in levels}
    for held in levels:
        train = [ratios[lev] for lev in levels if lev != held]
        scale = sum(train) / len(train)
        predicted = scale * d["levels_hPa"][held]["R1"]
        observed = d["levels_hPa"][held]["R2"]
        rel = abs(predicted - observed) / observed
        assert rel < 0.10, f"{held} hPa held-out error {rel:.3f}"
