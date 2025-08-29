import matplotlib.pyplot as plt
from casatasks import tclean, imfit, impbcor, imhead

OUTPUT_DIR = "uvrange_config_tests"
PLOT_PATH = f"{OUTPUT_DIR}/uvcutoff_vs_flux.png"
DATASETS = ["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"]

def run_clean(dataset: str, imagename: str, uvrange: str):
    """ Run tclean to fit the AGN model.
    Uses uvrange to cut diffuse structure, uniform weighting (robust -2). Scales are kept small as AGN shouldn't be resolved.
    Does automasking, thought not really required.

    Parameters
    ----------
    imagename : str
        Name to use for the image.
    uvrange : str
        The string version for the uvrange to use for the cleaning.
    """
    tclean(vis=dataset,
        imagename=imagename,
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=10000, gain=0.1, threshold='0.018mJy',
        deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
        stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
        uvrange=uvrange)


# In klambda
# uv_cutoffs = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
uv_cutoffs = [0, 5, 10, 15, 20, 25, 30]
logs = []
for data in DATASETS:
    logset = []
    for u in uv_cutoffs:
        uvrange = f">{u}klambda"
        test_str = f"{data.split('.')[0]}_range_{uvrange}"
        img_prefix = f"{OUTPUT_DIR}/{test_str}"
        log_path = f"{img_prefix}.log"

        logset.append(log_path)

        # Get the cleaned image
        if os.path.exists(f"{img_prefix}.image.tt0"):
            print(f"Skipping {uvrange} tclean as image exists")
        else:
            run_clean(data, img_prefix, uvrange)

        # Get the gaussian fit.
        if os.path.exists(log_path):
            print(f"Skipping {uvrange} imfit as log exists")
        else:
            imfit(f'{img_prefix}.image.tt0', logfile=log_path)
    logs.append(logset)


def read_log_value(l):
    values = l.split(":")[-1].split("mJy")[0].split("+/-")
    values = [float(v.strip()) for v in values]
    return values


# Plot the results
plt.figure()
for data_logset, data_name, c in zip(logs, DATASETS, ['C0', 'C1', 'C2']):
    # Pull the results for each configuration.
    peak_fluxes = []
    peak_flux_errors = []
    integrated_fluxes = []
    integrated_flux_errors = []

    for log in data_logset:
        with open(log, "r") as f:
            for l in f.readlines():
                if "Peak:" in l:
                    f, e = read_log_value(l)
                    peak_fluxes.append(f)
                    peak_flux_errors.append(e)
                elif "Integrated:" in l:
                    f, e = read_log_value(l)
                    integrated_fluxes.append(f)
                    integrated_flux_errors.append(e)

    plt.errorbar(uv_cutoffs, peak_fluxes, yerr=peak_flux_errors, fmt='o-', color=c, label=f"{data_name} Peak (mJy/beam)")
    plt.errorbar(uv_cutoffs, integrated_fluxes, yerr=integrated_flux_errors, fmt='s--', color=c, label=f"{data_name} Integrated (mJy)")

plt.xlabel("uv min cut (kλ)")
plt.ylabel("Flux density")
plt.title("RXJ1720+2638 AGN fit vs uv-range cut")
plt.grid(True, which='both', alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=300)
