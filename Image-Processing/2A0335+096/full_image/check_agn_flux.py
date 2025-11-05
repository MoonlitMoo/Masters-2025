import os
import re
from typing import List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from casatasks import imfit, imstat


def get_log_results(log_dict: dict):
    """ Pulls the integrated or peak flux from the log depending on if it was point-like or not.

    Returns
    -------
    value : float
        Flux in Jy
    err : float
        Flux err in Jy
    is_point : bool
        If fit was point-like
    """
    res = log_dict['deconvolved']["component0"]
    is_point = True  #res["ispoint"]
    if is_point:
        return res["flux"]["value"][0], res["flux"]["error"][0], is_point
    else:
        return res["peak"]["value"], res["peak"]["error"], is_point


def compare_point_fluxes(datasets: List[str], regions: List[str], labels: List[str],
                         uvrange=">12klambda", output_dir: str = "point_flux_output"):
    """ Creates uvcut images of each dataset, then fits a gaussian within each region to calculate the flux.
    Returns the peak and integrated flux of each object, alongside a plot comparing the differences.

    Parameters
    ----------
    datasets : list of str
        The datasets to use for comparison
    regions : list of str
        The CRTF for each region we want to fit within
    labels : list of str
        The labels associated with the regions
    uvrange : str, default=">12klambda"
        The cutoff for making point images
    output_dir : str, default=point_flux_output
        Where to output logs and images
    """
    os.makedirs(output_dir, exist_ok=True)
    datasets = [f"{d}.ms" for d in datasets if ".ms" not in d]
    images = [f"{output_dir}/{d.split('.ms')[0]}_point" for d in datasets]

    # --- Make images ---
    for d, i in zip(datasets, images):
        tclean(vis=d, imagename=i,
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=10000, gain=0.1, threshold='0.025mJy',
        deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
        stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
        uvrange=uvrange)

    # --- Fit the fluxes ---
    data = []
    for d, image in zip(datasets, images):
        image_name = f"{image}.image.tt0"
        for region, label in zip(regions, labels):
            fit = imfit(image_name, region=region, logfile=f"{image}.log", append=False)
            res = get_log_results(fit)
            data.append({
                "Dataset": d,
                "Label": label,
                "Flux (mJy)": res[0] * 1000,
                "Error (mJy)": res[1] * 1000,
                "is_point": res[2],
            })
    # Format data
    df = pd.DataFrame(data)
    df.sort_values(by=['Dataset', 'Label'], inplace=True)
    if not sum(df["is_point"]) == len(df["is_point"]) or sum(df["is_point"]) == 0:
        print(f"Not all fits are point/non-point")

    print(df.to_string(index=False))
    if df.empty:
        return

    # --- Plotting ---
    baseline_group = datasets[0]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    # --- Left: Flux vs Position ---
    ax = axes[0]
    for dataset, group in df.groupby("Dataset"):
        ax.errorbar(group["Label"], group["Flux (mJy)"], yerr=group["Error (mJy)"],
                    fmt='o-', capsize=4, label=dataset)
    ax.set_xlabel("Position")
    ax.set_ylabel("Flux (mJy)")
    ax.set_title("Flux Comparison by Dataset and Region")
    ax.legend(title="Dataset")
    ax.tick_params(axis='x', rotation=45)

    # --- Right: Relative difference vs cconfig ---
    ax2 = axes[1]

    # Pivot to align positions across datasets
    pivot_flux = df.pivot_table(index="Label", columns="Dataset", values="Flux (mJy)", aggfunc="mean")
    pivot_err  = df.pivot_table(index="Label", columns="Dataset", values="Error (mJy)", aggfunc="mean")

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
        ax2.set_ylabel(f"Relative to {baseline_group} (%)")
        ax2.set_title(f'Relative Difference vs {baseline_group}')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(title="Dataset")
        plt.suptitle(f"{'Peak' if all(df['is_point']) else 'Integrated'} Flux for point sources between datasets")

        plt.tight_layout()
        plt.show()
        plt.savefig(f"{output_dir}/comparison.png", dpi=300)


datasets = ["cconfig-p3", "dconfig1-p3", "dconfig2-p3"]
labels = ["agn"]
regions = ["circle[[3h38m40.57s, 9d58m11.95s], 5.5arcsec]"]

compare_point_fluxes(datasets, regions, labels)
