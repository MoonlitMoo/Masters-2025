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
    
    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlabel("Frequency (GHz)")
    axA.set_ylabel("Flux (mJy)")
    axA.set_title("Total flux of minihalo and BCG")
    axA.set_xlim(0.1, 20)
    axA.set_ylim(0.1, 1000)
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
mh_freq = np.array([1.4, 10])
mh_flux = np.array([21, 0.360])
mh_err  = np.array([1.6, 0.7, 0.2, 0.2, 0.1])

bcg_freq = np.array([1.4, 10])
bcg_flux = np.array([58.9, 11.1])
bcg_err  = np.array([2.9, 1.0])

s2_freq = np.array([1.4, 10])
s2_flux = np.array([1.6, 0.15])
s2_err  = np.array([0.1, 0.02])

# --- Plot SED ---
# plot_seds(
#     minihalo=(mh_freq, mh_flux, mh_err),
#     bcg=(bcg_freq, bcg_flux, bcg_err),
#     savepath="rxj2129_seds.png",
# )

# Fit BCG and S2
fit_bcg = fit_powerlaw(bcg_freq, bcg_flux, bcg_err)
fit_s2 = fit_powerlaw(s2_freq, s2_flux, s2_err)

print(f"AGN spectral index fit: alpha = {fit_bcg.alpha:1.2f} +/- {fit_bcg.sigma_alpha:1.2f}")
print(f"S2 spectral index fit: alpha = {fit_s2.alpha:1.2f} +/- {fit_s2.sigma_alpha:1.2f}")
