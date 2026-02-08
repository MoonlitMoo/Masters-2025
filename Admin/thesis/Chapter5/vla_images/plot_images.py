import os
import math
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
from matplotlib.colors import FuncNorm
import matplotlib.patheffects as pe


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
    line_pe = [pe.Stroke(linewidth=1, foreground="black"), pe.Normal()]
    line_kwargs.setdefault("color", "white")
    line = ax.plot([xl, xr], [y_center, y_center], **line_kwargs, path_effects=line_pe)[0]

    # Draw text centred above the line
    dy = text_offset * (y1 - y0)
    text_kwargs.setdefault("color", "white")
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

def annotate_mask_contour(
    ax, ax_wcs: WCS, mask_fits_path, *, 
    levels = None, threshold: float = 0.5, 
    linewidths: float = 1, linestyles: str = "--", colors: str = "red",
    zorder: int = 10, origin: str = "lower"
):
    """
    Open a FITS mask file and plot its contour onto an existing WCSAxes `ax`.

    Parameters
    ----------
    ax
        Matplotlib axis to draw on (typically WCSAxes).
    ax_wcs
        WCS describing the target axis coordinate frame (usually ax.wcs).
    mask_fits_path
        Path to the FITS mask image.
    levels
        Contour levels in mask value units. If None, uses a single level at `threshold`.
        For binary masks, threshold=0.5 is typical.
    threshold
        Used only when levels is None.
    linewidths, linestyles, alpha, zorder
        Passed through to `ax.contour`.
    origin
        "lower" is typical for FITS display.
    Returns
    -------
    QuadContourSet
        The contour artist.
    """
    with fits.open(mask_fits_path) as hdul:
        # Prefer first non-empty image HDU
        hdu = next((h for h in hdul if getattr(h, "data", None) is not None), hdul[0])
        data = np.asarray(hdu.data)
        mask_hdr = hdu.header

    # Drop extra dimensions (e.g., Stokes/freq) by taking the first plane
    if data.ndim > 2:
        # take first element along leading axes until 2D remains
        while data.ndim > 2:
            data = data[0]

    # if transpose:
    #     data = data.T
    # if flip_x:
    #     data = data[:, ::-1]
    # if flip_y:
    #     data = data[::-1, :]

    # Build mask WCS; contour will be reprojected onto ax_wcs via transform
    mask_wcs = WCS(mask_hdr).celestial

    if levels is None:
        levels = (threshold,)

    # Contour in the mask's sky coordinates, drawn onto the axis WCS frame
    cs = ax.contour(
        data,
        levels=levels,
        linewidths=linewidths,
        linestyles=linestyles,
        colors=colors,
        zorder=zorder,
        origin=origin,
        transform=ax.get_transform(mask_wcs),
    )

    return cs

def annotate_cross(ax, ra, dec, size_arcsec=2.0,
                       color="green", lw=1.5, frame="icrs", **kwargs):
    """
    Draw a cross marker at a given sky position on a WCSAxes plot.

    Parameters
    ----------
    ax : astropy.visualization.wcsaxes.WCSAxes
        Axes with a WCS projection.
    ra_deg, dec_deg : float
        Sky coordinates in degrees (ICRS).
    size_arcsec : float
        Half-length of each arm of the cross in arcseconds.
    color : str
        Line colour.
    lw : float
        Line width.
    **kwargs :
        Passed to matplotlib Axes.plot.
    """

    if isinstance(ra, str) or isinstance(dec, str):
        c = SkyCoord(ra, dec, frame=frame)
        ra_deg = c.ra.deg
        dec_deg = c.dec.deg
    else:
        ra_deg = ra
        dec_deg = dec

    # Cross arm length in degrees
    d = size_arcsec / 3600.0

    # Horizontal arm (constant Dec)
    ax.plot([ra_deg - d, ra_deg + d],
            [dec_deg, dec_deg],
            transform=ax.get_transform("world"),
            color=color, lw=lw, **kwargs)

    # Vertical arm (constant RA)
    ax.plot([ra_deg, ra_deg],
            [dec_deg - d, dec_deg + d],
            transform=ax.get_transform("world"),
            color=color, lw=lw, **kwargs)

def annotate_arrow_label_pixel(
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
    rms,
    vmin=None,  # Mjy
    vmax=None,  # Mjy
    scale="linear",
    alpha=None,
    cmap="inferno",
    zoom = 1,
    beam_detail="high",  # Should beam image include major/minor axis
    figsize=(6.5, 6.5),
    beam_loc=(0.1, 0.1),  # In fraction of axis
    cbar_label=r"$\mu$Jy beam$^{-1}$",
):
    hdu = fits.open(fits_path)[0]
    data = np.squeeze(hdu.data).astype(float)
    hdr = hdu.header
    wcs = WCS(hdr)
    
    # Scale Jy/beam -> uJy/beam for display. Clip to max and min values.
    data *= 1e6
    rms *= 1e6
    data = np.clip(data, vmin, vmax)
    
    # Set vmin/vmax
    if vmin is None:
        vmin = np.min(data)
    if vmax is None:
        vmax = np.max(data)
    
    # Set colour scaling
    if scale == "linear":
        norm = FuncNorm(
            (lambda x: x, lambda y: y),
            vmin=vmin, vmax=vmax
        )
        cticks = np.linspace(0, round(vmax), 5)
    elif scale == "log":
        # Log scale colouring, mimic CARTA func log(ax + 1)
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

    # Add contours
    levels = np.array([-3, 3, 6, 12, 24, 48]) * rms
    linestyles = ['dotted' if lvl < 0 else 'solid' for lvl in levels]

    ax.contour(
        data,
        levels=levels,
        colors="white",
        linewidths=0.5,
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
    
    # Restoring beam (from FITS header)
    if all(k in hdr for k in ("BMAJ", "BMIN", "BPA", "CDELT1")):
        plot_restoring_beam(ax, hdr, beam_loc, beam_detail)
 
    return fig, ax, wcs

def export_fits(image, out):
    c_str = f"exportfits(imagename='{image}', fitsimage='{out}', dropdeg=True, overwrite=True)"
    os.system(f"casa --nologger --nogui -c \"{c_str}\"")
    os.system("rm casa*.log")

def get_threshold(image):
    residual_image = ".".join(image.split(".")[:-2]) + ".residual.tt0"
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

# RXJ1720+2638
def rxj1720():
    print("RXJ1720+2638:")
    img = "../../../../Image-Processing/RXJ1720+2638/minihalo/model_minihalo/minihalo.image.tt0"
    fits_file = "rxj1720.fits"
    # export_fits(img, fits_file)
    sigma = 3.12e-06  # get_threshold(img)
    fig, ax, wcs = plot_fits(fits_file, rms=sigma, vmin=-1, vmax=50, zoom=5, beam_detail="high")
    # This has a custom mask that we need to build, load, and then add as contour.
    # os.system("casa --nologger --nogui -c rxj1720_custom_mask.py")
    def plot_mask_contour(ax, wcs, mask_path, *, level=0.5, **contour_kwargs):
        mask = np.load(mask_path)
        mask = np.squeeze(mask).astype(float).T
        contour_kwargs.setdefault("colors", "red")
        contour_kwargs.setdefault("linewidths", 1)
        ax.contour(mask, levels=[level], transform=ax.get_transform(wcs), **contour_kwargs,)
    plot_mask_contour(ax, wcs, "rxj1720_masks/centre_mask.npy", colors="red")
    plot_mask_contour(ax, wcs, "rxj1720_masks/tail_mask.npy", colors="red", linestyles="--")
    # Annotate the scale + BCG + subtracted points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.758, length=100)
    annotate_cross(ax, "17h20m10.03s", "26d37m31.9s")
    plt.savefig("rxj1720.pdf", dpi=300, bbox_inches='tight')

# A478
def a478():
    print("A478:")
    c_name = "a478"
    img = "../../../../Image-Processing/A478/minihalo/minihalo.image.tt0"
    fits_file = f"{c_name}.fits"
    mask_file = f"{c_name}_mask.fits"
    # export_fits(img, fits_file)
    sigma = 1.88e-06  # get_threshold(img)
    fig, ax, wcs = plot_fits(fits_file, rms=sigma, vmin=-1, vmax=50, zoom=5, beam_detail="high")
    # Annotate mask
    # export_fits("../../../../Image-Processing/A478/minihalo/significance.mask", mask_file)
    annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=1.612, length=75)
    annotate_cross(ax, "4h13m25.29s", "10d27m54.6s")
    plt.savefig("a478.pdf", dpi=300, bbox_inches='tight')
    

# rxj1720()
a478()