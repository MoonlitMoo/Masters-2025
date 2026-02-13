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

images = ["minihalo", "minihalo_uvconstr"]
masks = []

# Get all the different masks
shape, coords = None, None
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

# Create the G14 mask
ia.open(f"{images[0]}.image.tt0")
shape, coords = ia.shape(), ia.coordsys().torecord()
ia.close()
centre_region = "ellipse[[17:20:09.4, +026.37.30], [30.0arcsec, 34.8arcsec], 127deg]"
tail_region = "poly[[17:20:10.50000, +026.38.02.0000], [17:20:11.40000, +026.38.07.5000], " + \
    "[17:20:14.20000, +026.37.34.0000], [17:20:14.20000, +026.37.00.0000], " + \
    "[17:20:13.00000, +026.36.33.0000], [17:20:11.20000, +026.36.23.0000], " + \
    "[17:20:09.70000, +026.36.30.0000], [17:20:09.30000, +026.36.35.0000], " + \
    "[17:20:09.70000, +026.36.56.0000]]"
centre_region = rg.fromtext(centre_region, shape=shape, csys=coords)
tail_region = rg.fromtext(tail_region, shape=shape, csys=coords)
tail_region = rg.difference(tail_region, centre_region)  # Remove centre
full_region = rg.makeunion(regions={"c": centre_region, "t": tail_region})

sel_region = centre_region
os.system(f"cp -r {images[0]}.mask g14_mask.mask")
ia.open("g14_mask.mask")
ia.set(0.0, region=rg.complement(sel_region))
ia.set(1.0, region=sel_region)
g14_mask = np.squeeze(np.array(ia.getchunk(), dtype=bool))
ia.close()

# Select the one true mask to rule them all
base_mask = g14_mask

print(f"Using G14 mask")

# Get the now comparable fluxes.
flux = []
error = []
sigma = []
for im in images:
    out_img = f'{OUTPUT_DIR}/{im.split(".image.")[0]}_masked'
    agn_reg = "circle[[17h20m10.03s, 26d37m31.9s], 3arcsec]"
    f, e, s = get_minihalo_flux_density(f"{im}", out_img, mask=base_mask, agn_err=1.56e-5, agn_region=agn_reg, verbose=True)
    flux.append(f)
    error.append(e)
    sigma.append(s)

# Plotting via ChatGPT
rows = []
for i, (fname, flux_jy, error_jy, rms) in enumerate(zip(images, flux, error, sigma)):
    r = 1 + i*0.5
    rows.append({"file": fname, "robust": r, "ssb": -0.5,
                 "flux_jy": float(flux_jy), "error_jy": float(error_jy), "rms_jyb": float(rms)})

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
err_grid = pivot_metric("error_jy")
rms_grid  = pivot_metric("rms_jyb")
score_grid = flux_grid / rms_grid  # heuristic only; label clearly as unitless

# ---------- PLOTTING ----------
def annotate_cells(ax, grid, fmt="{:.3g}"):
    for (i, j), val in np.ndenumerate(grid.values):
        ax.text(j, i, fmt.format(val), ha="center", va="center", fontsize=10)

def heatmap(ax, grid, title, cbar_label, fmt="{:.3g}", err=None, err_fmt="{:.2g}", split_lines=False):
    """
    Plot a heatmap of `grid` and annotate each cell with its value (and ±error if provided).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    grid : pandas.DataFrame
        2D table of values (rows = 'Small-scale bias', cols = 'Robust').
    title : str
    cbar_label : str
    fmt : str
        Format string for values, e.g. "{:.3g}".
    err : pandas.DataFrame or None
        Optional errors with identical shape and index/columns to `grid`.
    err_fmt : str
        Format string for errors, e.g. "{:.2g}".
    split_lines : bool
        If True, write value and error on separate lines.
    """
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

    # --- Annotations (value ± error) ---
    if err is not None:
        # Basic shape/index/column check
        if not (list(err.index) == list(grid.index) and list(err.columns) == list(grid.columns)):
            raise ValueError("`err` must have the same index/columns as `grid`.")

    def _is_dark(rgba):
        r, g, b, _ = rgba
        # Perceptual luminance
        return (0.2126*r + 0.7152*g + 0.0722*b) < 0.45

    vals = grid.values
    errs = err.values if err is not None else None
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            v = vals[i, j]
            if np.isnan(v):
                continue
            text = fmt.format(v)
            if errs is not None:
                e = errs[i, j]
                if np.isfinite(e):
                    text = (text + ("\n±" if split_lines else " ± ") + err_fmt.format(e))
            # Choose contrasting text colour based on cell colour
            rgba = im.cmap(im.norm(v))
            color = "white" if _is_dark(rgba) else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=9, color=color)


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


    if trim_fn is not None:
        m = np.array(trim_fn(g14_mask), dtype=bool)
    else:
        m = g14_mask
    # Add G14 mask
    ax.imshow(
        m,
        cmap=ListedColormap([(0, 0, 0, 0), (1.0, 0.75, 0.8, alpha)]),
        interpolation="nearest",
        origin="upper",
    )

    # Outline at the mask boundary. For some reason this needs flipping in the y axis.
    ax.contour(
        np.flip(m.astype(float), 0),
        levels=[0.5],
        colors=["pink"],
        linestyles="solid",
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
    g14_label = Line2D([0], [0], marker="s", linestyle="none",
               markerfacecolor="pink", markeredgecolor="none", markersize=10,
               label=f"G14 mask")
    robust_handles.append(g14_label)

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


fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
heatmap(axes[0], flux_grid*1e3, "Integrated Flux", "mJy", fmt="{:1.2f}", err=err_grid*1e3)
heatmap(axes[1], rms_grid*1e6, "Image RMS", "uJy/beam", fmt="{:1.2f}")
plt.savefig("flux_comparison.png", dpi=300)

trim_border = 900
plot_masks_by_df(masks, df, trim_fn=lambda x: np.flip(x.T, 0)[trim_border:-trim_border, trim_border:-trim_border])
plt.savefig("mask_comparison.png", dpi=300)
