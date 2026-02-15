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
    comp: Tuple[np.ndarray, np.ndarray, np.ndarray],
    fig_size=(8, 5.0),
    savepath: Optional[str] = None,
):
    fig, axA = plt.subplots(1, 1, figsize=fig_size)

    # ---------- Panel (a): minihalo + BCG + power-laws ----------
    f_bcg, s_bcg, e_bcg = bcg

    fit_bcg = fit_powerlaw(f_bcg, s_bcg, e_bcg)
    fit_comp = fit_powerlaw(*comp)

    _scatter_with_errors(axA, f_bcg, s_bcg, e_bcg, facecolor="w", edgecolor="k")
    _scatter_with_errors(axA, *comp, facecolor="k", edgecolor="k")

    # Fit lines (dashed) spanning the panel’s frequency range
    fmin_a = 0.025  # in GHz
    fmax_a = 30
    _fit_with_band(axA, fit_bcg, fmin_a, fmax_a, ls="-", lw=1.0)
    _fit_with_band(axA, fit_comp, fmin_a, fmax_a, ls="--", lw=1.0)
    
    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlabel("Frequency (GHz)")
    axA.set_ylabel("Flux (mJy)")
    axA.set_title("Total flux of BCG and companion galaxy")
    # axA.set_xlim(1, 20)
    # axA.set_ylim(0.2, 1000)
    axA.text(0.55, 0.70, "comp", transform=axA.transAxes)
    axA.text(0.53, 0.64, _alpha_text(fit_comp.alpha, fit_comp.sigma_alpha), transform=axA.transAxes)
    axA.text(0.18, 0.18, "BCG", transform=axA.transAxes)
    axA.text(0.18, 0.12, _alpha_text(fit_bcg.alpha, fit_bcg.sigma_alpha), transform=axA.transAxes)
    
    # Cosmetics
    axA.minorticks_on()
    axA.grid(False)
    fig.tight_layout(w_pad=1.5)

    if savepath:
        fig.savefig(savepath, dpi=300, bbox_inches="tight")
    return fig


# 1.4 from G19, 144 from Benzin (offset-5), 144 from Ignesti2022. Both 144 incl S2 + lobes. Unsure about G19
# second 10 GHz (offset by -5) includes the estimated flux for agn lobes
bcg_freq = np.array([0.139, 0.144, 1.4, 10, 10.05])
bcg_flux = np.array([852, 750, 16, 3.01, 3.01+0.26+0.12])
bcg_err  = np.array([135, 150, 1, 0.17, 0.2])

comp_freq = np.array([1.4, 10])
comp_flux = np.array([1, 0.15])
comp_err  = np.array([0.1, 0.05])
# --- Plot SED ---
plot_seds(
    bcg=(bcg_freq, bcg_flux, bcg_err),
    comp=(comp_freq, comp_flux, comp_err),
    savepath="2a0335_seds.png",
)

# Estimate the fossil lobe flux from ~1.5 found by Igensti2022 and the points found by G19
arcsec_kpc_area = 0.716 ** 2  # kpc^2 / arcsec^2
beam_area = 6.68 * 5.14 * np.pi  # arcsec^2
lobe_area = (35/2) ** 2 * np.pi  # kpc^2
n_beams_lobe = lobe_area / (beam_area * arcsec_kpc_area)
print(f'Beams per lobe: {n_beams_lobe} and {n_beams_lobe*1.4} for the relic')
fit_se = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=4.1, sigma_S0=0.2)
print(f"Estimated flux of south east lobe: {fit_se.predict_S(10):1.2e} +/- {fit_se.sigma_S_at(10):1.2e} mJy " + 
    f"or {fit_se.predict_S(10)/n_beams_lobe:1.2e} mJy per beam") 

fit_nw = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=2.7, sigma_S0=0.1)
print(f"Estimated flux of south east lobe: {fit_nw.predict_S(10):1.2e} +/- {fit_nw.sigma_S_at(10):1.2e} mJy " + 
    f"or {fit_nw.predict_S(10)/n_beams_lobe:1.2e} mJy per beam") 

fit_relic = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=3.1, sigma_S0=0.1)
print(f"Estimated flux of south east lobe: {fit_relic.predict_S(10):1.2e} +/- {fit_relic.sigma_S_at(10):1.2e} mJy " + 
    f"or {fit_relic.predict_S(10)/(n_beams_lobe*1.4):1.2e} mJy per beam")


# Plot the normalised per beam
fit_se = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=4.1/n_beams_lobe, sigma_S0=0.2/np.sqrt(n_beams_lobe))
fit_nw = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=2.7/n_beams_lobe, sigma_S0=0.1/np.sqrt(n_beams_lobe))
fit_relic = PowerLawFit.from_existing(alpha=1.5, sigma_alpha=0.1, nu0=1.4, S0=3.1/n_beams_lobe, sigma_S0=0.1/np.sqrt(n_beams_lobe))

print(f"Southeast lobe: {fit_se.predict_S(10):1.2e} +/- {fit_se.sigma_S_at(10):1.2e} mJy/beam")
print(f"Northwest lobe: {fit_nw.predict_S(10):1.2e} +/- {fit_nw.sigma_S_at(10):1.2e} mJy/beam")
print(f"Relic lobe: {fit_relic.predict_S(10):1.2e} +/- {fit_relic.sigma_S_at(10):1.2e} mJy")

fig, ax = plt.subplots(1, 1)
fmin_a = 0.025
fmax_a = 30
_fit_with_band(ax, fit_se, fmin_a, fmax_a, ls="-", lw=1.0)
_fit_with_band(ax, fit_nw, fmin_a, fmax_a, ls="--", lw=1.0)
_fit_with_band(ax, fit_relic, fmin_a, fmax_a, ls="-.", lw=1.0)
plt.axhline(2.56e-3 * 3, c='k')
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Frequency (GHz)")
ax.set_ylabel("Flux (mJy)")
ax.minorticks_on()
ax.set_xlim(8, 12)
ax.set_ylim(1e-3, 1e-1)
    