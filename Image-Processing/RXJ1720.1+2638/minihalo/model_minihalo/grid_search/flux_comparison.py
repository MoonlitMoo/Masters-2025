import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = "flux_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

images = sorted([f for f in os.listdir() if ".image.tt0" in f])
flux = []
sigma = []

for im in images:
    out_img = f'{OUTPUT_DIR}/{im.split(".image.")[0]}_masked.image.tt0'
    f, s = get_minihalo_flux_density(im, out_img)
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

fig, axes = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)

heatmap(axes[0], flux_grid,  "Integrated Flux",        "Jy",        fmt="{:.3g}")
heatmap(axes[1], rms_grid,   "Image RMS",              "Jy/beam",   fmt="{:.2e}")

plt.tight_layout()
plt.show()
plt.savefig("flux_comparison.png", dpi=300)
