import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Plotting constants
f_scale = 0.8
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale

# --- load (expects long-format) ---
csv_path = "final_flagging_summary.csv"
df = pd.read_csv(csv_path)
CLUSTER_ORDER = [
    "2A0335+096", "A2626", "A1795", "A478", "A1413", "A2204", 
    "RXJ1720+2638", "RXJ2129+0005", "MS1455+2232", "Z3146", 
    "RXCJ1115+0129", "ACTJ0022-0036",
]  # Redshift
CLUSTER_ORDER2 = [
    "ACTJ0022-0036", "RXJ2129+0005", "RXCJ1115+0129", "Z3146", "A2204", "2A0335+096",
    "A478", "A2626", "MS1455+2232", "A1413", "A1795", "RXJ1720+2638"
]  # Increasing declination

# Normalise frequency column to GHz
if "freq_GHz" not in df.columns:
    if "freq_Hz" in df.columns:
        df["freq_GHz"] = df["freq_Hz"] / 1e9
    else:
        raise ValueError("Need freq_Hz or freq_GHz column")

long = df

# ---- effective exposure per dataset-row ----
df["Teff_s"] = df["exposure_s"].astype(float)

# Aggregate Teff per cluster+config+epoch (identical vals, representing total), then sum over epoch.
teff = (
    df.groupby(["cluster", "config", "epoch"], as_index=False)["Teff_s"]
      .max()
      .groupby(["cluster", "config"], as_index=False)["Teff_s"]
      .sum()
)

def freq_to_x(freqs, fmin, fmax):
    i0 = np.searchsorted(freqs, fmin, side="left")
    i1 = np.searchsorted(freqs, fmax, side="right") - 1
    return i0 - 0.5, i1 + 0.5

def plot_heatmap_with_teff(config_label: str):
    sub = long[long["config"] == config_label].copy()
    if sub.empty:
        print(f"No data for config {config_label}")
        return

    # Exposure-weighted retained fraction per (cluster, freq) for given config. 
    epoch_level = (
        sub.groupby(["cluster", "freq_GHz", "epoch"], as_index=False)
        .agg(
            retained_frac=("retained_frac", "first"),   # or "first" if identical
            exposure_s=("exposure_s", "first")            # total exposure for that epoch
        )
    )
    agg = (
        epoch_level
        .groupby(["cluster", "freq_GHz"], as_index=False)
        .apply(lambda g: pd.Series({
            "retained_frac": np.average(
                g["retained_frac"],
                weights=g["exposure_s"]
            )
        }))
        .reset_index(drop=True)
    )


    mat = agg.pivot_table(index="cluster", columns="freq_GHz", values="retained_frac", aggfunc="mean")
    # Reindex to desired cluster order (drop missing, redshift order)
    clusters = [c for c in CLUSTER_ORDER if c in mat.index]
    mat = mat.reindex(clusters)
    Z = mat.to_numpy()

    freqs = mat.columns.to_numpy()
    Z = mat.to_numpy()

    # teff_sub = (
    #     teff[teff["config"] == config_label]
    #     .set_index("cluster")
    #     .reindex(clusters)
    # )
    # teff_vals = teff_sub["Teff_s"].to_numpy()

    # ---- plot: heatmap + side bar ----
    fig, (ax_hm) = plt.subplots(
        ncols=1,
        figsize=(7, 4),
        # gridspec_kw={"width_ratios": [8, 2]},
        # sharey=True,
        constrained_layout=True
    )

    im = ax_hm.imshow(
        Z,
        aspect="auto",
        interpolation="nearest",
        cmap="RdYlGn",   # low=red, high=green
        vmin=0.0,
        vmax=1.0,
    )

    # # RFI regions (GHz)
    # rfi_regions = [
    #     (9.3, 9.9),
    #     (10.7, 12.0),
    # ]

    # for fmin, fmax in rfi_regions:
    #     x0, x1 = freq_to_x(freqs, fmin, fmax)
    #     ax_hm.axvspan(
    #         x0, x1,
    #         color="k",
    #         alpha=0.1,
    #         zorder=3
    #     )
    #     ax_hm.text(
    #         (x0 + x1) / 2,
    #         -0.8,
    #         "Known RFI",
    #         ha="center",
    #         va="bottom",
    #         fontsize=9,
    #         color="k"
    #     )


    cb = fig.colorbar(im, ax=ax_hm, fraction=0.046, pad=0.02)
    cb.set_label("Retained fraction")

    ax_hm.set_yticks(np.arange(len(clusters)))
    ax_hm.set_yticklabels(clusters)

    step = max(1, len(freqs) // 12)
    xticks = np.arange(0, len(freqs), step)
    ax_hm.set_xticks(xticks)
    ax_hm.set_xticklabels([f"{freqs[k]:.2f}" for k in xticks], rotation=45, ha="right")
    ax_hm.set_xlabel("Frequency (GHz)")
    ax_hm.set_ylabel("Cluster")
    
    # # Side bars: effective exposure (hours)
    # teff_hours = teff_vals / 3600.0
    # y = np.arange(len(clusters))
    # ax_bar.barh(y, teff_hours)
    # ax_bar.set_xlabel(r"$T_{\mathrm{eff}}$ (hr)")
    # ax_bar.set_xticks(np.arange(0, 4, 1))
    # ax_bar.grid(True, axis="x", linestyle=":", linewidth=0.5)
    # ax_bar.set_ylim(ax_hm.get_ylim())

    plt.savefig(f"flagging_{config_label}.pdf", dpi=300)

plot_heatmap_with_teff("C")
plot_heatmap_with_teff("D")

# Give reduction in exposure time
initial_exposure_time = {
    "2A0335+096": {"C": 45.3, "D": 137.0},
    "A478": {"C": 44.5, "D": 249.0},
    "A2204": {"C": 64.0, "D": 73.2},
    "MS1455+2232": {"C": 61.1, "D": 71.8},
    "RXJ1720+2638": {"C": 62.2, "D": 71.2},
    "A1413": {"C": 36.9, "D": 258.4},
    "A1795": {"C": 71.5, "D": 71.5},
    "RXCJ1115+0129": {"C": 73.1, "D": 73.0},
    "Z3146": {"C": 73.1, "D": 73.0},
    "A2626": {"C": 83.0, "D": 74.7},
    "ACTJ0022-0036": {"C": 219.0, "D": 63.9},
    "RXJ2129+0005": {"C": 276.2, "D": 129.0},
}

lf = []
for _, row in teff.iterrows():
        cluster = row["cluster"]
        config = row["config"]
        teff_min = row["Teff_s"] / 60.0

        try:
            sched_min = initial_exposure_time[cluster][config]
        except KeyError:
            print(f"{cluster:15s} {config}: no scheduled time")
            continue

        lost_frac = max(0.0, 1.0 - teff_min / sched_min)
        lost_pct = 100.0 * lost_frac
        lf.append(lost_pct)
        print(
            f"{cluster:15s} {config} & {sched_min:6.1f} & {teff_min:6.1f} & {lost_pct:5.1f}"
        )

teff["Lost_pc"] = lf
print(teff[teff["config"] == "C"].describe())
print(teff[teff["config"] == "D"].describe())