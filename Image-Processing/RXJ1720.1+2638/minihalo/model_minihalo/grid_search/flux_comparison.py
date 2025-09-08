import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, to_rgba
from matplotlib.cm import get_cmap
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

OUTPUT_DIR = "flux_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

images = sorted([f.split(".image.tt0")[0] for f in os.listdir() if ".image.tt0" in f])
masks = []

# Get all the different masks
for im in images:
    image_file = f"{im}.image.tt0"
    residual_file = f"{im}.residual.tt0"

    # Load the image
    ia.open(image_file)
    pix = ia.getchunk()
    ia.close()

    # Get sigma and flux
    res = imstat(residual_file)
    sigma = res["sigma"][0]

    # Get minihalo flux
    _, mask, _ = contour_sum(pix, 3 * sigma, pick='largest')
    masks.append(mask)

# Select the one true mask to rule them all
sel_index = 6
base_mask = masks[sel_index]
print(f"Using mask from image {images[sel_index]}")

# Get the now comparable fluxes.
flux = []
sigma = []
for im in images:
    out_img = f'{OUTPUT_DIR}/{im.split(".image.")[0]}_masked'
    f, s = get_minihalo_flux_density(im, out_img, mask=base_mask)
    flux.append(f)
    sigma.append(s)

# Plotting via ChatGPT
pat = re.compile(r"r=([\-0-9.]+)_ssb=([\-0-9.]+)")
rows = []
for fname, flux_jy, rms in zip(images, flux, sigma):
    m = pat.search(fname)
    if not m:
        raise ValueError(f"Could not parse r/ssb from: {fname}")
    r = float(m.group(1).rstrip("."))
    ssb = float(m.group(2).rstrip("."))
    rows.append({"file": fname, "robust": r, "ssb": ssb,
                 "flux_jy": float(flux_jy), "rms_jyb": float(rms)})

df = pd.DataFrame(rows)

# Ensure we have the 3×3 grid (sorted for nice axes)
robust_vals = sorted(df["robust"].unique())
ssb_vals = sorted(df["ssb"].unique())

def pivot_metric(metric_col):
    p = df.pivot(index="ssb", columns="robust", values=metric_col)
    # Reindex to guarantee consistent order on axes
    p = p.reindex(index=ssb_vals, columns=robust_vals)
    return p

flux_grid = pivot_metric("flux_jy")
rms_grid  = pivot_metric("rms_jyb")
score_grid = flux_grid / rms_grid  # heuristic only; label clearly as unitless

# ---------- PLOTTING ----------
def annotate_cells(ax, grid, fmt="{:.3g}"):
    for (i, j), val in np.ndenumerate(grid.values):
        ax.text(j, i, fmt.format(val), ha="center", va="center", fontsize=10)

def heatmap(ax, grid, title, cbar_label, fmt="{:.3g}"):
    im = ax.imshow(grid.values, origin="upper", aspect="equal")
    cbar = plt.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label(cbar_label)
    ax.set_title(title)
    ax.set_xlabel("Robust")
    ax.set_ylabel("Small-scale bias")
    ax.set_xticks(range(len(grid.columns)))
    ax.set_xticklabels([f"{c:g}" for c in grid.columns])
    ax.set_yticks(range(len(grid.index)))
    ax.set_yticklabels([f"{r:g}" for r in grid.index])
    annotate_cells(ax, grid, fmt=fmt)


def plot_masks_by_df(masks, df, cmap_name="viridis", alpha=0.35, trim_fn=None):
    """
    Overlay 2D masks with colour by 'robust' and outline style by 'ssb'.

    Parameters
    ----------
    masks : list[np.ndarray]
        List of 2D boolean/0-1 arrays.
    df : pandas.DataFrame
        Must contain columns 'robust' and 'ssb'; each row corresponds to masks[i].
    cmap_name : str
        Matplotlib colormap for mapping robust values to colours.
    alpha : float
        Transparency for mask fill.
    trim_fn : callable or None
        Optional function(mask) -> mask to preprocess (e.g., transpose/flip/trim).
    """
    assert len(masks) == len(df), "masks and df must be the same length"

    # Prepare colour map from robust
    robust_vals = df["robust"].to_numpy()
    rmin, rmax = np.min(robust_vals), np.max(robust_vals)
    # Avoid divide-by-zero if all robust are identical
    norm = Normalize(vmin=rmin, vmax=rmax if rmax > rmin else rmin + 1e-9)
    cmap = get_cmap(cmap_name)

    # Map unique SSB values to line styles
    ssb_unique = list(dict.fromkeys(df["ssb"].tolist()))  # preserve order
    style_cycle = ["solid", "dashed", "dashdot", "dotted", (0, (5, 1, 1, 1)), (0, (1, 1))]
    ssb_to_style = {v: style_cycle[i % len(style_cycle)] for i, v in enumerate(ssb_unique)}

    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot each mask
    for i, mask in enumerate(masks):
        m = np.array(mask, dtype=bool)
        if trim_fn is not None:
            m = np.array(trim_fn(m), dtype=bool)
        if m.size == 0:
            continue

        colour = cmap(norm(robust_vals[i]))
        # Filled overlay (transparent where False)
        ax.imshow(
            m,
            cmap=ListedColormap([(0, 0, 0, 0), to_rgba(colour, alpha)]),
            interpolation="nearest",
            origin="upper",
        )

        # Outline at the mask boundary. For some reason this needs flipping in the y axis.
        ax.contour(
            np.flip(m.astype(float), 0),
            levels=[0.5],
            colors=[to_rgba(colour, 1.0)],
            linestyles=ssb_to_style[df.at[i, "ssb"]],
            linewidths=1.6,
            origin="upper",
        )

    ax.set_aspect("equal")
    ax.axis("off")

    # Legends: one for robust colours, one for SSB line styles
    # Robust legend (dedupe in order)
    robust_unique = []
    for v in robust_vals:
        if v not in robust_unique:
            robust_unique.append(v)
    robust_handles = [
        Line2D([0], [0], marker="s", linestyle="none",
               markerfacecolor=to_rgba(cmap(norm(v)), 0.9), markeredgecolor="none", markersize=10,
               label=f"robust={v}")
        for v in robust_unique
    ]

    # SSB legend (styles)
    ssb_handles = [
        Line2D([0], [0], color="black", linestyle=ssb_to_style[s], linewidth=2, label=f"ssb={s}")
        for s in ssb_unique
    ]

    # Place the two legends without overlapping
    leg1 = ax.legend(handles=robust_handles, title="Colour: robust", loc="upper left", bbox_to_anchor=(1.02, 1.0))
    ax.add_artist(leg1)
    ax.legend(handles=ssb_handles, title="Outline: ssb", loc="upper left", bbox_to_anchor=(1.02, 0.45))

    plt.tight_layout()


fig, axes = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)
heatmap(axes[0], flux_grid*1e3, "Integrated Flux", "mJy", fmt="{:1.2f}")
heatmap(axes[1], rms_grid*1e6, "Image RMS", "uJy/beam", fmt="{:1.2f}")
plt.savefig("flux_comparison.png", dpi=300)

trim_border = 900
plot_masks_by_df(masks, df, trim_fn=lambda x: np.flip(x.T, 0)[trim_border:-trim_border, trim_border:-trim_border])
plt.savefig("mask_comparison.png", dpi=300)
plt.show()
