import os
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, SkyOffsetFrame

import astropy.units as u
from astropy.visualization import MinMaxInterval, AsinhStretch, ImageNormalize
import matplotlib.pyplot as plt

f_scale = 1.0
plt.rcParams["axes.labelsize"] = 14 * f_scale
plt.rcParams["axes.titlesize"] = 16 * f_scale
plt.rcParams["xtick.labelsize"] = 12 * f_scale
plt.rcParams["ytick.labelsize"] = 12 * f_scale
plt.rcParams["legend.fontsize"] = 12 * f_scale


def plot_fits_on_ax(
    fits_path,
    ax,
    *,
    norm=None,
    colour_scale="asinh",
    alpha=0.1,
    cmap="inferno",
    zoom=1,
    tick_spacing=60 * u.arcsec,
    show_xlabel=True,
    show_ylabel=True,
):
    """
    Plot a FITS image on an existing WCSAxes `ax`.

    - Returns (im, wcs, norm_used)
    - Does NOT create a colourbar (so callers can add one shared colourbar).
    """
    hdu = fits.open(fits_path)[0]
    data = np.squeeze(hdu.data).astype(float)
    hdr = hdu.header
    wcs = WCS(hdr)

    # Crop/zoom in pixel space
    ny, nx = data.shape
    cx, cy = nx / 2, ny / 2
    width = nx / zoom
    height = ny / zoom
    x_min, x_max = int(round(cx - width / 2)), int(round(cx + width / 2))
    y_min, y_max = int(round(cy - height / 2)), int(round(cy + height / 2))

    # Normalisation
    if norm is None:
        if isinstance(colour_scale, str):
            # Asinh-stretched min-max scaling (consistent with your current script)
            norm_used = ImageNormalize(
                data, interval=MinMaxInterval(), stretch=AsinhStretch(a=alpha)
            )
        else:
            norm_used = colour_scale
    else:
        norm_used = norm

    im = ax.imshow(
        data,
        origin="lower",
        cmap=cmap,
        norm=norm_used,
        interpolation="none",
    )

    # SkyOffset overlay (ΔRA/ΔDec)
    ref = SkyCoord(wcs.wcs.crval[0] * u.deg, wcs.wcs.crval[1] * u.deg, frame="icrs")
    off_frame = SkyOffsetFrame(origin=ref)
    ov = ax.get_coords_overlay(off_frame)

    ov[0].set_ticks(spacing=tick_spacing, size=5)
    ov[1].set_ticks(spacing=tick_spacing, size=5)
    ov[0].set_minor_frequency(4)
    ov[1].set_minor_frequency(4)
    ov[0].display_minor_ticks(True)
    ov[1].display_minor_ticks(True)

    ov[0].set_ticks_position("b")
    ov[0].set_ticklabel_position("b")
    ov[0].set_axislabel_position("b")

    ov[1].set_ticks_position("l")
    ov[1].set_ticklabel_position("l")
    ov[1].set_axislabel_position("l")

    ov[0].tick_params(color="white", which="both", direction="in")
    ov[1].tick_params(color="white", which="both", direction="in")

    ov[0].set_format_unit(u.arcsec)
    ov[1].set_format_unit(u.arcsec)

    if show_xlabel:
        ov[0].set_axislabel("ΔRA (arcsec)")
    else:
        ov[0].set_axislabel("")
        ov[0].set_ticklabel_visible(False)

    if show_ylabel:
        ov[1].set_axislabel("ΔDec (arcsec)")
    else:
        ov[1].set_axislabel("")
        ov[1].set_ticklabel_visible(False)

    # Hide absolute RA/Dec coordinate helpers
    ax.coords[0].set_ticklabel_visible(False)
    ax.coords[1].set_ticklabel_visible(False)
    ax.coords[0].set_ticks_visible(False)
    ax.coords[1].set_ticks_visible(False)
    ax.coords[0].set_axislabel("")
    ax.coords[1].set_axislabel("")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Convention: ΔRA increases to the left
    ax.invert_xaxis()

    return im, wcs, norm_used


def export_fits(image, out):
    c_str = f"exportfits(imagename='{image}', fitsimage='{out}', dropdeg=True, overwrite=True)"
    os.system(f"casa --nologger --nogui -c \"{c_str}\"")
    os.system("rm casa*.log")


BASE_DIR = "/media/benja/T7/psf_test"
colour_scale = "asinh"

# Only plot robust = -1 and +1
robust = [-1, 1]
labels = [f"test_r{r}" for r in robust]
fits_files = [f"FITS/{lab}.fits" for lab in labels]

# If you want to auto-export the FITS files, uncomment:
# for lab in labels:
#     psf_img = f"{BASE_DIR}/{lab}.psf.tt0"
#     export_fits(psf_img, f"FITS/{lab}.fits")

# Create 1x2 WCSAxes subplots with shared pixel axes
# Use the first FITS WCS for projection in both panels (PSFs should share WCS)
wcs0 = WCS(fits.getheader(fits_files[0]))
fig, axs = plt.subplots(
    1,
    2,
    figsize=(8, 4),
    subplot_kw={"projection": wcs0},
    sharex=True,
    sharey=True,
)

# Left: robust -1 (create norm from this panel)
im0, _, norm = plot_fits_on_ax(
    fits_files[0],
    axs[0],
    colour_scale=colour_scale,
    alpha=0.1,
    zoom=5,
    show_xlabel=True,
    show_ylabel=True,
)
axs[0].set_title("Robust = -1")

# Right: robust +1 (reuse same norm; hide duplicate y tick labels)
im1, _, _ = plot_fits_on_ax(
    fits_files[1],
    axs[1],
    norm=norm,
    zoom=5,
    show_xlabel=True,
    show_ylabel=False,
)
axs[1].set_title("Robust = +1")

# Single shared colourbar
fig.canvas.draw()
pos_r = axs[1].get_position()
cax = fig.add_axes([pos_r.x1 + 0.015, pos_r.y0, 0.02, pos_r.height])
cbar = fig.colorbar(im0, cax=cax)
cbar.set_label("Normalised response", rotation=90, labelpad=10)

plt.savefig("psf_r-1_r+1.pdf", dpi=300, bbox_inches="tight")
plt.close(fig)