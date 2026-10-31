"""Unit tests for Paper 4 — non-Markovian multiscale memory
(nonmarkov_argo.py).

Validate the autocorrelation, the Chapman-Kolmogorov excess, and the single/double
exponential model selection on deterministic synthetic processes (no Argo download):
AR(1) must read as Markov (excess ~0, single-exp); a two-timescale process must read
as non-Markovian (excess>0, double-exp, separated timescales). Seeded, CPU-only.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nonmarkov_argo as M  # noqa: E402
import run_nonmarkov_argo as R  # noqa: E402


def test_excess_zero_for_geometric_acf():
    rho = 0.7
    C = rho ** np.arange(20)            # exact AR(1) autocorrelation
    assert abs(M.nonmarkov_excess(C)) < 1e-12
    assert abs(M.nonmarkov_excess_k(C, 3)) < 1e-12
    assert abs(M.nonmarkov_excess_k(C, 5)) < 1e-12


def test_acf_white_noise_is_flat():
    w = np.random.default_rng(0).standard_normal(5000)
    C = M.acf_nan(w, 20)
    assert C[0] == 1.0
    assert np.all(np.abs(C[1:]) < 0.1)


def test_acf_nan_aware():
    x = np.sin(np.arange(500) * 0.3)
    x[::7] = np.nan                      # scattered gaps
    C = M.acf_nan(x, 10)
    assert C[0] == 1.0 and np.isfinite(C[1])


def test_ar1_reads_as_markov():
    ex2 = [M.nonmarkov_excess(M.acf_nan(M.ar1(phi=0.8, seed=s), 30)) for s in range(20)]
    assert abs(np.median(ex2)) < 0.02                       # excess ~ 0
    dA = [M.fit_models(M.acf_nan(M.ar1(phi=0.8, seed=s), 30), step=1.0)["d_aic"]
          for s in range(20)]
    assert np.median(dA) < 50                               # double not preferred


def test_two_timescale_reads_as_nonmarkov():
    ex2 = [M.nonmarkov_excess(M.acf_nan(M.two_timescale(seed=s), 30)) for s in range(20)]
    assert np.median(ex2) > 0.02                            # positive CK excess
    f = M.fit_models(M.acf_nan(M.two_timescale(seed=0), 30), step=1.0)
    assert f["d_aic"] > 50 and f["sep"] > 3 and f["double_preferred"]


def test_fit_recovers_single_timescale():
    phi = 0.85
    C = M.acf_nan(M.ar1(phi=phi, seed=3), 40)
    f = M.fit_models(C, step=1.0)
    expected = -1.0 / np.log(phi)
    assert abs(f["tau_single"] - expected) / expected < 0.4


def test_float_dir_default_when_env_unset(monkeypatch):
    monkeypatch.delenv(R.FLOAT_DIR_ENV, raising=False)
    assert R.resolve_float_dir(None) == Path(R.DEFAULT_FLOAT_DIR)


def test_float_dir_reads_environment(monkeypatch, tmp_path):
    monkeypatch.setenv(R.FLOAT_DIR_ENV, str(tmp_path))
    assert R.resolve_float_dir(None) == tmp_path


def test_float_dir_cli_beats_environment(monkeypatch, tmp_path):
    env_dir = tmp_path / "env"
    cli_dir = tmp_path / "cli"
    monkeypatch.setenv(R.FLOAT_DIR_ENV, str(env_dir))
    assert R.resolve_float_dir(str(cli_dir)) == cli_dir


def test_missing_profiles_names_the_env_var(tmp_path):
    with pytest.raises(FileNotFoundError, match=R.FLOAT_DIR_ENV):
        R.find_profiles(tmp_path)


def test_find_profiles_selects_prof_netcdf(tmp_path):
    (tmp_path / "6900001_prof.nc").write_bytes(b"")
    (tmp_path / "notes.txt").write_text("not a profile")
    assert R.find_profiles(tmp_path) == [str(tmp_path / "6900001_prof.nc")]
