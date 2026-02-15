import pandas as pd

images = ["images/image_spw0-7", "images/image_spw8-15", "images/image_spw16-23", "images/image_spw24-31"]
labels = ["Minihalo AGN"]
regions = ["circle[[4h13m25.29s, 10d27m54.6s], 5arcsec]"]
log_dir = "fit_logs"

def _read_log_value(l: str):
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


def _get_flux_from_log(log):
    with open(log, "r") as f:
        for l in f.readlines():
            if "Integrated:" in l:
                return _read_log_value(l)
    return np.nan, np.nan


def dump_flux_summary(
    df: pd.DataFrame,
    out_path: str = "flux_summary.txt",
):
    """
    Writes the full DataFrame and the per-position flux summary
    (weighted mean + conservative uncertainty) to a single text file.
    """

    # ---- build summary ----
    rows = []

    for pos, g in df.groupby("Position"):
        s = g["Flux (mJy)"].to_numpy(dtype=float)
        e = g["Error (mJy)"].to_numpy(dtype=float)
        n = s.size

        w = 1.0 / e**2
        mean = np.sum(w * s) / np.sum(w)
        sig_mean = np.sqrt(1.0 / np.sum(w))

        if n > 1:
            scatter = np.sqrt(np.sum((s - mean) ** 2) / (n - 1))
            sig_scat = scatter / np.sqrt(n)
        else:
            scatter = np.nan
            sig_scat = np.nan

        sig_final = np.nanmax([sig_mean, sig_scat])

        rows.append({
            "Position": pos,
            "N": n,
            "S_mean_mJy": mean,
            "sigma_final_mJy": sig_final,
            "sigma_formal_mJy": sig_mean,
            "rms_scatter_mJy": scatter,
        })

    summary = pd.DataFrame(rows).sort_values("Position")

    # ---- write to text file ----
    with open(out_path, "w") as f:

        # Header
        f.write("# Input flux measurements\n")
        f.write("# -----------------------\n")

        f.write(df.to_string(index=False))
        f.write("\n\n")
	# Full df
        f.write("# Calculated statistics \n")
        f.write("# -----------------------\n")
        f.write(summary.to_string(index=False))
        f.write("\n\n")
        # Summary
        f.write("# Per-source flux summary\n")
        f.write("# Weighted mean with conservative uncertainty\n")
        f.write("# --------------------------------------------\n")

        for r in summary.itertuples(index=False):
            f.write(
                f"{r.Position:>10s} : "
                f"{r.S_mean_mJy:.4f} ± {r.sigma_final_mJy:.4f} mJy "
                f"(N={r.N})\n"
            )

    return summary

# Fit the fluxes
log_files = []
for image in images:
    image_name = f"{image}.image.tt0"
    image_logs = []
    for region, label in zip(regions, labels):
        log_name = f"{log_dir}/{os.path.basename(image)}_{label}.log"
        image_logs.append(log_name)
        imfit(image_name, region=region, logfile=log_name, append=False)
    log_files.append(image_logs)

# Grab the log data
data = []
for d, all_l in zip(images, log_files):
    for p, l in zip(labels, all_l):
        flux, error = _get_flux_from_log(l)
        data.append({
            "Dataset": d,
            "Position": p,
            "Flux (mJy)": flux,
            "Error (mJy)": error
        })

df = pd.DataFrame(data)
df.sort_values(by=['Dataset', 'Position'], inplace=True)
print(df.to_string(index=False))

dump_flux_summary(df)

# Plotting provided by ChatGPT, because plotting is hard.

if not df.empty:
    baseline_group = images[0]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    # --- Left: Flux vs Position ---
    ax = axes[0]
    for dataset, group in df.groupby("Dataset"):
        ax.errorbar(group["Position"], group["Flux (mJy)"], yerr=group["Error (mJy)"],
                    fmt='o-', capsize=4, label=dataset)
    ax.set_xlabel("Position")
    ax.set_ylabel("Integrated Flux (mJy)")
    ax.set_title("Flux Comparison by Dataset and Source")
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
        plt.suptitle("Point source flux variability by observation")

        plt.tight_layout()
        plt.show()
        plt.savefig("flux_comparison.png", dpi=300)
else:
    print("No matching log files found.")
