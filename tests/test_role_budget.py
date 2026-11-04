"""Tests for the frozen role-budget protocol.

The structural tests run on a small DNS grid.  The artifact test activates once
``figures/31_role_budget.json`` and ``REPORT_ROLE_BUDGET.md`` are committed; it
checks the frozen protocol hash, the additive identity, and byte-for-byte
agreement between the committed report and the report rendered from the JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from compressible.ns import Spectral2D
from closure.role_budget import (
    BUDGET_KEYS,
    band_masks,
    compute_direction,
    force_from_streamfunction,
    positive_sign_reconstruction,
    prepare_realization,
    random_mode_reconstruction,
    random_shell_reconstruction,
    streamfunction_from_force,
    summarise_decision,
    wasserstein1,
)
from closure.sgs import divergence_rms, exact_sgs_force, force_spectrum, shell_index

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "figures" / "31_role_budget.json"
REPORT = ROOT / "REPORT_ROLE_BUDGET.md"
PROTOCOL_SHA256 = "c02735bb034ea704ec686aa419dbb14e0154252f9aa7c70007a6517acc4d4322"


@pytest.fixture(scope="module")
def small_realizations():
    sp = Spectral2D(64)
    kc = 8
    real = {seed: prepare_realization(sp, kc, seed, steps=250, k_f=12.0)
            for seed in (42, 43, 44)}
    return sp, kc, real


def test_streamfunction_roundtrip(small_realizations):
    sp, kc, real = small_realizations
    dns = real[42]
    sp_ref = sp
    _, _, mx, my = exact_sgs_force(sp_ref, dns.u, dns.v, kc)
    psi = streamfunction_from_force(sp_ref, mx, my)
    rx, ry = force_from_streamfunction(sp_ref, psi)
    scale = np.sqrt(np.mean(mx ** 2 + my ** 2)) + 1e-30
    err = np.sqrt(np.mean((rx - mx) ** 2 + (ry - my) ** 2)) / scale
    assert err < 1e-10, f"streamfunction round-trip error {err}"


def test_reconstructions_are_solenoidal(small_realizations):
    sp, kc, real = small_realizations
    test = real[44]
    _, e_test = force_spectrum(sp, test.mx, test.my, kc)
    ops = random_shell_reconstruction(sp, e_test, np.random.default_rng(1), kc)
    shell = random_shell_reconstruction(sp, e_test, np.random.default_rng(2), kc)
    mode = random_mode_reconstruction(sp, test.mx, test.my,
                                      np.random.default_rng(3), kc)
    pos = positive_sign_reconstruction(sp, test.mx, test.my,
                                       test.ub, test.vb, kc)
    for name, (fx, fy) in (("ops", ops), ("shell", shell),
                           ("mode", mode), ("pos", pos)):
        div = divergence_rms(sp, fx, fy)
        assert div < 1e-12, f"{name} divergence {div}"


def test_wasserstein1_is_nonnegative():
    rng = np.random.default_rng(0)
    idx = np.array([0, 1, 1, 1, 2, 2])
    t_true = rng.standard_normal(idx.size)
    t_model = rng.standard_normal(idx.size)
    for k in (1, 2):
        w = wasserstein1(t_true, t_model, idx == k)
        assert np.isfinite(w) and w >= 0.0


def test_budget_identity_and_bounds(small_realizations):
    sp, kc, real = small_realizations
    result = compute_direction(sp, kc, real, 42, 43, 44,
                               n_seed=3, n_boot=8, direction_index=0)
    for band in ("L", "H"):
        b = result["bands"][band]
        total = sum(b["budget"][key] for key in ("E_cal", "E_amp", "E_sign"))
        assert abs(total - b["budget"]["E_total"]) < 1e-12
        for key in ("d", "ops", "ops_raw", "shell", "mode", "pos", "exact"):
            assert not np.isfinite(b["W1"][key]) or b["W1"][key] >= 0.0
        for key in ("ops", "ops_raw", "shell", "mode", "pos", "exact"):
            assert not np.isfinite(b["closure"][key]) or b["closure"][key] <= 1.0 + 1e-12

    per = result["per_shell"]
    for i, _k in enumerate(per["k"]):
        vals = [per["budget"][key][i] for key in ("E_cal", "E_amp", "E_sign")]
        if all(v is not None for v in vals + [per["budget"]["E_total"][i]]):
            assert abs(sum(vals) - per["budget"]["E_total"][i]) < 1e-12


def test_decision_block_is_mechanical(small_realizations):
    sp, kc, real = small_realizations
    result = compute_direction(sp, kc, real, 42, 43, 44,
                               n_seed=3, n_boot=8, direction_index=0)
    decision = summarise_decision([result, result, result])
    assert set(decision) == {
        "kill_conditions", "material_rankings", "primary_ranking",
        "phase_aware_closure", "verdict",
    }
    assert decision["phase_aware_closure"] in {"go", "no_go", "unresolved"}
    assert decision["verdict"] in {
        "continue", "stop_no_residual", "stop_no_sign_role",
        "report_directions_separately", "unresolved_noise",
    }


@pytest.mark.skipif(not ARTIFACT.exists() or not REPORT.exists(),
                    reason="artifact not generated yet")
def test_artifact_and_report_are_consistent():
    from run_role_budget import render_report

    data = json.loads(ARTIFACT.read_text())
    assert data["protocol"]["sha256"] == PROTOCOL_SHA256
    assert data["config"]["n_seed"] >= 1
    assert len(data["directions"]) == 3

    for d in data["directions"]:
        for band in ("L", "H"):
            b = d["bands"][band]
            total = sum(b["budget"][key] for key in ("E_cal", "E_amp", "E_sign"))
            assert abs(total - b["budget"]["E_total"]) < 1e-12
            for key in BUDGET_KEYS:
                lo, hi = b["interval"][key]
                if lo is not None and hi is not None:
                    assert lo <= hi
            for key in ("d", "ops", "shell", "mode", "pos", "exact"):
                if b["W1"][key] is not None:
                    assert b["W1"][key] >= 0.0

    assert REPORT.read_text() == render_report(data)
