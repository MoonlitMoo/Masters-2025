import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# G14 Data (GHz + mJy units), gave 10% uncertainity to est point at 74 MHz to not kill the polyfit
freq = np.array([0.074, 0.317, 0.617, 1.28, 1.48, 4.86, 8.44])
flux = np.array([80, 24, 11, 6.9, 6.7, 2.3, 1.4])
flux_err = np.array([8, 2.0, 1.0, 0.4, 0.3, 0.1, 0.1])

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

# Measured vals (peak)
# S_meas = 1.1257
# sigma_meas = 0.0091

# Measured vals (integrated)
S_meas = 1.262
sigma_meas = 0.017

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
plt.plot(10, S_meas, marker='*', markersize=12, linestyle='none', label="My measurement")
plt.plot(15.5, 4.4, marker='*', markersize=12, linestyle='none', label="Y22")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Frequency (GHz)")
plt.ylabel("Flux density (mJy)")
plt.title("RX J1720.1+2638 BCG: Weighted power-law fit (G14) and 10 GHz measurement")
plt.legend()
plt.tight_layout()

print(f"alpha = {alpha:.3f} ± {sigma_alpha:.3f}")
print(f"S_10GHz(pred) = {S_meas_pred:.3f} ± {sigma_S_pred:.3f} mJy")
print(f"S_10GHz(meas) = {S_meas:.3f} mJy  →  Δ = {delta_S:.4f} mJy,  z_fit = {z_fit:.2f},  z_combined = {z_combined:.2f}")
print(f"")

plt.savefig("test.png")
