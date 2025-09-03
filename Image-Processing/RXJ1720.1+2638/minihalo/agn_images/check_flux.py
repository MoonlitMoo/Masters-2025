import os
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from casatasks import imfit, imstat

LOG_DIR = "flux_fits"

labels = ["agn", "head-tail", "right"]
regions = ["circle[[17h20m10.03s, 26d37m31.9s], 5.5arcsec]", "circle[[17h20m13.86s, 26d38m25.96s], 5.5arcsec]", "circle[[17h20m01.16s, 26d36m33.3s], 2.75arcsec]"]

images = ["cconfig", "dconfig1", "dconfig2"]

os.makedirs(LOG_DIR, exist_ok=True)

for image in images:
    image_name = f"{image}-p5_agn.image.tt0"
    for region, label in zip(regions, labels):
        imfit(image_name, region=region, logfile=f"{LOG_DIR}/{image}_{label}.log", append=False)
        # imstat(image_name, region=region, logfile=f"{LOG_DIR}/{image}_{label}.log", append=False)


def read_log_value(l: str):
    """Return (flux, error) in mJy from a log line supporting Jy, mJy, and uJy."""
    pattern = r".*:\s*([\d.]+)\s*\+/-\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    # pattern = r".*\[flux\]:\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    match = re.match(pattern, l)
    if not match:
        print(f"Unknown flux scale in {l.strip()}")
        return np.nan, np.nan

    value, error, unit = match.groups()
    value, error = float(value), float(error)
    # value, unit = match.groups()
    # Convert to mJy
    if unit == "Jy":
        scale = 1000.0
    elif unit == "mJy":
        scale = 1.0
    elif unit == "uJy":
        scale = 1.0 / 1000.0
    else:
        scale = np.nan
    return value * scale, error * scale
    # return float(value) * scale, 0 * scale

def get_flux_from_log(log):
    with open(log, "r") as f:
        for l in f.readlines():
            if "Integrated:" in l:
            # if "flux density" in l:
                return read_log_value(l)
            # elif "Integrated:" in l:
            #     return read_log_value(l)
    return np.nan, np.nan


data = []

for logfile in os.listdir(LOG_DIR):
    base = os.path.splitext(logfile)[0]
    try:
        dataset, position = base.split("_")
    except ValueError:
        # skip files that don't follow the dataset_position.log pattern
        continue

    flux, error = get_flux_from_log(f"{LOG_DIR}/{logfile}")
    data.append({
        "Dataset": dataset,
        "Position": position,
        "Flux (mJy)": flux,
        "Error (mJy)": error
    })

df = pd.DataFrame(data)
df.sort_values(by=['Dataset', 'Position'], inplace=True)
print(df.to_string(index=False))

# Plotting provided by ChatGPT, because plotting is hard.

if not df.empty:
    baseline_group = "cconfig"
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    # --- Left: Flux vs Position ---
    ax = axes[0]
    for dataset, group in df.groupby("Dataset"):
        ax.errorbar(group["Position"], group["Flux (mJy)"], yerr=group["Error (mJy)"],
                    fmt='o-', capsize=4, label=dataset)
    ax.set_xlabel("Position")
    ax.set_ylabel("Flux (mJy)")
    ax.set_title("Flux Comparison by Dataset and Position")
    ax.legend(title="Dataset")
    ax.tick_params(axis='x', rotation=45)

    # --- Right: Relative difference vs cconfig ---
    ax2 = axes[1]

    # Pivot to align positions across datasets
    pivot_flux = df.pivot_table(index="Position", columns="Dataset", values="Flux (mJy)", aggfunc="mean")
    pivot_err  = df.pivot_table(index="Position", columns="Dataset", values="Error (mJy)", aggfunc="mean")

    base = pivot_flux[baseline_group]
    base_err = pivot_err[baseline_group]

    for col in pivot_flux.columns:
        if col == baseline_group:
            continue
        grp = pivot_flux[col]
        grp_err = pivot_err[col]

        rel = (grp - base) / base * 100
        rel_err = 100 * np.sqrt((grp_err / grp)**2 + (base_err / base)**2) * (grp / base)

        ax2.errorbar(rel.index, rel.values, yerr=rel_err.values,
                    fmt='o-', capsize=4, label=col)

        ax2.axhline(0, linestyle="--", linewidth=1)
        ax2.set_xlabel("Position")
        ax2.set_ylabel("Relative to cconfig (%)")
        ax2.set_title('Relative Difference vs "cconfig"')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title="Dataset")
        plt.suptitle("Integrated Flux for point sources between datasets (5.5 arcsec diameter)")

        plt.tight_layout()
        plt.show()
        plt.savefig("flux_comparison.png", dpi=300)
else:
    print("No matching log files found.")
