import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from casatools import table

# ==== USER SETTINGS ====
BASE_DIR = "subband"  # <- change this
SPW_PATTERN = "spw*"             # directories under BASE_DIR
MS_PATTERN = "*.ms"              # pattern for MS files within each spw dir
MAX_POINTS_PER_MS = 30000        # downsample for speed/plot clarity
# ========================


def get_config_label(path):
    """Return 'D' or 'C' based on filename."""
    name = os.path.basename(path).lower()
    if "dconfig" in name:
        return "D"
    if "cconfig" in name:
        return "C"
    return "?"


def read_uv(ms_path, max_points=None):
    """Read u,v (in metres) from an MS, ignoring fully flagged rows."""
    tb = table()
    tb.open(ms_path)

    uvw = tb.getcol("UVW")        # shape (3, nrow)
    u = uvw[0, :]
    v = uvw[1, :]

    # Use FLAG column to drop fully-flagged rows (all chans, all pols)
    try:
        flag = tb.getcol("FLAG")  # shape (nchan, npol, nrow)
        row_flagged = np.all(flag, axis=(0, 1))
        good = ~row_flagged
        u = u[good]
        v = v[good]
    except Exception:
        # If FLAG missing/unexpected, just use all rows
        pass

    tb.close()
    if max_points is not None and len(u) > max_points:
        step = int(np.ceil(len(u) / float(max_points)))
        u = u[::step]
        v = v[::step]

    return u, v


def main():
    # Find spw directories
    spw_dirs = [
        f"{BASE_DIR}/{d}" for d in ["spw0-7", "spw8-15", "spw16-23", "spw24-31"]
    ]
    if not spw_dirs:
        raise RuntimeError(f"No spw directories found under {BASE_DIR}")

    n_spw = len(spw_dirs)
    ncols = int(np.ceil(np.sqrt(n_spw)))
    nrows = int(np.ceil(n_spw / float(ncols)))

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(4 * ncols, 4 * nrows), squeeze=False
    )

    # One colour per subband
    cmap = plt.cm.get_cmap("tab10", n_spw)

    # For legend (same across panels)
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker='x', linestyle='', label='D config'),
        Line2D([0], [0], marker='o', linestyle='', label='C config'),
    ]

    for i, spw_dir in enumerate(spw_dirs):
        row = i // ncols
        col = i % ncols
        ax = axes[row, col]
        colour = cmap(i)

        spw_label = os.path.basename(spw_dir)

        ms_list = sorted(glob.glob(os.path.join(spw_dir, MS_PATTERN)))
        if not ms_list:
            ax.set_title(f"{spw_label} (no MS)")
            ax.axis("off")
            continue

        for ms_path in ms_list:
            cfg = get_config_label(ms_path)
            marker = 'x' if cfg == "D" else 'o'
            u, v = read_uv(ms_path, max_points=MAX_POINTS_PER_MS)

            if len(u) == 0:
                continue

            # Draw both +uv and -uv for full coverage
            for uu, vv in ((u, v), (-u, -v)):
                ax.scatter(
                    uu, vv,
                    marker=marker,
                    s=3,
                    facecolors=[colour],
                    linewidths=0.5,
                    alpha=0.8,
                )

        ax.set_title(spw_label)
        ax.set_xlabel("u (m)")
        ax.set_ylabel("v (m)")
        ax.set_aspect("equal", adjustable="box")

        # Make axes square around origin
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        r = max(abs(xlim[0]), abs(xlim[1]), abs(ylim[0]), abs(ylim[1]))
        ax.set_xlim(-r, r)
        ax.set_ylim(-r, r)

        if i == 0:
            ax.legend(handles=legend_handles, loc="upper right", fontsize=8)

    # Hide any unused panels
    for j in range(n_spw, nrows * ncols):
        row = j // ncols
        col = j % ncols
        axes[row, col].axis("off")

    fig.suptitle("UV coverage by subband (colour) and config (marker)", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{BASE_DIR}/uv_coverage.png", dpi=300)


main()

