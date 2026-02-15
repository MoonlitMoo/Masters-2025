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
    # Trehaeven 
    # fit_tr = PowerLawFit.from_existing(1.0, 1.1, 1.283, 7.91, 2.59)
    # _fit_with_band(axA, fit_tr, fmin_a, fmax_a, ls="-.", lw=1.0)
    
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
    
    # Cosmetics
    axA.minorticks_on()
    axA.grid(False)
    fig.tight_layout(w_pad=1.5)

    if savepath:
        fig.savefig(savepath, dpi=300, bbox_inches="tight")
    return fig


# --- Data ---
mh_freq = np.array([1.283, 10])
mh_flux = np.array([7.91, 0.97])
mh_err  = np.array([2.59, 0.15])

bcg_freq = np.array([1.283, 10])
bcg_flux = np.array([8.73, 2.27])
bcg_err  = np.array([0.88, 0.21])

# --- Plot SED ---
plot_seds(
    minihalo=(mh_freq, mh_flux, mh_err),
    bcg=(bcg_freq, bcg_flux, bcg_err),
    savepath="rxjc115_seds.png",
)

# Extrapolate fit from Trehaeven
fit = PowerLawFit.from_existing(1.0, 1.1, 1.283, 7.91, 2.59)
pred_10 = fit.predict_S(10)
pred_10_sigma = fit.sigma_S_at(10)
print(f"Predicted from Trehaeven: S = {pred_10:1.2f} +/- {pred_10_sigma:1.2f} mJy")