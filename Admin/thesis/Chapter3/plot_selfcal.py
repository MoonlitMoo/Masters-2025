import os
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from astropy.visualization import MinMaxInterval, AsinhStretch, ImageNormalize


f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 12 * f_scale


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
            linewidth=0.75,
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
                linewidth=0.75,
                zorder=11,
            )

            ax.plot(
                [x_pix - dx_min, x_pix + dx_min],
                [y_pix - dy_min, y_pix + dy_min],
                transform=ax.get_transform("pixel"),
                color="0.3",
                linewidth=0.75,
                zorder=11,
            )
        ax.add_patch(beam)

def annotate_scale_bar(
    ax,
    scale_loc,
    kpc_scale,
    length,
    inv_colour=False,
    *,
    text_offset=0.02,
    line_kwargs=None,
    text_kwargs=None,
):
    """
    Draw a horizontal scale bar and annotate it with length in kpc above.

    Parameters
    ----------
    ax : matplotlib Axes
        Target axes.
    scale_loc: tuple of float
        The fractional location to put the bar.
    kpc_scale : float
        The number of kpc per arcsec (2 pixels)
    length: float
        The kpc length of the bar.
    text_offset : float
        Vertical offset *as a fraction of the y-axis range*.
    line_kwargs : dict or None
        Passed to ax.plot for the line.
    text_kwargs : dict or None
        Passed to ax.text for the label.

    Returns
    -------
    line, text : matplotlib artists
    """
    if line_kwargs is None:
        line_kwargs = {}
    if text_kwargs is None:
        text_kwargs = {}

    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x_center = x0 + scale_loc[0] * (x1 - x0)
    y_center = y0 + scale_loc[1] * (y1 - y0)
    
    pix_scale = 0.5  # arcsec
    b_length = length / (kpc_scale * 0.5) # Correct to pixel size then find total bar length
    xl = x_center - b_length / 2
    xr = x_center + b_length / 2
    # Draw line
    outline_c = "black" if not inv_colour else "white"
    text_c = "black" if inv_colour else "white"
    line_pe = [pe.Stroke(linewidth=1.5, foreground=outline_c), pe.Normal()]
    line_kwargs.setdefault("color", text_c)
    
    line = ax.plot([xl, xr], [y_center, y_center], **line_kwargs)[0]
    line.set_path_effects([pe.Stroke(linewidth=3.0, foreground=outline_c), pe.Normal()])
    # Draw text centred above the line
    dy = text_offset * (y1 - y0)
    text_kwargs.setdefault("color", text_c)
    text = ax.text(
        x_center,
        y_center + dy,
        f"{length} kpc",
        ha="center",
        va="bottom",
        **text_kwargs,
        path_effects=line_pe
    )

    return line, text


def plot_fits_on_ax(
    fits_path,
    ax,
    rms,
    *,
    norm=None,
    colour_scale="asinh",
    alpha=0.1,
    cmap="inferno",
    zoom=1,
    contour_levels=[-3, 3, 6, 12, 24, 48],
    neg_contour_color="white",
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

    data *= 1e3  # uJy
    rms *= 1e3
    
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

    levels = np.array(contour_levels) * rms
    linestyles = ['dotted' if lvl < 0 else 'solid' for lvl in levels]
    colors = [neg_contour_color if lvl < 0 else 'white' for lvl in levels]

    ax.contour(
        data,
        levels=levels,
        colors=colors,
        linewidths=1,
        linestyles=linestyles,
        transform=ax.get_transform(wcs)
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

    if not show_xlabel:
        ax.coords[0].set_ticklabel_visible(False)
        ax.coords[0].set_axislabel("")

    if not show_ylabel:
        ax.coords[1].set_ticklabel_visible(False)
        ax.coords[1].set_axislabel("")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    if all(k in hdr for k in ("BMAJ", "BMIN", "BPA", "CDELT1")):
            plot_restoring_beam(ax, hdr, (0.1, 0.1), 'flat')
    return im, wcs, norm_used

def export_fits(image, out):
    c_str = f"exportfits(imagename='{image}', fitsimage='{out}', dropdeg=True, overwrite=True)"
    os.system(f"casa --nologger --nogui -c \"{c_str}\"")
    os.system("rm casa*.log")

def get_threshold(image):
    residual_image = image.split(".image.tt0")[0].split(".pbcor")[0] + ".residual.tt0"
    c_str = (
        f"res = imstat('{residual_image}')\n"
        "sigma = res['sigma'][0]\n"
        "with open('sigma.txt', 'w') as f:\n"
        "    f.write(str(sigma))\n"
    )
     
    os.system(f"casa --nologger --nogui -c \"{c_str}\"")
    with open("sigma.txt") as f:
        sigma = float(f.read())
    os.system("rm sigma.txt casa*.log")
    print(f"Found threshold {sigma:.3g} for {image}")
    return sigma

BASE_DIR = "."
OUT_DIR = "."
images = ["image-p1", "image-p5"]

fits_paths = []
thresholds = []
for im in images:
    # export_fits(f"{BASE_DIR}/{im}.image.tt0", f"{OUT_DIR}/{im}.fits")
    fits_paths.append(f"{OUT_DIR}/{im}.fits")
    thresholds.append(get_threshold(f"{BASE_DIR}/{im}.image.tt0"))

wcs0 = WCS(fits.getheader(fits_paths[0]))
fig, axs = plt.subplots(
    1, 2, figsize=(8, 4),
    subplot_kw={"projection": wcs0},
    sharex=True,
    sharey=True,
)
axs = np.ravel(axs)

norm = None
for i, (fs, ax) in enumerate(zip(fits_paths, axs)):
    do_y = i == 0
    _, _, norm = plot_fits_on_ax(
        fs, ax, norm=norm, rms=20e-6/3, zoom=8, alpha=0.01,
        show_xlabel=True,
        show_ylabel=do_y,
    )
# ax.set_title(rf"$uv>{label}$ k$\lambda$")

# After creating your 2x2 subplot grid
# fig, axs = plt.subplots(2, 2, figsize=(...), constrained_layout=False)
axs[0].set_title("Before self-cal")
axs[1].set_title("After self-cal")

plt.tight_layout()
# Get bounding boxes of all panels
fig.canvas.draw()  # ensure positions are updated

# Find overall vertical span of subplot grid
top = max(ax.get_position().y1 for ax in axs.ravel())
bottom = min(ax.get_position().y0 for ax in axs.ravel())
right = max(ax.get_position().x1 for ax in axs.ravel())

# Define colourbar axis just to the right
cbar_width = 0.02
cbar_pad = 0.015

cax = fig.add_axes([
    right + cbar_pad,   # x position
    bottom,             # y position
    cbar_width,         # width
    top - bottom        # height
])

# Create mappable
sm = plt.cm.ScalarMappable(norm=norm, cmap='inferno')
sm.set_array([])

cbar = fig.colorbar(sm, cax=cax)
cbar.set_label(r"mJy beam$^{-1}$", rotation=90)
cbar.locator = MaxNLocator(6)
plt.savefig("selfcal_comparison.pdf", dpi=300, bbox_inches='tight')