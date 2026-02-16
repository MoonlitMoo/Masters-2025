import os
import math
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.visualization import MinMaxInterval, AsinhStretch, ImageNormalize
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import FuncNorm
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
from matplotlib.patches import Ellipse, Circle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


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

BASE_MASTERS_DIR = "../../../.."

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
    text_pe = [pe.Stroke(linewidth=1.5, foreground="black"), pe.Normal()]
    arrow_pe = [pe.Stroke(linewidth=2, foreground="black"), pe.Normal()]

    ann = ax.annotate(
        text,
        xy=(x_pix, y_pix),
        xycoords=ax.get_transform("pixel"),
        xytext=(xt, yt),
        textcoords=ax.get_transform("pixel"),
        path_effects=text_pe,
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
            path_effects=arrow_pe
        ),
        zorder=zorder,
    )
    return ann

def plot_fits(
    fits_path,
    rms,
    scale = "ujy",
    vmin=None,
    vmax=None,
    colour_scale="linear",
    alpha=0.1,
    cmap="inferno",
    zoom = 1,
    contour_levels=[-3, 3, 6, 12, 24, 48],
    neg_contour_color="white",
    beam_detail="high",  # Should beam image include major/minor axis
    figsize=(6.5, 6.5),
    beam_loc=(0.1, 0.1)  # In fraction of axis
):
    hdu = fits.open(fits_path)[0]
    data = np.squeeze(hdu.data).astype(float)
    hdr = hdu.header
    wcs = WCS(hdr)
    
    # Get zoom factors
    ny, nx = data.shape
    cx, cy = nx / 2, ny / 2
    width = nx / zoom
    height = ny / zoom
    x_min, x_max = int(round(cx - width / 2)), int(round(cx + width / 2))
    y_min, y_max = int(round(cy - height / 2)), int(round(cy + height / 2))

    # Set vmin/vmax based on visible data
    if vmin is None:
        vmin = np.nanmin(data[y_min:y_max, x_min:x_max])
    if vmax is None:
        vmax = np.nanmax(data[y_min:y_max, x_min:x_max])
    
    # Scale Jy/beam -> uJy/beam for display. 
    if scale.lower() == "ujy":
        scale_factor = 1e6
        cbar_label = r"$\mu$Jy beam$^{-1}$"
    elif scale.lower() == "mjy":
        scale_factor = 1e3
        cbar_label = r"mJy beam$^{-1}$"
    else:
        raise ValueError(f"Unknown scale {scale}.")   
    data *= scale_factor 
    rms *= scale_factor
    vmin *= scale_factor
    vmax *= scale_factor
    data = np.clip(data, vmin, vmax)
    
    # Set colour scaling
    if colour_scale == "linear":
        norm = FuncNorm(
            (lambda x: x, lambda y: y),
            vmin=vmin, vmax=vmax
        )
        cticks = np.linspace(0, round(vmax), 5)
    elif colour_scale == "asinh":
        norm = ImageNormalize(data, interval=MinMaxInterval(),
                      stretch=AsinhStretch(a=alpha))
        cticks = None
    elif colour_scale == "log":
        # Log scale colouring, mimic CARTA func log(ax + 1)
        norm = FuncNorm(
            (lambda x: np.log10(alpha*x + 1),
            lambda y: (10**y - 1) / alpha),
            vmin=vmin, vmax=vmax,
        )
        cticks = [0, 0.01, 0.05, 0.1, 0.5, 1]
    else:
        raise ValueError(f"Unknown colour_scale {colour_scale}")


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

    # Trim image size (central zoom)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Colorbar axis: fixed fraction of the parent axes height, since inset_axes and divider don't like the CoordinateHelper
    fig.canvas.draw()
    pos = ax.get_position()
    cax = fig.add_axes([pos.x1 + 0.015, pos.y0, 0.02, pos.height])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(cbar_label, rotation=90, labelpad=10)
    if cticks is not None:
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

# 2A0335+096
def twoA0335():
    print("2A0335+096:")
    c_name = "2A0335"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/2A0335+096/full_image/image-p6.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/2A0335+096/minihalo/minihalo.pbcor.image.tt0"
    mask_img = f"{BASE_MASTERS_DIR}/Image-Processing/2A0335+096/minihalo/significance.mask"
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.52e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 4.14x3.32 arcsec, -9.9
        fits_file, rms=sigma, zoom=4.5, scale="mjy", colour_scale="asinh", alpha=0.001, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=0.716, length=40)
    annotate_arrow_label_pixel(ax, 1150, 1145, "S1", text_offset_pix=(-10, -60))
    annotate_arrow_label_pixel(ax, 1164, 1164, "S2", text_offset_pix=(30, 0))
    annotate_arrow_label_pixel(ax, 1070, 1115, "S3", text_offset_pix=(-40, -40))
    annotate_arrow_label_pixel(ax, 1120, 1167, "NE Lobe", text_offset_pix=(-80, 20))
    annotate_arrow_label_pixel(ax, 1175, 1137, "SW Lobe", text_offset_pix=(80, -20))
    # Annotate fossil + relic lobes
    def annotate_circle(ax, x_pix, y_pix, radius_pix, **kwargs):
        circle = Circle((x_pix, y_pix), radius_pix, fill=False, **kwargs)
        ax.add_patch(circle)
    rad_px = 35 / 0.716  # 35 kpc diam / kpc per " * 2 px per " / 2 = rad
    annotate_circle(ax, 1070, 1110, rad_px, color='r')
    annotate_circle(ax, 1230, 1190, rad_px, color='r')
    annotate_circle(ax, 1320, 1280, rad_px*1.4, color='r')
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.43e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 6.68x5.14 arcsec, -14.2
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.3, zoom=6, beam_detail="flat")
    # Annotate mask
    # export_fits(mask_img, mask_file)
    # annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=0.716, length=25)
    annotate_cross(ax, "3h38m41.4s", "9d58m17.5s")
    annotate_cross(ax, "3h38m40.6s", "9d58m11.6s")
    annotate_cross(ax, "3h38m39.9s", "9d58m07.3s")
    annotate_cross(ax, "3h38m40.3s", "9d58m17.9s")
    # Annotate fossil lobes
    annotate_circle(ax, 1070, 1110, rad_px, color='r')
    annotate_circle(ax, 1230, 1190, rad_px, color='r')
    annotate_arrow_label_pixel(ax, 1070, 1120, "S3", text_offset_pix=(-40, 20))
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# A478
def a478():
    print("A478:")
    c_name = "a478"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/A478/full_image/image-p6.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/A478/minihalo/minihalo.pbcor.image.tt0"
    
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 1.94e-6  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(
        fits_file, rms=sigma, zoom=2, scale="mjy", colour_scale="asinh", alpha=0.001, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=1.646, length=150)
    annotate_arrow_label_pixel(ax, 1165, 1165, "S1", text_offset_pix=(60, 60))
    annotate_arrow_label_pixel(ax, 970, 1250, "S2", text_offset_pix=(60, 60))
    annotate_arrow_label_pixel(ax, 850, 1340, "S3", text_offset_pix=(-60, 60))
    annotate_arrow_label_pixel(ax, 770, 1150, "S4", text_offset_pix=(-20, -90))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 1.88e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(fits_file, rms=sigma, colour_scale="asinh", alpha=0.5, zoom=7, beam_detail="flat")
    # Annotate mask
    # export_fits(f"{BASE_MASTERS_DIR}/Image-Processing/A478/minihalo/significance.mask", mask_file)
    annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=1.646, length=50)
    annotate_cross(ax, "4h13m25.29s", "10d27m54.6s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# RXJ1720+2638
def rxj1720():
    print("RXJ1720+2638:")
    c_name = "rxj1720"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXJ1720+2638/full_image/image-p5.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXJ1720+2638/minihalo/model_minihalo/minihalo_uvconstr.pbcor.image.tt0"
    
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 3.48e-6  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.79x2.51 arcsec, -25.6
        fits_file, rms=sigma, zoom=3, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.775, length=200)
    annotate_arrow_label_pixel(ax, 1158, 1158, "S1", text_offset_pix=(50, 50))
    annotate_arrow_label_pixel(ax, 1055, 1270, "S2")
    annotate_arrow_label_pixel(ax, 1400, 1045, "S3")
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')

    # Make the subtracted image
    sub_fits_file = f"FITS/{c_name}_sub.fits"
    # export_fits(sub_img, sub_fits_file)
    sigma = 3.38e-6  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 4.65x4.38 arcsec, -55.7
        sub_fits_file, rms=sigma, zoom=6, colour_scale="asinh", alpha=0.15, beam_detail="flat")
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
    annotate_scale_bar(ax, (0.65, 0.1), kpc_scale=2.775, length=100)
    annotate_cross(ax, "17h20m10.03s", "26d37m31.9s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# A2204
def a2204():
    print("A2204:")
    c_name = "a2204"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/A2204/full_image/image-p4.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/A2204/minihalo/minihalo.pbcor.image.tt0"
    mask_img = f"{BASE_MASTERS_DIR}/Image-Processing/A2204/minihalo/significance.mask"

    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 6.04e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.02x1.69 arcsec, -58.0
        fits_file, rms=sigma, zoom=5, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48, 96], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.646, length=50)
    annotate_arrow_label_pixel(ax, 455, 445, "S1", text_offset_pix=(20, 0))
    annotate_arrow_label_pixel(ax, 455, 462, "S2", text_offset_pix=(20, 0))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.99e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 3.67x2.79 arcsec, -32.4
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.5, zoom=8, beam_detail="flat")
    # Annotate mask
    # export_fits(mask_img, mask_file)
    # annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.646, length=75)
    annotate_cross(ax, "16h32m46.94s", "5d34m40.7s")
    annotate_cross(ax, "16h32m46.94s", "5d34m32.5s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# MS1455+2232
def ms1455():
    print("MS1455+2232:")
    c_name = "ms1455"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/MS1455+2232/full_image/image-p4.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/MS1455+2232/minihalo/minihalo.image.tt0"

    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.99e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.43x2.27 arcsec, -27.5
        fits_file, rms=sigma, zoom=3, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=4.007, length=200)
    annotate_arrow_label_pixel(ax, 1160, 1160, "S1", text_offset_pix=(30, 30))
    annotate_arrow_label_pixel(ax, 1278, 943, "S2", text_offset_pix=(30, 30))
    annotate_arrow_label_pixel(ax, 1330, 1120, "S3", text_offset_pix=(-40, 40))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.85e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 3.02x2.80 arcsec, -25.1 
        fits_file, rms=sigma, scale="mjy", colour_scale="asinh", alpha=0.1, zoom=4.5, beam_detail="flat")
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.1, 0.2), kpc_scale=4.007, length=100)
    annotate_cross(ax, "14h57m15.11s", "22d20m34s")
    annotate_cross(ax, "14h57m10.80s", "22d18m44.71s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# Z3146
def z3146():
    print("Z3146:")
    c_name = "z3146"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/Z3146/full_image/image-final.image.tt0"

    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 3.19e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 3.56x2.62 arcsec, -35.
        fits_file, rms=sigma, zoom=4, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=4.347, length=200)
    annotate_arrow_label_pixel(ax, 1160, 1160, "S1", text_offset_pix=(30, 40))
    annotate_arrow_label_pixel(ax, 1185, 1145, "S2", text_offset_pix=(30, 20))
    annotate_arrow_label_pixel(ax, 1000, 1075, "S3", text_offset_pix=(0, -50))
    annotate_arrow_label_pixel(ax, 972, 1100, "S4", text_offset_pix=(-50, 30))
    annotate_arrow_label_pixel(ax, 1000, 1216, "S5", text_offset_pix=(20, 20))
    annotate_arrow_label_pixel(ax, 1213, 900, "S6", text_offset_pix=(-70, -10))
    annotate_arrow_label_pixel(ax, 1225, 925, "Lobes", text_offset_pix=(30, 20))
    annotate_arrow_label_pixel(ax, 1243, 900, "Lobes", text_offset_pix=(12, 45))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')

# RXCJ1115+0129
def rxcj1115():
    print("RXCJ1115+0129:")
    c_name = "rxcj1115"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXCJ1115+0129/full_image/image-p4.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXCJ1115+0129/minihalo/minihalo.pbcor.image.tt0"
    mask_image = f"{BASE_MASTERS_DIR}/Image-Processing/RXCJ1115+0129/minihalo/significance.mask"
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.66e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.89x2.20 arcsec, -31.9
        fits_file, rms=sigma, zoom=3, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=4.856, length=300)
    annotate_arrow_label_pixel(ax, 1160, 1140, "S1", text_offset_pix=(0, -70))
    annotate_arrow_label_pixel(ax, 1475, 1000, "S2", text_offset_pix=(-80, -10))
    annotate_arrow_label_pixel(ax, 830, 955, "S3", text_offset_pix=(60, -10))
    annotate_arrow_label_pixel(ax, 875, 1280, "S4", text_offset_pix=(60, -10))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.63e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 2.89x2.20 arcsec, -31.9
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.5, zoom=9, beam_detail="flat")
    # Annotate mask
    # export_fits(mask_image, mask_file)
    annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=4.856, length=100)
    annotate_cross(ax, "11h15m51.93s", "1d29m55.1s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# A1413
def a1413():
    print("A1413:")
    c_name = "a1413"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/A1413/full_image/image-p4.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/A1413/minihalo/minihalo.pbcor.image.tt0"
    
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.6e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 6.33x5.97 arcsec, -49.9
        fits_file, rms=sigma, zoom=3, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.455, length=150)
    annotate_arrow_label_pixel(ax, 1248, 1117, "S1", text_offset_pix=(40, -10))
    annotate_arrow_label_pixel(ax, 1136, 1170, "S2", text_offset_pix=(0, 40))
    annotate_arrow_label_pixel(ax, 1160, 1160, "S3", text_offset_pix=(30, 40))
    annotate_arrow_label_pixel(ax, 1186, 1090, "S4", text_offset_pix=(30, -50))
    annotate_arrow_label_pixel(ax, 1387, 1400, "S5", text_offset_pix=(-80, -10))
    annotate_arrow_label_pixel(ax, 1193, 904, "S6", text_offset_pix=(40, -10))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.27e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 8.32x7.85 arcsec, -52.6
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.5, zoom=6, beam_detail="flat")
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=2.455, length=50)
    annotate_cross(ax, "11h55m18.0s", "23d24m17.3s")
    annotate_cross(ax, "11h55m18.6s", "23d24m22.6s")
    annotate_cross(ax, "11h55m17.1s", "23d23m53.4s")
    annotate_cross(ax, "11h55m15.1s", "23d24m01.9s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# ACTJ0022-0036
def actj0022():
    print("ACTJ0022-0036:")
    c_name = "actj0022"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/ACTJ0022-0036/full_image/image-p4.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/ACTJ0022-0036/minihalo/minihalo.pbcor.image.tt0"
    
    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.1e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.47x2.10 arcsec, 13.2
        fits_file, rms=sigma, zoom=4, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=7.521, length=300)
    annotate_arrow_label_pixel(ax, 1160, 1138, "S1", text_offset_pix=(20, -40))
    annotate_arrow_label_pixel(ax, 1347, 1224, "S2", text_offset_pix=(-60, -10))
    annotate_arrow_label_pixel(ax, 1033, 1147, "S3", text_offset_pix=(30, -30))
    annotate_arrow_label_pixel(ax, 1170, 1338, "S4", text_offset_pix=(30, -30))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 1.94e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 2.90x2.36 arcsec, 10.7
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.5, zoom=9, beam_detail="flat")
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=7.521, length=200)
    annotate_cross(ax, "0h22m13.02s", "-0d36m33.57s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')

# RXJ2129+0005
def rxj2129():
    print("RXJ2129+0005:")
    c_name = "rxj2129"
    full_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXJ2129+0005/full_image/image-p4-2.image.tt0"
    sub_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXJ2129+0005/minihalo/minihalo.pbcor.image.tt0"
    mask_img = f"{BASE_MASTERS_DIR}/Image-Processing/RXJ2129+0005/minihalo/significance.mask"

    # Make the full image
    fits_file = f"FITS/{c_name}.fits"
    # export_fits(full_img, fits_file)
    sigma = 2.24e-06  # get_threshold(full_img)
    fig, ax, wcs = plot_fits(  # 2.53x2.23 arcsec, -15.4
        fits_file, rms=sigma, zoom=7, scale="mjy", colour_scale="asinh", alpha=0.01, 
        contour_levels=[-3, 6, 12, 24, 48], neg_contour_color="black", beam_detail="flat")
    # Annotate the scale + points.
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=3.727, length=150)
    annotate_arrow_label_pixel(ax, 1134, 1143, "S1", text_offset_pix=(-40, -20))
    annotate_arrow_label_pixel(ax, 1181, 1130, "S2", text_offset_pix=(20, -10))
    # annotate_arrow_label_pixel(ax, 973, 1230, "S3", text_offset_pix=(20, -10))
    # annotate_arrow_label_pixel(ax, 455, 462, "S2", text_offset_pix=(20, 0))
    # annotate_arrow_label_pixel(ax, 485, 489, "S3", text_offset_pix=(15, -15))
    plt.savefig(f"{c_name}.pdf", dpi=300, bbox_inches='tight')
    
    # Make subtracted image
    fits_file = f"FITS/{c_name}_sub.fits"
    mask_file = f"FITS/{c_name}_mask.fits"
    # export_fits(sub_img, fits_file)
    sigma = 2.03e-06  # get_threshold(sub_img)
    fig, ax, wcs = plot_fits(  # 3.67x2.79 arcsec, -32.4
        fits_file, rms=sigma, colour_scale="asinh", alpha=0.9, zoom=9, beam_detail="flat")
    # Annotate mask
    # export_fits(mask_img, mask_file)
    annotate_mask_contour(ax, wcs, mask_file)
    # Annotate the scale + bcg
    annotate_scale_bar(ax, (0.85, 0.1), kpc_scale=3.727, length=75)
    annotate_cross(ax, "21h29m39.97s", "0d05m21.05s")
    annotate_cross(ax, "21h29m39.97s", "0d05m21.05s")
    plt.savefig(f"{c_name}_sub.pdf", dpi=300, bbox_inches='tight')


# twoA0335()
# a478()
# rxj1720()
# a2204()
ms1455()
# z3146()
# rxcj1115()
# a1413()
# A1795
# A2626
# actj0022()
# rxj2129()