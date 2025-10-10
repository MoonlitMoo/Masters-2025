import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# G14 Data (GHz + mJy units), minihalo total
freq = np.array([0.317, 0.617, 1.28, 1.48, 4.86, 8.44])
flux = np.array([365, 170, 65, 68, 20.3, 6.6])
flux_err = np.array([58, 12, 4, 5, 1.5, 0.7])

# Assume power law fit BS^-A -> log10(B) - Alog10(S) -> f = ax + b (a = -A, x = log10(S), b = log10(B))
# Need dx so with x = log10(S), dx ~ d(log10(S)) = ln(S)/ln(10) = dS/(ln(10) * S)
log_error = flux_err / (flux * np.log(10))
weights = 1 / log_error
coeffs, cov = np.polyfit(np.log10(freq), np.log10(flux), 1, w=weights, cov=True)

# Get the actual coefs
a, b = coeffs
alpha = -a
beta = 10 ** b
sigma_alpha = np.sqrt(cov[0,0])  # Negative doesn't matter
sigma_b = np.sqrt(cov[1,1])

# Predicted value at 10GHz
f_meas = 10
x_meas = np.log10(f_meas)
y_meas_pred = a * x_meas + b
S_meas_pred = 10 ** y_meas_pred
# Error to image value + discrepancy to prediction
sigma_y_pred = np.sqrt(np.array([x_meas, 1.0]) @ cov @ np.array([x_meas, 1.0]))  # Calc variance from the fit
sigma_S_pred = np.log(10) * S_meas_pred * sigma_y_pred  # Calculate the flux sigma from inverse of prev formula

# Measured vals for total minihalo flux
S_meas = 8.72
sigma_meas = 0.44

# Get sigma deviation
delta_S = S_meas - S_meas_pred
z_fit = delta_S / sigma_S_pred
sigma_combined = np.sqrt(sigma_S_pred**2 + sigma_meas**2)
z_combined = delta_S / sigma_combined

# Plotting as provided by ChatGPT since I don't know how to plot the filled bit :)
nu_grid = np.logspace(np.log10(freq.min()) - 0.1, np.log10(12.0), 400)
xg = np.log10(nu_grid)
yg = b + a * xg
Sg = 10**yg

A = np.vstack([xg, np.ones_like(xg)])  # shape (2,N)
var_y_g = (A * (cov @ A)).sum(axis=0)   # v^T C v for each column
sig_y_g = np.sqrt(var_y_g)
Sg_upper = 10**(yg + sig_y_g)
Sg_lower = 10**(yg - sig_y_g)

plt.figure(figsize=(7.5, 5.5))
plt.errorbar(freq, flux, yerr=flux_err, fmt='o', label="G14 + 1σ")
plt.plot(nu_grid, Sg, '-', label="Weighted fit (power law)")
plt.fill_between(nu_grid, Sg_lower, Sg_upper, alpha=0.25, label="Fit 1σ band")
plt.errorbar(10, S_meas, yerr=sigma_meas, fmt='*', label="My measurement")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Frequency (GHz)")
plt.ylabel("Flux density (mJy)")
plt.title("RX J1720.1+2638 Total Minihalo Flux\nWeighted power-law fit (G14) and 10 GHz measurement")
plt.legend()
plt.tight_layout()

print(f"alpha = {alpha:.3f} ± {sigma_alpha:.3f}")
print(f"S_10GHz(pred) = {S_meas_pred:.3f} ± {sigma_S_pred:.3f} mJy")
print(f"S_10GHz(meas) = {S_meas:.3f} mJy  →  Δ = {delta_S:.4f} mJy,  z_fit = {z_fit:.2f},  z_combined = {z_combined:.2f}")
print(f"")

plt.savefig("minihalo_fit.png")
