import os
import re

import numpy as np
import pandas as pd
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.stats import chi2 as chi2dist

from casatasks import imfit, imstat, tclean


def contour_sum(data, level, *, seed=None, pick='largest',
                     connectivity=1, fill_holes=True, valid_mask=None):
    """
    Sum pixels/voxels inside thresholded connected regions.
    Created via ChatGPT.

    Parameters
    ----------
    data : ndarray
        From ia.getchunk() or a numpy array. Can be (ny, nx) or (nz, ny, nx),
        or with extra singleton axes (they'll be squeezed).
    level : float
        Threshold.
    seed : tuple | None
        Index inside the desired region. (y,x) for 2D or (z,y,x) for 3D when pick='seed'.
    pick : {'largest', 'seed', 'all'}
        Selection strategy for components.
    connectivity : {1, 2} for 2D, {1, 2, 3} for 3D
        Neighborhood definition; higher = more connected.
    fill_holes : bool
        Fill internal holes in the binary mask.
    valid_mask : ndarray[bool] | None
        Optional mask (same shape as data before squeeze or broadcastable).

    Returns
    -------
    total : float
        Sum of data inside the selected region(s).
    mask_sel : ndarray[bool]
        Boolean mask (same shape as squeezed data) of selected pixels/voxels.
    info : dict
        {'ndim': 2 or 3, 'n_components': int, 'component_size': int or array, 'level': float}
    """
    a = np.asarray(data)
    a = np.squeeze(a)  # drop Stokes=1, Freq=1 if present
    if valid_mask is None:
        valid_mask = np.isfinite(a)
    else:
        valid_mask = np.squeeze(valid_mask) & np.isfinite(a)

    if a.ndim not in (2, 3):
        raise ValueError(f"Expected 2D or 3D after squeeze, got shape {a.shape} (ndim={a.ndim}).")

    # Threshold
    thr = (a >= level) & valid_mask

    # Optional hole fill
    if fill_holes:
        thr = ndi.binary_fill_holes(thr)

    # Build structure matching array rank
    structure = ndi.generate_binary_structure(a.ndim, connectivity)

    # Label connected components
    labels, nlab = ndi.label(thr, structure=structure)

    # No labels means we return empty
    if nlab == 0:
        z = np.zeros_like(thr, bool)
        return 0.0, z, {'ndim': int(a.ndim), 'n_components': 0, 'component_size': 0, 'level': float(level)}

    # Select components
    if pick == 'all':
        mask_sel = thr
        comp_sizes = np.bincount(labels.ravel())[1:]  # exclude background
    elif pick == 'largest':
        counts = np.bincount(labels.ravel())
        counts[0] = 0  # Ignore background
        lab_id = counts.argmax()
        mask_sel = (labels == lab_id)
        comp_sizes = int(mask_sel.sum())
    elif pick == 'seed':
        if seed is None:
            raise ValueError("pick='seed' requires a seed index: (y,x)")
        lab_id = labels[seed]
        if lab_id == 0:
            z = np.zeros_like(thr, bool)
            return 0.0, z, {'ndim': int(a.ndim), 'n_components': int(nlab), 'component_size': 0, 'level': float(level)}
        mask_sel = (labels == lab_id)
        comp_sizes = int(mask_sel.sum())
    else:
        raise ValueError("pick must be 'largest', 'seed', or 'all'.")

    total = float(a[mask_sel].sum())
    return total, mask_sel, {'ndim': int(a.ndim), 'n_components': int(nlab), 'component_size': comp_sizes, 'level': float(level)}




def get_minihalo_flux_density(image: str, output_image: str, mask: None, agn_err: float = None, agn_region: str = None, cleanup: bool = False, verbose: bool = False):
    """ Gets the minihalo flux density from an image.

    Parameters
    ----------
    image : str
        The image to use (without .image.tt0 suffix)
    output_image : str
        The path to use for the masked image (without .image.tt0 suffix).
    mask : ndarray, default = None
        An optional mask to use instead of calculating the contour.
    agn_err : int, default = None
        The error per beam of the agn subtraction.
    cleanup : bool, default=False
        Whether to remove the masked image at the end.
    verbose : bool, default=False
        Whether to print error breakdown.

    Returns
    -------
    flux : float
        The flux density of the minihalo in Jy
    error : float
        The approximated error of the flux density in Jy
    sigma : float
        The sigma used for the thresholding of the minihalo in Jy
    """
    image_file = f"{image}.image.tt0"
    residual_file = f"{image}.residual.tt0"
    output_file = f"{output_image}.image.tt0"

    # Get data from the image file. We need the raw data, beam area (in arcsec2), and the intensity around the agn.
    ia.open(image_file)
    beam_area = ia.beamarea()['arcsec2']
    pix = ia.getchunk()
    if agn_err is None:
        # Get the average value from the image of the minihalo and assume it's all bad
        # Estimate the region as a square the same area as the beam.
        agn_region = f"centerbox [[{agn_region}], [{np.sqrt(beam_area)}arcsec, {np.sqrt(beam_area)}arcsec]]"
        agn_err = np.average(ia.getregion(region=agn_region))
    ia.close()

    # Get the RMS using the residuals.
    res = imstat(residual_file)
    sigma = res["sigma"][0]

    # Get a 3sigma mask to use for the flux calculation if not given.
    if mask is None:
        _, mask, _ = contour_sum(pix, 3*sigma, pick='largest')

    # Save minihalo flux image for the flux calculation.
    if os.path.exists(output_file):
        os.system(f'rm -r {output_file}')
    os.system(f'cp -r {image_file} {output_file}')
    pix[~mask] = 0.
    ia.open(output_file)
    ia.putchunk(pix)
    ia.close()

    # Get the flux density from the masked image.
    res = imstat(output_file)
    flux = res["flux"][0]

    # Calculate the error following G14.
    # Calibration error is ~5%, multiply that to result to get effect on the flux
    cal_error = 0.05 * flux
    # Noise per beam weighted by number of beams. Pixel size is constant, but we need to calculate the area of the mask.
    pixel_area = 0.5 ** 2
    n_beams = (np.sum(mask) * pixel_area) / beam_area
    noise_error = sigma * np.sqrt(n_beams)
    # AGN subtraction error and the approximate area.
    # Using the G14 agn size as <1.4 kpc this is ~0.5", amusing same as pixel. Maybe use beam size instead?
    n_beams_agn = (0.5 ** 2) / beam_area
    sub_error = agn_err * np.sqrt(n_beams_agn)
    error = np.sqrt(cal_error ** 2 + noise_error ** 2 + sub_error ** 2)
    if verbose:
        print(f"Flux {flux:1.2e} +/- {error:1.2e}")
        print(f"cal error: {cal_error:1.2e}, noise error: {noise_error:1.2e}, sub_error: {sub_error:1.2e}")

    if cleanup:
        os.system(f'rm -r {output_file}')

    return flux, error, sigma

def _calculate_scaling(freq1, flux1, err1, freq2, flux2, err2):
    """
    Fit coefficient g so that flux2 = g * flux1, using weights 1/(e1^2+e2^2).
    """
    # Combined weights on the difference
    w = 1.0 / (err1**2 + err2**2)

    # Weighted least-squares solution for g:
    # minimize sum w * (f2 - g f1)^2  =>  g = sum(w f1 f2)/sum(w f1^2)
    S1 = np.sum(w * flux1 * flux2)
    S2 = np.sum(w * flux1**2)
    g = S1 / S2

    # 1σ uncertainty on g
    sigma_g = 1.0 / np.sqrt(S2)

    return g, sigma_g

def _plot_secondary_comparison(freq, flux1, err1, flux2, err2, g, sigma_g, title):
    """
    Top: both spectra with 1σ error bars.
    Bottom: ratio f2/f1 with error bars, best-fit g as a line, and ±1σ band.
    """
    ratio = flux2 / flux1
    # Propagate errors for the ratio (ignoring correlation): σ_r = r * sqrt((e1/f1)^2 + (e2/f2)^2)
    ratio_err = ratio * np.sqrt((err1/flux1)**2 + (err2/flux2)**2)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[2, 1], figsize=(8, 6))

    # Top panel: fluxes
    ax1.errorbar(freq, flux1, yerr=err1, fmt='o', ms=4, capsize=2, label='Dconfig1')
    ax1.errorbar(freq, flux2, yerr=err2, fmt='s', ms=4, capsize=2, label='Dconfig2')
    ax1.set_ylabel("Flux density")
    ax1.set_title(title)
    ax1.grid(True, ls='--', alpha=0.3)
    ax1.legend()

    # Bottom panel: ratio and fitted normalisation
    ax2.errorbar(freq, ratio, yerr=ratio_err, fmt='.', ms=5, alpha=0.9, label='Dconfig2 / Dconfig1')
    ax2.axhline(g, ls='--', lw=1.5, label=f'Best-fit g = {g:.4f}')
    ax2.axhline(1, ls='--', lw=1, c='r', label=None)
    ax2.fill_between(freq, g - sigma_g, g + sigma_g, alpha=0.15, step='mid', label='±1σ on g')
    ax2.set_xlabel("Frequency")
    ax2.set_ylabel("Ratio")
    ax2.grid(True, ls='--', alpha=0.3)
    ax2.legend(loc='best')

    plt.tight_layout()
    plt.savefig('secondary_models.png', dpi=300)
    plt.show()

def compare_secondary_models(filename: str, cluster_name: str):
    """ Creates a plot comparing the spectra of the fitted secondary models of the D configuration
    observations.
    The data should be in a csv file where each three columns corresponds to the Freq, Flux, Err for each obs.
    """
    # --- Load data ---
    df = pd.read_csv(filename)
    dconfig1_freq = df.iloc[:, 0]
    dconfig1_flux = df.iloc[:, 1]
    dconfig1_err = df.iloc[:, 2]
    dconfig2_freq = df.iloc[:, 3]
    dconfig2_flux = df.iloc[:, 4]
    dconfig2_err = df.iloc[:, 5]


    # --- Run Comparisonn ---
    g, sigma_g = _calculate_scaling(
        dconfig1_freq, dconfig1_flux, dconfig1_err,
        dconfig2_freq, dconfig2_flux, dconfig2_err
    )

    print(f"g = {g:.6f} ± {sigma_g:.6f}")
    print(f"Second obs changes by {(g-1) * 100:2.1f}%")

    _plot_secondary_comparison(
        dconfig1_freq, dconfig1_flux, dconfig1_err,
        dconfig2_flux, dconfig2_err,
        g=g, sigma_g=sigma_g,
        title=f"{cluster_name} D config \nSecondary calibrator models"
    )


def _read_log_value(l: str):
    """Return (flux, error) in mJy from a log line supporting Jy, mJy, and uJy."""
    pattern = r".*:\s*([\d.]+)\s*\+/-\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    # pattern = r".*\[flux\]:\s*([\d.]+)\s*(Jy|mJy|uJy)(?:/beam)?"
    match = re.match(pattern, l)
    if not match:
        print(f"Unknown flux scale in {l.strip()}")
        return np.nan, np.nan

    value, error, unit = match.groups()
    value, error = float(value), float(error)
    # value, unit = match.groups()
    # Convert to mJy
    if unit == "Jy":
        scale = 1000.0
    elif unit == "mJy":
        scale = 1.0
    elif unit == "uJy":
        scale = 1.0 / 1000.0
    else:
        scale = np.nan
    return value * scale, error * scale


def _get_flux_from_log(log):
    with open(log, "r") as f:
        for l in f.readlines():
            if "Integrated:" in l:
            # if "flux density" in l:
                return _read_log_value(l)
            # elif "Integrated:" in l:
            #     return read_log_value(l)
    return np.nan, np.nan


def check_point_flux(datasets, regions, labels,
                     redo_images: bool = False, output_dir: str = "check_flux"):
    image_dir = f"{output_dir}/images"
    log_dir = f"{output_dir}/log_dir"
    if redo_images:
        # Reset the output dir
        os.system(f'rm -r {output_dir}')
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Make the images
    images = []
    for d in datasets:
        imagename = f"{image_dir}/{d}_checkflux"
        images.append(imagename)
        if os.path.exists(f"{imagename}.image.tt0"):
            continue
        tclean(vis=f"{d}.ms",
            imagename=imagename,
            imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
            specmode='mfs', niter=10000, gain=0.1, threshold='0.025mJy',
            deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
            stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
            usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
            lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
            uvrange=">12klambda")

    # Fit the fluxes
    log_files = []
    for image in images:
        image_name = f"{image}.image.tt0"
        image_logs = []
        for region, label in zip(regions, labels):
            log_name = f"{log_dir}/{os.path.basename(image)}_{label}.log"
            image_logs.append(log_name)
            imfit(image_name, region=region, logfile=log_name, append=False)
        log_files.append(image_logs)

    # Grab the log data
    data = []
    for d, all_l in zip(datasets, log_files):
        for p, l in zip(labels, all_l):
            flux, error = _get_flux_from_log(l)
            data.append({
                "Dataset": d,
                "Position": p,
                "Flux (mJy)": flux,
                "Error (mJy)": error
            })

    df = pd.DataFrame(data)
    df.sort_values(by=['Dataset', 'Position'], inplace=True)
    print(df.to_string(index=False))

    # Plotting provided by ChatGPT, because plotting is hard.

    if not df.empty:
        baseline_group = datasets[0]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

        # --- Left: Flux vs Position ---
        ax = axes[0]
        for dataset, group in df.groupby("Dataset"):
            ax.errorbar(group["Position"], group["Flux (mJy)"], yerr=group["Error (mJy)"],
                        fmt='o-', capsize=4, label=dataset)
        ax.set_xlabel("Position")
        ax.set_ylabel("Flux (mJy)")
        ax.set_title("Flux Comparison by Dataset and Position")
        ax.legend(title="Dataset")
        ax.tick_params(axis='x', rotation=45)

        # --- Right: Relative difference vs cconfig ---
        ax2 = axes[1]

        # Pivot to align positions across datasets
        pivot_flux = df.pivot_table(index="Position", columns="Dataset", values="Flux (mJy)", aggfunc="mean")
        pivot_err  = df.pivot_table(index="Position", columns="Dataset", values="Error (mJy)", aggfunc="mean")

        base = pivot_flux[baseline_group]
        base_err = pivot_err[baseline_group]

        for col in pivot_flux.columns:
            if col == baseline_group:
                continue
            grp = pivot_flux[col]
            grp_err = pivot_err[col]

            rel = (grp - base) / base * 100
            rel_err = 100 * np.sqrt((grp_err / grp)**2 + (base_err / base)**2) * (grp / base)

            ax2.errorbar(rel.index, rel.values, yerr=rel_err.values,
                        fmt='o-', capsize=4, label=col)

            ax2.axhline(0, linestyle="--", linewidth=1)
            ax2.set_xlabel("Position")
            ax2.set_ylabel("Relative to cconfig (%)")
            ax2.set_title('Relative Difference vs "cconfig"')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend(title="Dataset")
            plt.suptitle("Integrated Flux for point sources between datasets (5.5 arcsec diameter)")

            plt.tight_layout()
            plt.show()
            plt.savefig("flux_comparison.png", dpi=300)
    else:
        print("No matching log files found.")
