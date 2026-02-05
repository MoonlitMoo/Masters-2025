# --- Plot the uvrange cutoff vs flux for RXJ1720+2638 ---
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DATASETS = ["C-config", "D-config1", "D-config2"]
DATA_PATH = "../../../Image-Processing/RXJ1720+2638/minihalo/config_tests/uvrange_config_tests"
uv_cutoffs = [0, 5, 10, 12, 14, 15, 16, 18, 20, 25, 30]
logs = []
for config in ["cconfig-p5", "dconfig1-p5", "dconfig2-p5"]:
    c_logs = []
    for u in uv_cutoffs:
        uvrange = f">{u}klambda"
        c_logs.append(f"{DATA_PATH}/{config}_range_{uvrange}.log")
    logs.append(c_logs)

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 12 * f_scale

def read_log_value(l):
    """ Returns the flux in mJy. """
    pattern = ".*:\s*([\d.]+)\s*\+/-\s*([\d.]+)\s*(?:[um]Jy(?:/beam)?)?"
    if "mJy" not in l and "uJy" not in l:
        print(f"Unknown flux scale in {l}")
        return np.nan, np.nan
    scale = 1 if "mJy" in l else 1/1000

    match = re.match(pattern, l)
    return [float(v) * scale for v in match.groups()]


fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(8.5, 4.2), sharex=True, constrained_layout=True
)

# Style helpers
for ax in (ax1, ax2):
    ax.grid(True, which="major", alpha=0.25)
    ax.grid(True, which="minor", alpha=0.12)

all_flux = {}
handles = []
# Plot absolute values
for data_logset, data_name, c in zip(logs, DATASETS, ["C0", "C1", "C1"]):
    peak_fluxes, peak_flux_errors = [], []
    integrated_fluxes, integrated_flux_errors = [], []

    for log in data_logset:
        with open(log, "r") as f:
            for l in f.readlines():
                if "Peak:" in l:
                    v, e = read_log_value(l)
                    peak_fluxes.append(v); peak_flux_errors.append(e)
                elif "Integrated:" in l:
                    v, e = read_log_value(l)
                    integrated_fluxes.append(v); integrated_flux_errors.append(e)
                elif "*** FIT FAILED ***" in l:
                    peak_fluxes.append(np.nan); peak_flux_errors.append(np.nan)
                    integrated_fluxes.append(np.nan); integrated_flux_errors.append(np.nan)

    peak_fluxes = np.array(peak_fluxes, dtype=float)
    peak_flux_errors = np.array(peak_flux_errors, dtype=float)
    
    all_flux[f"{data_name}_peak"] = peak_fluxes
    all_flux[f"{data_name}_peak_err"] = peak_flux_errors
    
    h1 = ax1.errorbar(
        uv_cutoffs, peak_fluxes, yerr=peak_flux_errors,
        fmt="o-", ms=4, lw=1.2, capsize=2, color=c,
    )
    handles.append(h1)

ax1.set_ylabel(r"Peak (mJy beam$^{-1}$)")

# Relative to C-config (peak), with error propagation
c_name = DATASETS[0]
c_peak = all_flux[f"{c_name}_peak"]
c_err  = all_flux[f"{c_name}_peak_err"]

ax2.axhline(0.0, lw=1.0, alpha=0.4)

for data_name, rel_label in [(DATASETS[1], "D config 1"), (DATASETS[2], "D config 2")]:
    y = all_flux[f"{data_name}_peak"]
    yerr = all_flux[f"{data_name}_peak_err"]

    ratio = y / c_peak
    # sigma(ratio) = ratio * sqrt((sy/y)^2 + (sc/c)^2)
    relerr = ratio * np.sqrt((yerr / y) ** 2 + (c_err / c_peak) ** 2)

    pct = (ratio - 1.0) * 100.0
    pct_err = relerr * 100.0

    ax2.errorbar(
        uv_cutoffs, pct, yerr=pct_err,
        fmt="o-", ms=4, lw=1.2, capsize=2,
        label=rel_label
    )

ax2.set_ylabel("Relative peak flux (D - C) / C (%)")
# Labels/titles
ax1.set_title("Absolute")
ax2.set_title("Relative")
ax2.set_xlabel(r"$uv$ min cut (k$\lambda$)")
ax1.set_xlabel(r"$uv$ min cut (k$\lambda$)")

ax1.axvline(12, c='k', linestyle='--', linewidth=1)
ax2.axvline(12, c='k', linestyle='--', linewidth=1)

ax1.set_xlim(-0.5, 22)
ax2.set_xlim(-0.5, 22)
ax1.set_ylim(0.8, 1.2)
ax2.set_ylim(-20, 5)

# Legends: compact, no frame
ax1.legend(handles,
    ["C-config", "D-config"],
    ncol=2, frameon=False,
    handlelength=2.0, columnspacing=1.2
)

plt.savefig("uvrange_vs_flux.pdf", dpi=300)
