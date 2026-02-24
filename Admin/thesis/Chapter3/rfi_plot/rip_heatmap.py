import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Load image

def rip_heatmap(img_name, tl, br, cells):
    img = Image.open(f"{img_name}.png").convert("RGB")
    arr = np.array(img)

    # ---- 1️⃣ Manually crop to heatmap area ----
    # Adjust these after visually inspecting the image
    # (use plt.imshow(arr) to find bounds)

    left, top  = tl
    right, bottom = br

    heat = arr[top:bottom, left:right]
    plt.imshow(arr)
    plt.show()

    # ---- 2️⃣ Convert colour → intensity ----
    # Using luminance as proxy (works well for single-hue maps)

    heat_float = heat.astype(float) / 255.0
    intensity = (
        0.2126 * heat_float[:, :, 0] +
        0.7152 * heat_float[:, :, 1] +
        0.0722 * heat_float[:, :, 2]
    )
    # invert y
    intensity = intensity[::-1, :]
    # ---- 3️⃣ Estimate grid size ----
    # From visual inspection this looks ~64 x 96 (adjust if needed)

    nx, ny = cells

    sx = intensity.shape[1] // nx
    sy = intensity.shape[0] // ny

    matrix = np.zeros((ny, nx))

    for j in range(ny):
        for i in range(nx):
            block = intensity[j*sy:(j+1)*sy, i*sx:(i+1)*sx]
            matrix[j, i] = block.mean()

    # ---- 4️⃣ Normalise 0–1 ----
    matrix = (matrix - matrix.min()) / (matrix.max() - matrix.min())

    np.save(f"{img_name}.npy", matrix)
    plt.imshow(matrix, origin="lower", cmap="viridis")
    plt.colorbar(label="Relative value")
    plt.show()


# rip_heatmap("cont_broad", (60, 31), (355, 406), (54, 86))  # Ground
# rip_heatmap("intermittent_broad", (72, 32), (406, 407), (60, 86))  # Ground
# rip_heatmap("cont_narrow", (74, 65), (385, 441), (60, 86))  # low spw
# rip_heatmap("intermittent_narrow", (62, 32), (406, 407), (64, 86))  # radar
