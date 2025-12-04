import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from casatools import table

# ==== USER SETTINGS ====
BASE_DIR = "subband"  # <- change this
SPW_PATTERN = "spw*"             # directories under BASE_DIR
MS_PATTERN = "*.ms"              # pattern for MS files within each spw dir
N_BINS = 40                      # baseline-length histogram bins
# ========================


def read_baseline_lengths(ms_path):
    """
    Return baseline lengths (sqrt(u^2+v^2) in metres) for all non-flagged rows.
    """
    tb = table()
    tb.open(ms_path)

    uvw = tb.getcol("UVW")  # shape (3, nrow)
    u = uvw[0, :]
    v = uvw[1, :]

    # Select rows that are not fully flagged (all chans, all pols)
    try:
        flag = tb.getcol("FLAG")  # (nchan, npol, nrow)
        row_flagged = np.all(flag, axis=(0, 1))
        good = ~row_flagged
        u = u[good]
        v = v[good]
    except Exception:
        # If FLAG missing/unexpected, just use all rows
        pass

    tb.close()

    # baseline length in metres
    bl = np.sqrt(u * u + v * v)
    return bl


def main():
    # Find spw directories
    spw_dirs = [
        f"{BASE_DIR}/{d}" for d in ["spw0-7", "spw8-15", "spw16-23", "spw24-31"]
    ]
    if not spw_dirs:
        raise RuntimeError(f"No spw directories found under {BASE_DIR}")

    # Collect baseline lengths for each sub-band first,
    # so we can set a common bin range.
    bl_per_spw = []   # list of 1D arrays
    labels = []       # matching labels
    total_points = [] # total non-flagged uv points per spw

    for spw_dir in spw_dirs:
        spw_label = os.path.basename(spw_dir)
        ms_list = sorted(glob.glob(os.path.join(spw_dir, MS_PATTERN)))
        if not ms_list:
            print(f"{spw_label}: no MS files found")
            bl_per_spw.append(np.array([]))
            labels.append(spw_label)
            total_points.append(0)
            continue

        all_bl = []
        for ms_path in ms_list:
            bl = read_baseline_lengths(ms_path)
            if bl.size > 0:
                all_bl.append(bl)

        if all_bl:
            all_bl = np.concatenate(all_bl)
        else:
            all_bl = np.array([])

        bl_per_spw.append(all_bl)
        labels.append(spw_label)
        total_points.append(int(all_bl.size))
        print(f"{spw_label}: {all_bl.size} non-flagged u,v points")

    # Determine global bin edges (shared across all panels)
    max_bl = max((arr.max() for arr in bl_per_spw if arr.size > 0), default=0.0)
    if max_bl <= 0:
        raise RuntimeError("No non-flagged points found in any MS.")

    bin_edges = np.linspace(0.0, max_bl, N_BINS + 1)

    # Set up subplot grid
    n_spw = len(spw_dirs)
    ncols = int(np.ceil(np.sqrt(n_spw)))
    nrows = int(np.ceil(n_spw / float(ncols)))

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(4 * ncols, 3.5 * nrows), squeeze=False, sharey=True, sharex=True
    )

    cmap = plt.cm.get_cmap("tab10", n_spw)

    for i, (bl, label, npts) in enumerate(zip(bl_per_spw, labels, total_points)):
        row = i // ncols
        col = i % ncols
        ax = axes[row, col]

        if bl.size == 0:
            ax.set_title(f"{label} (no data)")
            ax.axis("off")
            continue

        ax.hist(
            bl,
            bins=bin_edges,
            histtype="step",
            color=cmap(i),
            linewidth=1.2,
        )

        ax.set_title(f"{label}  (N={npts})")
        ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.7)

    # Hide any unused panels
    for j in range(n_spw, nrows * ncols):
        row = j // ncols
        col = j % ncols
        axes[row, col].axis("off")

    fig.suptitle("Histogram of non-flagged baseline lengths by sub-band", fontsize=14)
    fig.supxlabel("Baseline length |uv| (m)")
    fig.supylabel("Count")

    plt.tight_layout()
    plt.savefig(f"{BASE_DIR}/baseline_histogram.png", dpi=300)

main()

