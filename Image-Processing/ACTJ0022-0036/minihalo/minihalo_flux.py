import math
from typing import Callable, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




# --- Plotting ---
def plot_seds(
    *,
    # Panel (a)
    bcg: Tuple[np.ndarray, np.ndarray, np.ndarray],
    # Panel (b)
    fig_size=(6, 6),
    savepath: Optional[str] = None,
):
    fig, axA = plt.subplots(1, 1, figsize=fig_size)

    # ---------- Panel (a): BCG + power-laws ----------
    f_bcg, s_bcg, e_bcg = bcg

    fit_bcg = fit_powerlaw(f_bcg, s_bcg, e_bcg)

    _scatter_with_errors(axA, f_bcg, s_bcg, e_bcg, facecolor="w", edgecolor="k")
    
    # Fit lines (dashed) spanning the panel’s frequency range
    fmin_a = 0.025  # in GHz
    fmax_a = 30
    _fit_with_band(axA, fit_bcg, fmin_a, fmax_a, ls="-", lw=1.0)
    
    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlabel("Frequency (GHz)")
    axA.set_ylabel("Flux (mJy)")
    axA.set_title("Total flux of BCG")
    axA.set_xlim(0.5, 12)
    axA.set_ylim(0.1, 100)
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
bcg_freq = np.array([0.610, 1.4, 10])
bcg_flux = np.array([46.8, 19.02, 3.89])
bcg_err  = np.array([0.2, 0.93, 0.04])

plot_seds(bcg=(bcg_freq, bcg_flux, bcg_err))

# Plot this
# Extrapolate fit from Knowles19
fit = fit_powerlaw(bcg_freq[:-1], bcg_flux[:-1], bcg_err[:-1])
pred_10 = fit.predict_S(10)
pred_10_sigma = fit.sigma_S_at(10)
print(f"Fit using G19: alpha = {fit.alpha:1.2f} +/- {fit.sigma_alpha:1.2f}")
print(f"Predicted minihalo flux from G19: S = {pred_10:1.2f} +/- {pred_10_sigma:1.2f} mJy")
