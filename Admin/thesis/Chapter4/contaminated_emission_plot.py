import os
import math
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
from matplotlib.colors import FuncNorm


f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 12 * f_scale

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from matplotlib.ticker import AutoMinorLocator
from matplotlib.patches import Ellipse

def plot_restoring_beam(ax, hdr, beam_loc, beam_detail):
        bmaj_as = hdr["BMAJ"] * 3600.0  # deg -> arcsec
        bmin_as = hdr["BMIN"] * 3600.0
        bpa_deg = hdr["BPA"]
        print(f"Beam size: {bmaj_as:.2f}x{bmin_as:.2f} arcsec, {bpa_deg:.1f}")
        pixscale_as = abs(hdr["CDELT1"]) * 3600.0  # arcsec/pixel
        sign = np.sign(hdr["CDELT1"])
        angle = -sign * bpa_deg

        # Beam size in pixels
        bmaj_pix = bmaj_as / pixscale_as
        bmin_pix = bmin_as / pixscale_as

        # Place beam at a fractional location, of the visible pixel range
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()

        x_pix = x0 + beam_loc[0] * (x1 - x0)
        y_pix = y0 + beam_loc[1] * (y1 - y0)
        
        if beam_detail == "high":
            edge_colour = "0.3"
        else:
            edge_colour = "0.7"

        beam = Ellipse(
            (x_pix, y_pix),
            width=bmin_pix,
            height=bmaj_pix,
            angle=angle,
            transform=ax.get_transform("pixel"),
            edgecolor=edge_colour,
            facecolor="0.7",
            linewidth=1.2,
            zorder=10,
        )
        
        if beam_detail == "high":
            # --- Major / minor axis lines ---
            bpa = np.deg2rad(bpa_deg)
            ux = np.sin(bpa) * sign          # major-axis unit vector x
            uy = np.cos(bpa)                   # major-axis unit vector y

            # Major axis (along PA)
            dx_maj = 0.5 * bmaj_pix * ux
            dy_maj = 0.5 * bmaj_pix * uy
            dx_min = 0.5 * bmin_pix * uy
            dy_min = -0.5 * bmin_pix * ux
            
            ax.plot(
                [x_pix - dx_maj, x_pix + dx_maj],
                [y_pix - dy_maj, y_pix + dy_maj],
                transform=ax.get_transform("pixel"),
                color="0.3",
                linewidth=1.0,
                zorder=11,
            )

            ax.plot(
                [x_pix - dx_min, x_pix + dx_min],
                [y_pix - dy_min, y_pix + dy_min],
                transform=ax.get_transform("pixel"),
                color="0.2",
                linewidth=1.0,
                zorder=11,
            )
        ax.add_patch(beam)

def add_arrow_label_pixel(
    ax,
    x_pix,
    y_pix,
    text,
    text_offset_pix=(30, 30),
    ha="left",
    va="bottom",
    arrow_color="white",
    text_color="white",
    fontsize=12,
    arrow_lw=1.2,
    arrow_ms=10,
    zorder=50,
):
    dx, dy = text_offset_pix
    xt, yt = x_pix + dx, y_pix + dy

    ann = ax.annotate(
        text,
        xy=(x_pix, y_pix),
        xycoords=ax.get_transform("pixel"),
        xytext=(xt, yt),
        textcoords=ax.get_transform("pixel"),
        ha=ha,
        va=va,
        color=text_color,
        fontsize=fontsize,
        arrowprops=dict(
            arrowstyle="-|>",
            color=arrow_color,
            lw=arrow_lw,
            mutation_scale=arrow_ms,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=zorder,
    )
    return ann


def plot_fits(
    fits_path,
    vmin=None,
    vmax=None,
    scale="linear",
    alpha=None,
    cmap="inferno",
    zoom = 1,
    beam_detail="high",  # Should beam image include major/minor axis
    figsize=(6.5, 6.5),
    beam_loc=(0.1, 0.1),  # In fraction of axis
    cbar_label=r"mJy beam$^{-1}$",
):
    hdu = fits.open(fits_path)[0]
    data = np.squeeze(hdu.data).astype(float)
    hdr = hdu.header
    wcs = WCS(hdr)

    # Scale Jy/beam -> mJy/beam for display. Clip to max and min values.
    data *= 1e3
    data = np.clip(data, vmin, vmax)
    
    if scale == "linear":
        norm = FuncNorm(
            (lambda x: x, lambda y: y),
            vmin=vmin, vmax=vmax
        )
        cticks = np.linspace(0, round(vmax), 5)
    elif scale == "log":
        # Log scale colouring, mimic CARTA colouring
        norm = FuncNorm(
            (lambda x: np.log10(alpha*x + 1),
            lambda y: (10**y - 1) / alpha),
            vmin=vmin, vmax=vmax,
        )
        cticks = [0, 0.01, 0.05, 0.1, 0.5, 1]
    else:
        raise ValueError("Unknown scale")


    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=wcs)

    im = ax.imshow(
        data,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="none",
    )

    # --- WCS ticks/labels styling ---
    ra = ax.coords[0]
    dec = ax.coords[1]
    # Sexagesimal tick labels
    ra.set_major_formatter("hh:mm:ss")
    dec.set_major_formatter("dd:mm:ss")
    # Axis labels (Dec vertical), no alignment setting seems to work with CoordinateHelper.
    ra.set_axislabel("Right ascension")
    dec.set_axislabel("Declination")
    dec.set_ticklabel(rotation='vertical')
    # Major tick size
    ra.set_ticks(size=5)
    dec.set_ticks(size=5)
    # Minor ticks
    ra.set_minor_frequency(4)
    dec.set_minor_frequency(4)
    ra.display_minor_ticks(True)
    dec.display_minor_ticks(True)
    # Make all tick marks white, and ticks inward
    ra.tick_params(color="white", which="both", direction="in", bottom=True, top=True, labelbottom=True)
    dec.tick_params(color="white", which="both", direction="in", left=True, right=True, labelleft=True)

    # Trim image size (central zoom)
    ny, nx = data.shape
    cx, cy = nx / 2, ny / 2
    width = nx / zoom
    height = ny / zoom
    ax.set_xlim(cx - width/2, cx + width/2)
    ax.set_ylim(cy - height/2, cy + height/2)

    # Colorbar axis: fixed fraction of the parent axes height, since inset_axes and divider don't like the CoordinateHelper
    fig.canvas.draw()
    pos = ax.get_position()
    cax = fig.add_axes([pos.x1 + 0.015, pos.y0, 0.02, pos.height])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(cbar_label, rotation=90, labelpad=10)
    cbar.set_ticks(cticks)
    fig.savefig("contaminating_emission.pdf", dpi=300, bbox_inches="tight")

    # Restoring beam (from FITS header)
    if all(k in hdr for k in ("BMAJ", "BMIN", "BPA", "CDELT1")):
        plot_restoring_beam(ax, hdr, beam_loc, beam_detail)
 
    return fig, ax


def export_fits(image, out):
    c_str = f"exportfits(imagename='{image}', fitsimage='{out}', dropdeg=True, overwrite=True)"
    os.system(f"casa -c \"{c_str}\"")
    os.system("rm casa*.log")

img = "../../../Image-Processing/RXJ1720+2638/full_image/image-p5.image.tt0"
fits_file = "rxj1720.fits"

export_fits(img, fits_file)
fig, ax = plot_fits(fits_file, scale="log", alpha=1000, vmin=-1e-6, vmax=1.2, zoom=2.5, beam_detail="flat")

add_arrow_label_pixel(
    ax,
    1405, 1050,
    text="S1",
    text_offset_pix=(40, 60),
)

add_arrow_label_pixel(
    ax,
    1165, 1165,
    text="BCG",
    text_offset_pix=(40, 60),
)

plt.savefig("contaminating_emission.pdf", dpi=300, bbox_inches='tight')