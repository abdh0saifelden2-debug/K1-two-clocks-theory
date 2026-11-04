"""Role-budget decomposition of a deterministic subgrid closure's residual.

This module implements the protocol frozen in ``docs/PRESPEC_ROLE_BUDGET.md``
(tag ``paper0-roles-prespec-v1``).  It is a frozen-field, a-priori benchmark:
the exact subgrid force is known, the deterministic arm is calibrated on a
separate realization, the operational residual spectrum is measured on a second
realization, and everything is scored on a third.

Nothing in this module chooses a protocol.  The split, the arms, the
reconstruction hierarchy, the Wasserstein metric, and the additive budget are
all fixed by the pre-specification.  The implementation only fills in details
the protocol leaves open (FFT layout, resampling order, report formatting).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from closure.sgs import (
    divergence_rms,
    exact_sgs_force,
    force_spectrum,
    project_vec,
    sharp_filter,
    shell_index,
    smagorinsky_force,
)

CS_SMAG = 0.17
CLARK_FIXED = 1.0 / 12.0
BUDGET_KEYS = ("E_total", "E_cal", "E_amp", "E_sign")
MODEL_KEYS = ("d", "ops", "ops_raw", "shell", "mode", "pos", "exact")


# ---------------------------------------------------------------------------
# basic operators
# ---------------------------------------------------------------------------

def clark_gradient_force(sp, ub: np.ndarray, vb: np.ndarray, kc: float,
                         coefficient: float = 1.0):
    """Clark/gradient model ``tau_ij = C Delta^2 (d_k u_i)(d_k u_j)``.

    The returned force is ``P div tau``, sharp-filtered and Leray-projected.
    With ``coefficient=1`` the caller can calibrate ``C`` by linear least
    squares and then rescale.
    """
    delta = np.pi / kc
    c = coefficient * delta ** 2
    ux, uy = sp.ddx(ub), sp.ddy(ub)
    vx, vy = sp.ddx(vb), sp.ddy(vb)
    txx = c * (ux * ux + uy * uy)
    tyy = c * (vx * vx + vy * vy)
    txy = c * (ux * vx + uy * vy)
    mx = sp.ddx(txx) + sp.ddy(txy)
    my = sp.ddx(txy) + sp.ddy(tyy)
    mx = sharp_filter(sp, mx, kc)
    my = sharp_filter(sp, my, kc)
    mx, my = project_vec(sp, mx, my)
    return mx, my


def spectral_eddy_viscosity(sp, ub: np.ndarray, vb: np.ndarray,
                            mx: np.ndarray, my: np.ndarray, kc: int) -> np.ndarray:
    """Shell-wise ``nu_t(k) = -T_true(k) / sum_shell k^2 |uhat|^2``.

    The sign is not constrained: a negative value is backscatter.
    """
    idx = shell_index(sp)
    uh, vh = sp.fft(ub), sp.fft(vb)
    mhx, mhy = sp.fft(mx), sp.fft(my)
    t = np.real(np.conj(uh) * mhx + np.conj(vh) * mhy)
    denom = sp.k2 * (np.abs(uh) ** 2 + np.abs(vh) ** 2)
    nu = np.zeros(kc + 1)
    for k in range(kc + 1):
        m = idx == k
        d = float(denom[m].sum())
        if d > 1e-30:
            nu[k] = -float(t[m].sum()) / d
    return nu


def spectral_ev_force(sp, ub: np.ndarray, vb: np.ndarray, kc: int,
                      nu_shell: np.ndarray):
    """``m_par = -nu_t(k) k^2 uhat``; solenoidal because it is parallel to uhat."""
    idx = shell_index(sp)
    uh, vh = sp.fft(ub), sp.fft(vb)
    mxh = np.zeros_like(uh)
    myh = np.zeros_like(vh)
    for k in range(kc + 1):
        m = idx == k
        mxh[m] = -nu_shell[k] * sp.k2[m] * uh[m]
        myh[m] = -nu_shell[k] * sp.k2[m] * vh[m]
    return sp.ifft(mxh), sp.ifft(myh)


def strain_norm_sq(sp, ub: np.ndarray, vb: np.ndarray) -> float:
    """``Z = mean(|Sbar|^2)`` with the same norm used by Smagorinsky."""
    ux, uy = sp.ddx(ub), sp.ddy(ub)
    vx, vy = sp.ddx(vb), sp.ddy(vb)
    s11, s22, s12 = ux, vy, 0.5 * (uy + vx)
    return float(np.mean(2.0 * (s11 ** 2 + s22 ** 2 + 2.0 * s12 ** 2)))


def streamfunction_from_force(sp, mx: np.ndarray, my: np.ndarray) -> np.ndarray:
    """Inverse of ``r = grad_perp psi`` in Fourier space.

    ``rhat_x = i ky psihat`` and ``rhat_y = -i kx psihat``, hence
    ``psihat = (i kx rhat_y - i ky rhat_x) / k^2``.
    """
    mhx, mhy = sp.fft(mx), sp.fft(my)
    psi = np.zeros_like(mhx)
    mask = sp.k2 > 0
    psi[mask] = ((1j * sp.kx[mask] * mhy[mask]
                  - 1j * sp.ky[mask] * mhx[mask]) / sp.k2[mask])
    psi[0, 0] = 0.0
    return psi


def force_from_streamfunction(sp, psi: np.ndarray):
    """``r = (d_y psi, -d_x psi)``; divergence-free by construction."""
    return sp.ifft(1j * sp.ky * psi), sp.ifft(-1j * sp.kx * psi)


def local_transfer(sp, ub: np.ndarray, vb: np.ndarray,
                   mx: np.ndarray, my: np.ndarray) -> np.ndarray:
    """Mode-wise ``t = Re(uhat* . mhat)``."""
    uh, vh = sp.fft(ub), sp.fft(vb)
    mhx, mhy = sp.fft(mx), sp.fft(my)
    return np.real(np.conj(uh) * mhx + np.conj(vh) * mhy)


def mode_magnitude(sp, mx: np.ndarray, my: np.ndarray) -> np.ndarray:
    """``|mhat|`` per mode."""
    mhx, mhy = sp.fft(mx), sp.fft(my)
    return np.sqrt(np.abs(mhx) ** 2 + np.abs(mhy) ** 2)


def velocity_magnitude(sp, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    uh, vh = sp.fft(u), sp.fft(v)
    return np.sqrt(np.abs(uh) ** 2 + np.abs(vh) ** 2)


# ---------------------------------------------------------------------------
# stochastic reconstructions
# ---------------------------------------------------------------------------

def random_shell_reconstruction(sp, target_energy: np.ndarray, rng, kc: int):
    """Solenoidal field whose shell energy is ``target_energy[k]``.

    A real Gaussian streamfunction supplies Hermitian-symmetric random phases;
    each shell is then rescaled so that ``sum_shell |rhat|^2`` matches.
    """
    n = sp.n
    gh = sp.fft(rng.standard_normal((n, n)))
    gh[0, 0] = 0.0
    idx = shell_index(sp)
    psi = np.zeros_like(gh)
    for k in range(1, kc + 1):
        m = idx == k
        cur = float((sp.k2[m] * np.abs(gh[m]) ** 2).sum())
        target = float(target_energy[k])
        if cur <= 0.0 or target <= 0.0:
            continue
        psi[m] = gh[m] * np.sqrt(target / cur)
    return force_from_streamfunction(sp, psi)


def random_mode_reconstruction(sp, mx_true: np.ndarray, my_true: np.ndarray,
                               rng, kc: int):
    """Per-mode amplitudes of the truth, random streamfunction phases."""
    n = sp.n
    gh = sp.fft(rng.standard_normal((n, n)))
    gh[0, 0] = 0.0
    rxh, ryh = sp.fft(mx_true), sp.fft(my_true)
    amp = np.sqrt(np.abs(rxh) ** 2 + np.abs(ryh) ** 2)
    kr = np.sqrt(sp.k2)
    idx = shell_index(sp)
    fill = (idx >= 1) & (idx <= kc)
    phase = np.zeros_like(gh)
    nz = np.abs(gh) > 0.0
    phase[nz] = gh[nz] / np.abs(gh[nz])
    psi = np.zeros_like(gh)
    psi[fill] = phase[fill] * amp[fill] / kr[fill]
    return force_from_streamfunction(sp, psi)


def positive_sign_reconstruction(sp, mx_true: np.ndarray, my_true: np.ndarray,
                                 ub: np.ndarray, vb: np.ndarray, kc: int):
    """Per-mode amplitudes of the truth, every sign aligned with ``uhat``.

    In 2D the solenoidal subspace is one-dimensional, so this sets
    ``rhat = |rhat| uhat/|uhat|`` and makes every local transfer non-negative.
    """
    uh, vh = sp.fft(ub), sp.fft(vb)
    rxh, ryh = sp.fft(mx_true), sp.fft(my_true)
    amp = np.sqrt(np.abs(rxh) ** 2 + np.abs(ryh) ** 2)
    uamp = np.sqrt(np.abs(uh) ** 2 + np.abs(vh) ** 2)
    idx = shell_index(sp)
    fill = (idx >= 1) & (idx <= kc) & (uamp > 0.0)
    rx = np.zeros_like(uh)
    ry = np.zeros_like(vh)
    rx[fill] = amp[fill] * uh[fill] / uamp[fill]
    ry[fill] = amp[fill] * vh[fill] / uamp[fill]
    return sp.ifft(rx), sp.ifft(ry)


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

def wasserstein1(t_true: np.ndarray, t_model: np.ndarray,
                 mask: np.ndarray) -> float:
    """Normalized mode-wise Wasserstein-1 distance on one shell."""
    a = np.sort(t_true[mask])
    b = np.sort(t_model[mask])
    rms = float(np.sqrt(np.mean(t_true[mask] ** 2)))
    if rms <= 0.0 or a.size == 0:
        return float("nan")
    return float(np.mean(np.abs(a - b)) / rms)


def _stats(t: np.ndarray, mask: np.ndarray) -> dict:
    x = t[mask]
    if x.size == 0:
        return {key: float("nan") for key in
                ("mean", "std", "p05", "p50", "p95", "p_plus", "f_plus")}
    return {
        "mean": float(x.mean()),
        "std": float(x.std(ddof=0)),
        "p05": float(np.percentile(x, 5)),
        "p50": float(np.percentile(x, 50)),
        "p95": float(np.percentile(x, 95)),
        "p_plus": float(np.maximum(x, 0.0).mean()),
        "f_plus": float(np.mean(x > 0.0)),
    }


def _mean_stats(t_values, mask):
    rows = [_stats(t, mask) for t in t_values]
    keys = rows[0].keys()
    return {key: float(np.mean([row[key] for row in rows])) for key in keys}


def _alignment(t: np.ndarray, uamp: np.ndarray, mamp: np.ndarray,
               mask: np.ndarray) -> float:
    denom = float((uamp[mask] * mamp[mask]).sum())
    if denom <= 0.0:
        return 0.0
    return float(t[mask].sum() / denom)


def band_masks(sp, kc: int) -> dict:
    idx = shell_index(sp)
    return {
        "L": (idx >= 1) & (idx < kc / 2),
        "H": (idx >= kc / 2) & (idx <= kc),
    }


def _weighted(values: np.ndarray, ks, weights: np.ndarray) -> float:
    num = 0.0
    den = 0.0
    for k in ks:
        if np.isfinite(values[k]):
            num += weights[k] * values[k]
            den += weights[k]
    return float(num / den) if den > 0 else float("nan")


def _label(point: float, p05: float, p95: float, e_total: float) -> str:
    """Material / negligible / unresolved / adverse label from the protocol."""
    if not np.isfinite(point):
        return "unresolved"
    if e_total <= 0.0:
        return "not_labelled"
    if point < 0.0:
        return "adverse"
    if point < 0.05 * e_total:
        return "negligible"
    if point >= 0.10 * e_total and p05 > 0.05 * e_total:
        return "material"
    return "unresolved"


def _bootstrap_band(shells: dict, ks, weights: np.ndarray, n_boot: int,
                    rng, n_seed: int) -> dict:
    """Joint mode-bootstrap + seed-draw distribution of the band budget."""
    draws = {key: [] for key in BUDGET_KEYS}
    for _ in range(n_boot):
        seed_index = int(rng.integers(0, n_seed))
        num = {key: 0.0 for key in BUDGET_KEYS}
        den = 0.0
        for k in ks:
            d = shells[k]
            n = d["n"]
            ii = rng.integers(0, n, n)
            tt = d["t_true"][ii]
            rms = float(np.sqrt(np.mean(tt ** 2)))
            if rms <= 0.0:
                continue
            wd = float(np.mean(np.abs(np.sort(tt) - np.sort(d["t_d"][ii]))) / rms)
            if wd <= 0.0:
                continue
            wops = float(np.mean(np.abs(np.sort(tt) - np.sort(d["t_ops"][seed_index][ii]))) / rms)
            wshell = float(np.mean(np.abs(np.sort(tt) - np.sort(d["t_shell"][seed_index][ii]))) / rms)
            wmode = float(np.mean(np.abs(np.sort(tt) - np.sort(d["t_mode"][seed_index][ii]))) / rms)
            num["E_total"] += weights[k] * (wops / wd)
            num["E_cal"] += weights[k] * ((wops - wshell) / wd)
            num["E_amp"] += weights[k] * ((wshell - wmode) / wd)
            num["E_sign"] += weights[k] * (wmode / wd)
            den += weights[k]
        if den > 0.0:
            for key in BUDGET_KEYS:
                draws[key].append(num[key] / den)
    return {key: ([float(np.percentile(draws[key], 5)),
                   float(np.percentile(draws[key], 95))]
                  if draws[key] else [float("nan"), float("nan")])
            for key in BUDGET_KEYS}


# ---------------------------------------------------------------------------
# one held-out direction
# ---------------------------------------------------------------------------

@dataclass
class Realization:
    seed: int
    u: np.ndarray
    v: np.ndarray
    ub: np.ndarray
    vb: np.ndarray
    mx: np.ndarray
    my: np.ndarray
    strain_z: float


def prepare_realization(sp, kc: int, seed: int, steps: int,
                        k_f: float = 24.0) -> Realization:
    """Spin up one DNS realization and freeze the exact-force snapshot."""
    from closure.dns2d import Vorticity2D

    dns = Vorticity2D(n=sp.n, seed=seed, k_f=k_f)
    u, v = dns.field(steps=steps)
    ub, vb, mx, my = exact_sgs_force(sp, u, v, kc)
    return Realization(seed=seed, u=u, v=v, ub=ub, vb=vb, mx=mx, my=my,
                       strain_z=strain_norm_sq(sp, ub, vb))


def compute_direction(sp, kc: int, realizations: dict,
                      fit_seed: int, cal_seed: int, test_seed: int,
                      n_seed: int = 32, n_boot: int = 200,
                      direction_index: int = 0, rng=None) -> dict:
    """Run the frozen decomposition for one cyclic rotation."""
    if rng is None:
        rng = np.random.default_rng(20261104 + direction_index)

    fit = realizations[fit_seed]
    cal = realizations[cal_seed]
    test = realizations[test_seed]
    idx = shell_index(sp)
    kmax = int(kc)

    # --- deterministic arms: fit on the fit realization -------------------
    mgx, mgy = clark_gradient_force(sp, fit.ub, fit.vb, kc, coefficient=1.0)
    numerator = float((fit.mx * mgx + fit.my * mgy).sum())
    denominator = float((mgx * mgx + mgy * mgy).sum())
    clark_c = numerator / denominator if denominator > 0.0 else 0.0

    nu_shell = spectral_eddy_viscosity(sp, fit.ub, fit.vb, fit.mx, fit.my, kc)

    # --- apply to the test realization ------------------------------------
    zero = np.zeros_like(test.ub)
    d1x, d1y = smagorinsky_force(sp, test.ub, test.vb, kc, cs=CS_SMAG)
    gx, gy = clark_gradient_force(sp, test.ub, test.vb, kc, coefficient=1.0)
    d2x, d2y = clark_c * gx, clark_c * gy
    d3x, d3y = spectral_ev_force(sp, test.ub, test.vb, kc, nu_shell)

    # --- residuals ---------------------------------------------------------
    rx_test = test.mx - d2x
    ry_test = test.my - d2y
    cal_gx, cal_gy = clark_gradient_force(sp, cal.ub, cal.vb, kc, coefficient=1.0)
    rx_cal = cal.mx - clark_c * cal_gx
    ry_cal = cal.my - clark_c * cal_gy

    _, e_cal = force_spectrum(sp, rx_cal, ry_cal, kc)
    _, e_test = force_spectrum(sp, rx_test, ry_test, kc)
    z_ratio = test.strain_z / cal.strain_z if cal.strain_z > 0.0 else 1.0
    e_ops = e_cal * z_ratio

    # --- reconstructions ---------------------------------------------------
    ops, ops_raw, shell, mode = [], [], [], []
    for s in range(n_seed):
        rng_ops = np.random.default_rng(100000 * (direction_index + 1) + 10 * s + 1)
        rng_raw = np.random.default_rng(100000 * (direction_index + 1) + 10 * s + 2)
        rng_shell = np.random.default_rng(100000 * (direction_index + 1) + 10 * s + 3)
        rng_mode = np.random.default_rng(100000 * (direction_index + 1) + 10 * s + 4)
        ops.append(random_shell_reconstruction(sp, e_ops, rng_ops, kc))
        ops_raw.append(random_shell_reconstruction(sp, e_cal, rng_raw, kc))
        shell.append(random_shell_reconstruction(sp, e_test, rng_shell, kc))
        mode.append(random_mode_reconstruction(sp, rx_test, ry_test, rng_mode, kc))
    pos = positive_sign_reconstruction(sp, rx_test, ry_test, test.ub, test.vb, kc)

    # --- local transfer ----------------------------------------------------
    t_true = local_transfer(sp, test.ub, test.vb, test.mx, test.my)
    t_d = local_transfer(sp, test.ub, test.vb, d2x, d2y)
    t_r_true = t_true - t_d

    def _t(pair):
        return t_d + local_transfer(sp, test.ub, test.vb, pair[0], pair[1])

    t_ops = [_t(p) for p in ops]
    t_ops_raw = [_t(p) for p in ops_raw]
    t_shell = [_t(p) for p in shell]
    t_mode = [_t(p) for p in mode]
    t_pos = _t(pos)
    t_exact = t_true

    # --- magnitudes for the sign-alignment diagnostic ----------------------
    uamp = velocity_magnitude(sp, test.ub, test.vb)
    mamp_true = mode_magnitude(sp, test.mx, test.my)
    mamp_d = mode_magnitude(sp, d2x, d2y)
    mamp_r = mode_magnitude(sp, rx_test, ry_test)
    mamp_ops = [mode_magnitude(sp, d2x + p[0], d2y + p[1]) for p in ops]
    mamp_shell = [mode_magnitude(sp, d2x + p[0], d2y + p[1]) for p in shell]
    mamp_mode = [mode_magnitude(sp, d2x + p[0], d2y + p[1]) for p in mode]

    # --- per-shell W1 ------------------------------------------------------
    per_shell = {"k": list(range(1, kmax + 1)), "n_modes": []}
    w1 = {key: np.full(kmax + 1, np.nan) for key in MODEL_KEYS}
    budget_shell = {key: np.full(kmax + 1, np.nan) for key in BUDGET_KEYS}

    for k in range(1, kmax + 1):
        m = idx == k
        n_k = int(m.sum())
        per_shell["n_modes"].append(n_k)
        w1["d"][k] = wasserstein1(t_true, t_d, m)
        w1["ops"][k] = float(np.nanmean([wasserstein1(t_true, t, m) for t in t_ops]))
        w1["ops_raw"][k] = float(np.nanmean([wasserstein1(t_true, t, m) for t in t_ops_raw]))
        w1["shell"][k] = float(np.nanmean([wasserstein1(t_true, t, m) for t in t_shell]))
        w1["mode"][k] = float(np.nanmean([wasserstein1(t_true, t, m) for t in t_mode]))
        w1["pos"][k] = wasserstein1(t_true, t_pos, m)
        w1["exact"][k] = 0.0

        wd = w1["d"][k]
        if np.isfinite(wd) and wd > 0.0:
            budget_shell["E_total"][k] = w1["ops"][k] / wd
            budget_shell["E_cal"][k] = (w1["ops"][k] - w1["shell"][k]) / wd
            budget_shell["E_amp"][k] = (w1["shell"][k] - w1["mode"][k]) / wd
            budget_shell["E_sign"][k] = w1["mode"][k] / wd

    # --- band summaries ----------------------------------------------------
    bands = band_masks(sp, kc)
    weights = np.array([int((idx == k).sum()) for k in range(kmax + 1)],
                       dtype=float)
    band_out = {}
    for band, mask in bands.items():
        ks = [k for k in range(1, kmax + 1) if weights[k] > 0 and
              bool(np.any(mask & (idx == k)))]
        w1_band = {key: _weighted(w1[key], ks, weights) for key in MODEL_KEYS}
        budget = {key: _weighted(budget_shell[key], ks, weights) for key in BUDGET_KEYS}
        interval = _bootstrap_band(
            {k: {"n": int((idx == k).sum()),
                 "t_true": t_true[idx == k],
                 "t_d": t_d[idx == k],
                 "t_ops": [t[idx == k] for t in t_ops],
                 "t_shell": [t[idx == k] for t in t_shell],
                 "t_mode": [t[idx == k] for t in t_mode]}
             for k in ks},
            ks, weights, n_boot, rng, n_seed)

        labels = {}
        for key in BUDGET_KEYS:
            labels[key] = _label(budget[key], interval[key][0], interval[key][1],
                                 budget["E_total"])

        stats = {
            "truth": _stats(t_true, mask),
            "d": _stats(t_d, mask),
            "r": _stats(t_r_true, mask),
            "ops": _mean_stats(t_ops, mask),
            "ops_raw": _mean_stats(t_ops_raw, mask),
            "shell": _mean_stats(t_shell, mask),
            "mode": _mean_stats(t_mode, mask),
            "pos": _stats(t_pos, mask),
            "exact": _stats(t_exact, mask),
        }
        alignment = {
            "truth": _alignment(t_true, uamp, mamp_true, mask),
            "d": _alignment(t_d, uamp, mamp_d, mask),
            "r": _alignment(t_r_true, uamp, mamp_r, mask),
            "ops": float(np.mean([_alignment(t, uamp, mm, mask)
                                  for t, mm in zip(t_ops, mamp_ops)])),
            "shell": float(np.mean([_alignment(t, uamp, mm, mask)
                                    for t, mm in zip(t_shell, mamp_shell)])),
            "mode": float(np.mean([_alignment(t, uamp, mm, mask)
                                   for t, mm in zip(t_mode, mamp_mode)])),
        }
        closure = {key: (1.0 - w1_band[key] / w1_band["d"]
                         if np.isfinite(w1_band["d"]) and w1_band["d"] > 0.0
                         else float("nan"))
                   for key in ("ops", "ops_raw", "shell", "mode", "pos", "exact")}

        # mean-transfer error of the three deterministic arms (H1)
        t_arms = {
            "D1": local_transfer(sp, test.ub, test.vb, d1x, d1y),
            "D2": t_d,
            "D3": local_transfer(sp, test.ub, test.vb, d3x, d3y),
        }
        transfer_error = {}
        for name, t in t_arms.items():
            num = abs(float(t[mask].sum() - t_true[mask].sum()))
            den = abs(float(t_true[mask].sum())) + 1e-30
            transfer_error[name] = num / den

        band_out[band] = {
            "k_min": min(ks), "k_max": max(ks),
            "W1": w1_band,
            "budget": budget,
            "interval": interval,
            "labels": labels,
            "stats": stats,
            "alignment": alignment,
            "closure": closure,
            "transfer": {
                "truth": float(t_true[mask].sum()),
                "d": float(t_d[mask].sum()),
                "ops": float(np.mean([t[mask].sum() for t in t_ops])),
                "shell": float(np.mean([t[mask].sum() for t in t_shell])),
                "mode": float(np.mean([t[mask].sum() for t in t_mode])),
                "pos": float(t_pos[mask].sum()),
                "exact": float(t_exact[mask].sum()),
            },
            "mean_transfer_error": transfer_error,
        }

    # --- seed ensemble, for the artifact ----------------------------------
    seed_ensemble = {}
    for band, mask in bands.items():
        ks = [k for k in range(1, kmax + 1) if weights[k] > 0 and
              bool(np.any(mask & (idx == k)))]
        for name, series in (("ops", t_ops), ("shell", t_shell), ("mode", t_mode)):
            vals = []
            for t in series:
                vals.append(_weighted(
                    np.array([np.nan] + [wasserstein1(t_true, t, idx == k)
                                         for k in range(1, kmax + 1)]),
                    ks, weights))
            seed_ensemble[f"{name}_{band}"] = [float(v) for v in vals]
        seed_ensemble[f"ops_raw_{band}"] = [float(_weighted(
            np.array([np.nan] + [wasserstein1(t_true, t, idx == k)
                                 for k in range(1, kmax + 1)]), ks, weights))]
        seed_ensemble[f"pos_{band}"] = [float(_weighted(
            np.array([np.nan] + [wasserstein1(t_true, t_pos, idx == k)
                                 for k in range(1, kmax + 1)]), ks, weights))]

    # --- divergence audit --------------------------------------------------
    div = {
        "ops": float(np.max([divergence_rms(sp, p[0], p[1]) for p in ops])),
        "ops_raw": float(np.max([divergence_rms(sp, p[0], p[1]) for p in ops_raw])),
        "shell": float(np.max([divergence_rms(sp, p[0], p[1]) for p in shell])),
        "mode": float(np.max([divergence_rms(sp, p[0], p[1]) for p in mode])),
        "pos": divergence_rms(sp, pos[0], pos[1]),
        "exact": divergence_rms(sp, rx_test, ry_test),
    }

    # --- arm scorecard -----------------------------------------------------
    fixed_x, fixed_y = clark_gradient_force(sp, test.ub, test.vb, kc,
                                            coefficient=CLARK_FIXED)
    arm_w1 = {}
    for name, pair in (("D0", (zero, zero)), ("D1", (d1x, d1y)),
                       ("D2", (d2x, d2y)), ("D2_fixed", (fixed_x, fixed_y)),
                       ("D3", (d3x, d3y))):
        t = local_transfer(sp, test.ub, test.vb, pair[0], pair[1])
        arm_w1[name] = {}
        for band, mask in bands.items():
            m = np.array([np.nan] + [wasserstein1(t_true, t, idx == k)
                                     for k in range(1, kmax + 1)])
            ks = [k for k in range(1, kmax + 1) if np.any(mask & (idx == k))]
            arm_w1[name][band] = _weighted(m, ks, weights)

    return {
        "direction": direction_index + 1,
        "fit": int(fit_seed),
        "cal": int(cal_seed),
        "test": int(test_seed),
        "clark_C": float(clark_c),
        "clark_fixed_sensitivity": float(CLARK_FIXED),
        "nu_t": [float(v) for v in nu_shell],
        "Z_cal": float(cal.strain_z),
        "Z_test": float(test.strain_z),
        "Z_ratio": float(z_ratio),
        "bands": band_out,
        "per_shell": {
            "k": per_shell["k"],
            "n_modes": per_shell["n_modes"],
            "W1": {key: [float(v) for v in w1[key][1:]] for key in MODEL_KEYS},
            "budget": {key: [float(v) for v in budget_shell[key][1:]]
                       for key in BUDGET_KEYS},
        },
        "seed_ensemble": seed_ensemble,
        "divergence": div,
        "arm_w1": arm_w1,
    }


# ---------------------------------------------------------------------------
# cross-direction decision rules
# ---------------------------------------------------------------------------

def _material_ranking(labels: dict, budget: dict) -> list:
    return sorted([key for key in ("E_cal", "E_amp", "E_sign")
                   if labels.get(key) == "material"],
                  key=lambda key: budget[key], reverse=True)


def summarise_decision(directions: list) -> dict:
    """Apply the pre-specified labels and kill conditions to all directions."""
    bands = ("L", "H")
    no_residual = True
    no_sign = True
    split_instability = {band: False for band in bands}
    rankings = {band: [] for band in bands}

    for band in bands:
        rankings[band] = [_material_ranking(d["bands"][band]["labels"],
                                            d["bands"][band]["budget"])
                          for d in directions]
        first = rankings[band][0]
        split_instability[band] = any(r != first for r in rankings[band][1:])
        for d in directions:
            b = d["bands"][band]
            if b["W1"]["d"] <= 0.05:
                continue
            no_residual = False
            if b["labels"]["E_sign"] != "negligible":
                no_sign = False

    primary = directions[0]
    unresolved_primary = False
    for band in bands:
        b = primary["bands"][band]
        for key in ("E_cal", "E_amp", "E_sign"):
            p05, p95 = b["interval"][key]
            point = b["budget"][key]
            if not np.isfinite(point) or point == 0.0:
                continue
            if (p95 - p05) > 0.5 * abs(point):
                unresolved_primary = True

    sign_labels = [d["bands"][band]["labels"]["E_sign"]
                   for d in directions for band in bands]
    if all(label == "negligible" for label in sign_labels):
        phase = "no_go"
    elif all(label == "material" for label in sign_labels) and not split_instability["L"] and not split_instability["H"]:
        phase = "go"
    else:
        phase = "unresolved"

    if no_residual:
        verdict = "stop_no_residual"
    elif no_sign:
        verdict = "stop_no_sign_role"
    elif split_instability["L"] or split_instability["H"]:
        verdict = "report_directions_separately"
    elif unresolved_primary:
        verdict = "unresolved_noise"
    else:
        verdict = "continue"

    primary_rank = {}
    for band in bands:
        labels = primary["bands"][band]["labels"]
        budget = primary["bands"][band]["budget"]
        primary_rank[band] = _material_ranking(labels, budget)

    return {
        "kill_conditions": {
            "no_residual": bool(no_residual),
            "no_sign_role": bool(no_sign),
            "unresolved_noise_primary": bool(unresolved_primary),
            "split_instability": {band: bool(v) for band, v in
                                  split_instability.items()},
        },
        "material_rankings": {band: rankings[band] for band in bands},
        "primary_ranking": primary_rank,
        "phase_aware_closure": phase,
        "verdict": verdict,
    }
