from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


_MJD_RE = re.compile(r"(?:^|\.)(\d{5}\.\d+)(?:$|\.)")
_YEAR_RE = re.compile(r"^(?P<yy>\d{2})A-")


def _obsid_to_year_bin(obs_id: str) -> str:
    m = _YEAR_RE.match(str(obs_id))
    return m.group("yy") if m else "??"


def _obsid_to_mjd(obs_id: str) -> float:
    s = str(obs_id)
    last = None
    for m in _MJD_RE.finditer(s):
        last = m
    return float(last.group(1)) if last else float("nan")


def plot_cluster_epochs(
    points_df: pd.DataFrame,
    cluster: str,
    outdir: str | Path,
    *,
    freq_col: str = "Frequency [GHz]",
    fit_col: str = "Fitted Data",
    err_col: str = "Error",
    obs_col: str = "obs_id",
    cluster_col: str = "Source",
    fmin: float = 8.0,
    fmax: float = 12.0,
    dpi: int = 200,
    figsize: tuple[float, float] = (7.5, 4.5),
) -> Optional[Path]:
    """
    Plot all epochs for one cluster on a single figure.

    - One curve per epoch: Fitted Data vs Frequency with error bars
    - Legend labels: "YY (YYYY.MJD)" i.e. YearBin (epoch MJD)
      (Example: "24 (60350.810)")
    - Saves into a subfolder: <outdir>/cluster_epoch_plots/<cluster>.png

    Returns path to saved figure, or None if no rows for the cluster.
    """
    # Filter cluster + frequency range
    df = points_df.copy()
    for c in [freq_col, fit_col, err_col]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    sub = df[df[cluster_col].astype(str) == str(cluster)].copy()
    sub = sub.dropna(subset=[obs_col, freq_col, fit_col, err_col])
    sub = sub[(sub[freq_col] >= fmin) & (sub[freq_col] <= fmax)]
    sub = sub[(sub[fit_col] > 0) & (sub[err_col] > 0)]

    if sub.empty:
        return None

    # Add year + mjd for ordering/labels
    sub["yy"] = sub[obs_col].map(_obsid_to_year_bin)
    sub["mjd"] = sub[obs_col].map(_obsid_to_mjd)

    # Create output folder
    outdir = Path(outdir)
    plot_dir = outdir / "cluster_epoch_plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=figsize, constrained_layout=True)

    # Order epochs by MJD
    epochs = (
        sub[[obs_col, "yy", "mjd"]]
        .drop_duplicates()
        .sort_values("mjd")
        .reset_index(drop=True)
    )

    for _, erow in epochs.iterrows():
        obs_id = erow[obs_col]
        yy = erow["yy"]
        mjd = erow["mjd"]
        
        g = sub[sub[obs_col] == obs_id].sort_values(freq_col)
        label = f"{yy} ({mjd:.3f})"
        fmt = "o-" if yy == "25" else "o--"
        ax.errorbar(
            g[freq_col].to_numpy(),
            g[fit_col].to_numpy(),
            yerr=g[err_col].to_numpy(),
            fmt=fmt,
            capsize=2,
            linewidth=1,
            markersize=3,
            label=label,
        )

    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Fitted flux density (Jy)")
    ax.set_title(str(cluster))
    ax.legend(loc="best", frameon=False, fontsize=9)

    # Safe filename
    safe = (
        str(cluster)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("+", "p")
        .replace("-", "m")
    )
    outpath = plot_dir / f"{safe}.png"
    fig.savefig(outpath, dpi=dpi)
    plt.close(fig)

    return outpath

points_df = pd.read_csv("fluxboot_secondary_fits/secondary_per_spw_points.csv")

for cluster in sorted(points_df["Source"].dropna().unique()):
    plot_cluster_epochs(points_df, cluster, outdir=".")
