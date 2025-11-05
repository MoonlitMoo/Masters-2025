import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.stats import chi2 as chi2dist

def calculate_scaling(freq1, flux1, err1, freq2, flux2, err2):
    """
    Fit coefficient g so that flux2 = g * flux1, using weights 1/(e1^2+e2^2).
    """
    # Combined weights on the difference
    w = 1.0 / (err1**2 + err2**2)

    # Weighted least-squares solution for g:
    # minimize sum w * (f2 - g f1)^2  =>  g = sum(w f1 f2)/sum(w f1^2)
    S1 = np.sum(w * flux1 * flux2)
    S2 = np.sum(w * flux1**2)
    g = S1 / S2

    # 1σ uncertainty on g
    sigma_g = 1.0 / np.sqrt(S2)

    return g, sigma_g


def plot_comparison(freq, flux1, err1, flux2, err2, g, sigma_g, title):
    """
    Top: both spectra with 1σ error bars.
    Bottom: ratio f2/f1 with error bars, best-fit g as a line, and ±1σ band.
    """
    ratio = flux2 / flux1
    # Propagate errors for the ratio (ignoring correlation): σ_r = r * sqrt((e1/f1)^2 + (e2/f2)^2)
    ratio_err = ratio * np.sqrt((err1/flux1)**2 + (err2/flux2)**2)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[2, 1], figsize=(8, 6))

    # Top panel: fluxes
    ax1.errorbar(freq, flux1, yerr=err1, fmt='o', ms=4, capsize=2, label='Dconfig1')
    ax1.errorbar(freq, flux2, yerr=err2, fmt='s', ms=4, capsize=2, label='Dconfig2')
    ax1.set_ylabel("Flux density")
    ax1.set_title(title)
    ax1.grid(True, ls='--', alpha=0.3)
    ax1.legend()

    # Bottom panel: ratio and fitted normalisation
    ax2.errorbar(freq, ratio, yerr=ratio_err, fmt='.', ms=5, alpha=0.9, label='Dconfig2 / Dconfig1')
    ax2.axhline(g, ls='--', lw=1.5, label=f'Best-fit g = {g:.4f}')
    ax2.axhline(1, ls='--', lw=1, c='r', label=None)
    ax2.fill_between(freq, g - sigma_g, g + sigma_g, alpha=0.15, step='mid', label='±1σ on g')
    ax2.set_xlabel("Frequency")
    ax2.set_ylabel("Ratio")
    ax2.grid(True, ls='--', alpha=0.3)
    ax2.legend(loc='best')

    plt.tight_layout()
    plt.savefig('secondary_models.png', dpi=300)
    plt.show()

# --- Load data ---
df = pd.read_csv("secondarymodels.csv")
dconfig1_freq = df.iloc[:, 0]
dconfig1_flux = df.iloc[:, 1]
dconfig1_err = df.iloc[:, 2]
dconfig2_freq = df.iloc[:, 3]
dconfig2_flux = df.iloc[:, 4]
dconfig2_err = df.iloc[:, 5]


# --- Run Comparisonn ---
g, sigma_g = calculate_scaling(
    dconfig1_freq, dconfig1_flux, dconfig1_err,
    dconfig2_freq, dconfig2_flux, dconfig2_err
)

print(f"g = {g:.6f} ± {sigma_g:.6f}")
print(f"Second obs changes by {(g-1) * 100:2.1f}%")

plot_comparison(
    dconfig1_freq, dconfig1_flux, dconfig1_err,
    dconfig2_flux, dconfig2_err,
    g=g, sigma_g=sigma_g,
    title="RXJ1720+2638 D config \nSecondary calibrator models"
)
