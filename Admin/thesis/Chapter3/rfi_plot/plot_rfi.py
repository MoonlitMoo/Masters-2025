import numpy as np
import matplotlib.pyplot as plt

# ---- set your file paths (assumes each is a normalised 0–1 ndarray saved as .npy) ----
paths = {
    ("narrow", "continuous"):    "cont_narrow.npy",
    ("narrow", "intermittent"):  "intermittent_narrow.npy",
    ("broad",  "continuous"):    "cont_broad.npy",
    ("broad",  "intermittent"):  "intermittent_broad.npy",
}

# ---- load ----
A_nc = np.load(paths[("narrow","continuous")])
A_ni = np.load(paths[("narrow","intermittent")])
A_bc = np.load(paths[("broad","continuous")])
A_bi = np.load(paths[("broad","intermittent")])

f_scale=1
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale

fig, ax = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)

data_grid = [
    [A_nc, A_ni],
    [A_bc, A_bi],
]

col_titles = ["Continuous", "Intermittent"]
row_titles = ["Narrowband", "Broadband"]

vmin, vmax = 0.0, 1.0

im = None
for r in range(2):
    for c in range(2):
        im = ax[r, c].imshow(
            data_grid[r][c],
            origin="lower",
            vmin=vmin,
            vmax=vmax,
            aspect="auto"
        )

        if r == 0:
            ax[r, c].set_title(col_titles[c])

        if c == 0:
            ax[r, c].set_ylabel(f"{row_titles[r]}")

fig.supylabel("Time (s)", fontsize=16)
fig.supxlabel("Frequency Channel (arbitrary units)", fontsize=16)
# Single colourbar aligned to grid
cbar = fig.colorbar(im, ax=ax.ravel().tolist(), pad=0.02)
cbar.set_label("Normalised visibility amplitude")

plt.savefig("rfi_example.pdf", dpi=300, bbox_inches='tight')