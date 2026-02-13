import math
from dataclasses import dataclass
from typing import Callable, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

@dataclass(frozen=True)
class PowerLawFit:
    """
    Power-law fit in log10-space:

        log10(S) = a * log10(nu) + b
        S = beta * nu^{-alpha}, where alpha = -a, beta = 10**b

    Attributes
    ----------
    a, b : float
        Linear coefficients in log10 space.
    cov : (2,2) ndarray
        Covariance matrix of [a, b].
    alpha, beta : float
        Power-law parameters S = beta * nu^{-alpha}.
    sigma_alpha, sigma_b : float
        1-sigma uncertainties on alpha and b (in log10 space).
    """
    a: float
    b: float
    cov: np.ndarray
    alpha: float
    beta: float
    sigma_alpha: float
    sigma_b: float

    def predict_S(self, nu: np.ndarray | float) -> np.ndarray | float:
        """Predict S(nu) in mJy."""
        x = np.log10(nu)
        y = self.b + self.a * x
        return 10.0 ** y

    def sigma_y_at(self, nu: np.ndarray | float) -> np.ndarray | float:
        """Uncertainty of y=log10(S) at frequency nu. (Logspace)"""
        x = np.log10(nu)
        v = np.vstack([np.atleast_1d(x), np.ones_like(np.atleast_1d(x))])  # shape (2, N)
        var_y = (v * (self.cov @ v)).sum(axis=0)
        sig_y = np.sqrt(var_y)
        return sig_y if np.ndim(x) else sig_y.item()

    def sigma_S_at(self, nu: np.ndarray | float) -> np.ndarray | float:
        """Uncertainty of S at frequency nu via error propagation. (Linear space)"""
        S = self.predict_S(nu)
        sig_y = self.sigma_y_at(nu)
        sig_S = np.log(10.0) * S * sig_y
        return sig_S


def fit_powerlaw(freq: np.ndarray, flux: np.ndarray, flux_err: np.ndarray) -> PowerLawFit:
    """
    Weighted linear fit in log10-space. Weights are 1/sigma_y, where
    sigma_y = flux_err / (ln(10)*flux).

    Returns a PowerLawFit with helpers to evaluate S(nu) and uncertainties.
    """
    freq = np.asarray(freq, dtype=float)
    flux = np.asarray(flux, dtype=float)
    flux_err = np.asarray(flux_err, dtype=float)

    # y = log10(S), x = log10(nu), sigma_y by propagation
    x = np.log10(freq)
    y = np.log10(flux)
    sigma_y = flux_err / (flux * np.log(10.0))
    w = 1.0 / sigma_y

    coeffs, cov = np.polyfit(x, y, 1, w=w, cov=True)
    a, b = coeffs
    alpha = -a
    beta = 10.0 ** b
    sigma_alpha = math.sqrt(cov[0, 0])  # same as sigma_a; sign doesn’t matter for alpha
    sigma_b = math.sqrt(cov[1, 1])

    return PowerLawFit(a=a, b=b, cov=cov, alpha=alpha, beta=beta,
                       sigma_alpha=sigma_alpha, sigma_b=sigma_b)


def prepare_plot_band(fit: PowerLawFit,
                      nu_min: float,
                      nu_max: float,
                      n_points: int = 400) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Produce log-spaced grid and the 1σ band around the fit, ready for plotting.

    Returns
    -------
    nu_grid, S_fit, S_lower, S_upper
    """
    nu_grid = np.logspace(np.log10(nu_min), np.log10(nu_max), n_points)
    S_fit = fit.predict_S(nu_grid)
    sig_y = fit.sigma_y_at(nu_grid)
    # Convert ±sigma in log space to multiplicative bounds in linear space
    S_upper = 10.0 ** (np.log10(S_fit) + sig_y)
    S_lower = 10.0 ** (np.log10(S_fit) - sig_y)
    return nu_grid, S_fit, S_lower, S_upper


def point_deviation_from_fit(fit: PowerLawFit,
                             nu_meas: float,
                             S_meas: float,
                             sigma_meas: float) -> Tuple[float, float, float, float]:
    """
    Compare a single measurement against the fit at nu_meas.

    Returns
    -------
    S_pred : float
        Predicted flux from the fit.
    sigma_pred : float
        1σ uncertainty from the fit at nu_meas.
    z_fit : float
        (S_meas - S_pred) / sigma_pred      — deviation vs. fit uncertainty only.
    z_combined : float
        (S_meas - S_pred) / sqrt(sigma_pred^2 + sigma_meas^2) — combined uncertainty.
    """
    S_pred = float(fit.predict_S(nu_meas))
    sigma_y_pred = float(fit.sigma_y_at(nu_meas))
    sigma_y_meas = float(S_sigma) / (float(S_meas) * math.log(10.0)) 
    # Logspace uncertainty
    sigma_y_comb = math.hypot(sigma_y_pred, sigma_y_meas)
    # Logspace difference
    y_diff = (math.log10(S_meas) - math.log10(S_pred))
    # 
    return 


# --- Helpers ---
def _scatter_with_errors(ax, f, s, e, *, label=None, facecolor="k", edgecolor="k", marker="o", star_color="r", star_marker="*", star_ms=7.0):
    # ax.errorbar(f, s, yerr=e, fmt=marker, mec=edgecolor, mfc=facecolor,
    #             ecolor=edgecolor, elinewidth=1.0, ms=4.5, lw=0.0, capsize=3, label=label)
    if f.size > 1:
        ax.errorbar(
            f[:-1], s[:-1], yerr=e[:-1],
            fmt=marker, mec=edgecolor, mfc=facecolor,
            ecolor=edgecolor, elinewidth=1.0, ms=4.5, lw=0.0, capsize=3,
            label=label  # keep the legend on the bulk points
        )

    # Last point is own
    ax.errorbar(
        f[-1], s[-1], yerr=e[-1],
        fmt=star_marker, mec=star_color, mfc=star_color,
        ecolor=edgecolor, elinewidth=1.0, ms=star_ms, lw=0.0, capsize=3,
        label=None  # avoid duplicate legend entry
    )


def _fit_line(ax, fit: PowerLawFit, fmin: float, fmax: float, *, ls="--", color="k", lw=1.0, n=200):
    g = np.logspace(np.log10(fmin), np.log10(fmax), n)
    ax.plot(g, fit.predict_S(g), ls=ls, color=color, lw=lw)
    return g

def _fit_with_band(ax, fit, fmin, fmax, *, color="k", ls="--", lw=1.0, alpha=0.18, n_points=400):
    nu, S_fit, S_lo, S_up = prepare_plot_band(fit, fmin, fmax, n_points=n_points)
    ax.fill_between(nu, S_lo, S_up, alpha=alpha, linewidth=0, color=color)
    ax.plot(nu, S_fit, ls=ls, lw=lw, color=color)


def _alpha_text(alpha: float, sigma: float) -> str:
    return rf"$\alpha_{{\rm fit}}={alpha:.2f}\pm{sigma:.2f}$"


# --- Plotting ---
def plot_rxj1720_seds(
    *,
    # Panel (a)
    minihalo: Tuple[np.ndarray, np.ndarray, np.ndarray],
    bcg: Tuple[np.ndarray, np.ndarray, np.ndarray],
    # Panel (b)
    central: Tuple[np.ndarray, np.ndarray, np.ndarray],
    tail: Tuple[np.ndarray, np.ndarray, np.ndarray],
    fig_size=(11.5, 5.0),
    savepath: Optional[str] = None,
):
    fig, (axA, axB) = plt.subplots(1, 2, figsize=fig_size)

    # ---------- Panel (a): minihalo + BCG ----------
    f_mh, s_mh, e_mh = minihalo
    f_bcg, s_bcg, e_bcg = bcg

    fit_mh = fit_powerlaw(f_mh, s_mh, e_mh)
    fit_bcg = fit_powerlaw(f_bcg, s_bcg, e_bcg)

    _scatter_with_errors(axA, f_mh, s_mh, e_mh, facecolor="k", edgecolor="k")
    _scatter_with_errors(axA, f_bcg, s_bcg, e_bcg, facecolor="w", edgecolor="k")

    # Fit lines (dashed) spanning the panel’s frequency range
    fmin_a = 0.025  # in GHz
    fmax_a = 30
    _fit_with_band(axA, fit_mh, fmin_a, fmax_a)
    _fit_with_band(axA, fit_bcg, fmin_a, fmax_a, ls="-", lw=1.0)

    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlabel("Frequency (GHz)")
    axA.set_ylabel("Flux (mJy)")
    axA.set_title("Total flux of minihalo and BCG")
    axA.set_xlim(0.01, 100)
    axA.set_ylim(0.3, 5000)
    axA.text(0.55, 0.70, "minihalo", transform=axA.transAxes)
    axA.text(0.53, 0.64, _alpha_text(fit_mh.alpha, fit_mh.sigma_alpha), transform=axA.transAxes)
    axA.text(0.18, 0.18, "BCG", transform=axA.transAxes)
    axA.text(0.18, 0.12, _alpha_text(fit_bcg.alpha, fit_bcg.sigma_alpha), transform=axA.transAxes)

    # ---------- Panel (b): central + tail ----------
    f_c, s_c, e_c = central
    f_t, s_t, e_t = tail

    fit_c = fit_powerlaw(f_c, s_c, e_c)
    fit_t = fit_powerlaw(f_t, s_t, e_t)

    _scatter_with_errors(axB, f_c, s_c, e_c, facecolor="k", edgecolor="k")
    _scatter_with_errors(axB, f_t, s_t, e_t, facecolor="k", edgecolor="k", marker="s")

    fmin_b = 0.06   # (60 MHz)
    fmax_b = 30.0   # 30 GHz
    _fit_with_band(axB, fit_c, fmin_b, fmax_b)
    _fit_with_band(axB, fit_t, fmin_b, fmax_b)

    axB.set_xscale("log")
    axB.set_yscale("log")
    axB.set_xlabel("Frequency (GHz)")
    axB.set_title("Total flux of minihalo centre and tail")
    axB.set_xlim(0.01, 100)
    axB.set_ylim(0.3, 1000)
    axB.text(0.58, 0.70, "central part", transform=axB.transAxes)
    axB.text(0.58, 0.64, _alpha_text(fit_c.alpha, fit_c.sigma_alpha), transform=axB.transAxes)
    axB.text(0.18, 0.28, "tail", transform=axB.transAxes)
    axB.text(0.18, 0.22, _alpha_text(fit_t.alpha, fit_t.sigma_alpha), transform=axB.transAxes)

    # Cosmetics to echo the paper’s feel
    for ax in (axA, axB):
        ax.minorticks_on()
        ax.grid(False)
        # clean legend-less layout
    fig.tight_layout(w_pad=1.5)

    if savepath:
        fig.savefig(savepath, dpi=300, bbox_inches="tight")
    return fig


# --- Data ---
mh_freq = np.array([0.317, 0.617, 1.28, 1.48, 4.86, 8.44, 10])
mh_flux = np.array([365,   170,   65,    68,    20.3,  6.6, 8.61])
mh_err  = np.array([58,    12,    4,     5,     1.5,   0.7, 0.56])

bcg_freq = mh_freq
# Estimated own points now
bcg_flux = np.array([24, 11, 6.9, 6.7, 2.3, 1.4, 1.27])
bcg_err  = np.array([2, 1, 0.4, 0.3, 0.1, 0.1, 0.2])

central_freq = mh_freq
central_flux = np.array([286, 144, 59, 60, 18.7, 6.2, 7.60])
central_err  = np.array([38, 11, 3, 5, 1.3, 0.6, 0.52])

tail_freq = mh_freq
tail_flux = np.array([79, 26, 6, 8, 1.6, 0.2, 1.01])
tail_err  = np.array([6, 2, 1, 1, 0.5, 0.2, 0.35])

# --- Recreate G14 plot with our points ---
plot_rxj1720_seds(
    minihalo=(mh_freq, mh_flux, mh_err),
    bcg=(bcg_freq, bcg_flux, bcg_err),
    central=(central_freq, central_flux, central_err),
    tail=(tail_freq, tail_flux, tail_err),
    savepath="rxj1720_seds.png",
)


# --- Check our point against previous spectral index ---
for flux, err, label in zip([mh_flux, central_flux, tail_flux], [mh_err, central_err, tail_err], ["Total", "Centre", "Tail"]):
    # Fit the power law excluding 8.44 GHz and ours
    fit = fit_powerlaw(mh_freq[:-2], flux[:-2], err[:-2])

    # Prepare a plotting band (extend a touch below min for nicer look)
    nu_min = 10 ** (np.log10(mh_freq.min()) - 0.1)
    nu_max = 12.0
    nu_grid, S_fit, S_lower, S_upper = prepare_plot_band(fit, nu_min, nu_max, n_points=400)

    # Single-point comparison @ 10 GHz
    nu_meas = mh_freq[-1]
    S_meas = flux[-1]
    sigma_meas = err[-1]
    S_pred, sigma_pred, = fit.predict_S(nu_meas), fit.sigma_S_at(nu_meas)

    print(f"Minihalo {label}")
    print(f"alpha (<8.44 Ghz) = {fit.alpha:.3f} ± {fit.sigma_alpha:.3f}")
    print(f"S_10GHz(pred) = {S_pred:.3f} ± {sigma_pred:.3f} mJy")
    print(f"S_10GHz(meas) = {S_meas:.3f} ± {sigma_meas:.3f} mJy mJy  →  Δ = {S_meas - S_pred:.4f} mJy")

    # Plot
    plt.figure(figsize=(7.5, 5.5))
    plt.errorbar(mh_freq[:-1], flux[:-1], yerr=err[:-1], fmt='o', label="G14 + 1σ", capsize=3)
    plt.plot(nu_grid, S_fit, '-', label="Weighted fit (power law)")
    plt.fill_between(nu_grid, S_lower, S_upper, alpha=0.25, label="Fit 1σ band")
    plt.errorbar(nu_meas, S_meas, yerr=sigma_meas, fmt='*', c='r', ecolor='k', label="10 GHz Meas.", capsize=3)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Flux density (mJy)")
    plt.title("RX J1720.1+2638 Total Minihalo Flux\nWeighted power-law fit (G14) compared to 10 GHz measurement")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"minihalo_fit_{label.lower()}.png")
