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
    subband: Tuple[np.ndarray, np.ndarray, np.ndarray],
    subband_agn: Tuple[np.ndarray, np.ndarray, np.ndarray],
    fig_size=(11.5, 5.0),
    savepath: Optional[str] = None,
):
    fig, (axA, axB) = plt.subplots(1, 2, figsize=fig_size)

    # ---------- Panel (a): minihalo + BCG + power-laws ----------
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
    # Add alpha = 1 upper limit from Savini
    x_points = np.logspace(np.log10(fmin_a), np.log10(fmax_a), 400)
    axA.plot(x_points, f_mh[0]*s_mh[0] * x_points ** -1, c='r')
    
    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlabel("Frequency (GHz)")
    axA.set_ylabel("Flux (mJy)")
    axA.set_title("Total flux of minihalo and BCG")
    axA.set_xlim(1, 20)
    axA.set_ylim(0.2, 1000)
    axA.text(0.55, 0.70, "minihalo", transform=axA.transAxes)
    axA.text(0.53, 0.64, _alpha_text(fit_mh.alpha, fit_mh.sigma_alpha), transform=axA.transAxes)
    axA.text(0.18, 0.18, "BCG", transform=axA.transAxes)
    axA.text(0.18, 0.12, _alpha_text(fit_bcg.alpha, fit_bcg.sigma_alpha), transform=axA.transAxes)

    # ---------- Panel (b): Subbands ----------
    fit_sb = fit_powerlaw(*subband)
    _scatter_with_errors(axB, *subband, facecolor="k", edgecolor="k")
    _scatter_with_errors(axB, *subband_agn, facecolor="w", edgecolor="k")
    
    # Fits
    _fit_with_band(axB, fit_mh, fmin_a, fmax_a, ls="--")
    _fit_with_band(axB, fit_bcg, fmin_a, fmax_a)
    _fit_with_band(axB, fit_sb, fmin_a, fmax_a, ls="-.")

    axB.set_xscale("log")
    axB.set_yscale("log")
    axB.set_xlabel("Frequency (GHz)")
    axB.set_ylabel("Flux (mJy)")
    axB.set_title("Sub-band flux of minihalo and BCG")
    axB.set_xlim(6, 14)
    axB.set_ylim(0.1, 10)
    
    # Cosmetics to echo the paper’s feel
    axA.minorticks_on()
    axA.grid(False)
    fig.tight_layout(w_pad=1.5)

    if savepath:
        fig.savefig(savepath, dpi=300, bbox_inches="tight")
    return fig


# --- Data ---
mh_freq = np.array([1.40, 10])
mh_flux = np.array([16.6, 0.31])
mh_err  = np.array([3, 0.029])

bcg_freq = np.array([1.4, 4.9, 10])
bcg_flux = np.array([31, 9.6, 5.41])
bcg_err  = np.array([1.6, 0.5, 0.13])

subband_freq = np.array([8.5, 9.5, 10.5, 11.5])
subband_flux = np.array([0.52, 0.35, 0.26, 0.17])
subband_err = np.array([0.06, 0.03, 0.03, 0.08])

subband_agn_freq = np.array([8.5, 9.5, 10.5, 11.5])
subband_agn_flux = np.array([6.03, 5.53, 5.15, 4.75])
subband_agn_err = np.array([0.02, 0.02, 0.02, 0.02])

# --- Plot SED ---
plot_seds(
    minihalo=(mh_freq, mh_flux, mh_err),
    bcg=(bcg_freq, bcg_flux, bcg_err),
    subband=(subband_freq, subband_flux, subband_err),
    subband_agn=(subband_agn_freq, subband_agn_flux, subband_agn_err),
    savepath="A478_seds.png",
)

