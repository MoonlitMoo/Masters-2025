import math
from typing import Callable, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# --- Plotting ---
def plot_seds(
    *,
    # Panel (a)
    minihalo: Tuple[np.ndarray, np.ndarray, np.ndarray],
    bcg: Tuple[np.ndarray, np.ndarray, np.ndarray],
    # Panel (b)
    fig_size=(11.5, 5.0),
    savepath: Optional[str] = None,
):
    fig, axA = plt.subplots(1, 1, figsize=fig_size)

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
    axA.set_xlim(1, 20)
    axA.set_ylim(0.1, 5000)
    axA.text(0.55, 0.70, "minihalo", transform=axA.transAxes)
    axA.text(0.53, 0.64, _alpha_text(fit_mh.alpha, fit_mh.sigma_alpha), transform=axA.transAxes)
    axA.text(0.18, 0.18, "BCG", transform=axA.transAxes)
    axA.text(0.18, 0.12, _alpha_text(fit_bcg.alpha, fit_bcg.sigma_alpha), transform=axA.transAxes)

    # Cosmetics to echo the paper’s feel
    axA.minorticks_on()
    axA.grid(False)
    fig.tight_layout(w_pad=1.5)

    if savepath:
        fig.savefig(savepath, dpi=300, bbox_inches="tight")
    return fig


# --- Data ---
mh_freq = np.array([1.40, 8.5, 9.5, 10.5, 11.5])
mh_flux = np.array([16.6, 0.52, 0.35, 0.26, 0.16])
mh_err  = np.array([3, 0.19, 0.09, 0.07, 0.13])

bcg_freq = np.array([1.4, 4.9, 8.5, 9.5, 10.5, 11.5])
bcg_flux = np.array([31, 9.6, 6.033, 5.535, 5.145, 4.750])
bcg_err  = np.array([1.6, 0.5, 0.023, 0.019, 0.016, 0.02])

# --- Recreate plot with our points ---
plot_seds(
    minihalo=(mh_freq[1:], mh_flux[1:], mh_err[1:]),
    bcg=(bcg_freq[2:], bcg_flux[2:], bcg_err[2:]),
    savepath="A478_subband_seds.png",
)


# --- Total minihalo only ---
fit = fit_powerlaw(mh_freq, mh_flux, mh_err)

# Prepare a plotting band (extend a touch below min for nicer look)
nu_min = 10 ** (np.log10(mh_freq.min()) - 0.1)
nu_max = 12.0
nu_grid, S_fit, S_lower, S_upper = prepare_plot_band(fit, nu_min, nu_max, n_points=400)

# Example single-point comparison @ 10 GHz
nu_meas = mh_freq[-1]
S_meas = mh_flux[-1]
sigma_meas = mh_err[-1]
S_pred, sigma_pred, z_fit, z_combined = point_deviation_from_fit(fit, nu_meas, S_meas, sigma_meas)

# Plot
plt.figure(figsize=(7.5, 5.5))
plt.errorbar(mh_freq[:-1], mh_flux[:-1], yerr=mh_err[:-1], fmt='o', label="G14 + 1σ", capsize=3)
plt.plot(nu_grid, S_fit, '-', label="Weighted fit (power law)")
plt.fill_between(nu_grid, S_lower, S_upper, alpha=0.25, label="Fit 1σ band")
plt.errorbar(nu_meas, S_meas, yerr=sigma_meas, fmt='*', c='r', ecolor='k', label="Us =)", capsize=3)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Frequency (GHz)")
plt.ylabel("Flux density (mJy)")
plt.title("A478 Total Minihalo Flux\nWeighted power-law fit for sub band measurements")
plt.legend()
plt.tight_layout()
plt.savefig("minihalo_fit.png")

# Console summary
print(f"alpha = {fit.alpha:.3f} ± {fit.sigma_alpha:.3f}")
print(f"S_10GHz(pred) = {S_pred:.3f} ± {sigma_pred:.3f} mJy")
print(f"S_10GHz(meas) = {S_meas:.3f} mJy  →  Δ = {S_meas - S_pred:.4f} mJy,  z_fit = {z_fit:.2f},  z_combined = {z_combined:.2f}")


