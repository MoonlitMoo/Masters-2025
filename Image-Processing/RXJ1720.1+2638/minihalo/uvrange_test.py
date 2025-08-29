import matplotlib.pyplot as plt
from casatasks import tclean, imfit, impbcor, imhead

OUTPUT_DIR = "uvrange_tests"
PLOT_PATH = f"{OUTPUT_DIR}/uvcutoff_vs_flux.png"

def run_clean(imagename: str, uvrange: str):
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
    tclean(vis=["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"],
        imagename=imagename,
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=10000, gain=0.1, threshold='0.018mJy',
        deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
        stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
        uvrange=uvrange)


# In klambda
uv_cutoffs = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
logs = []

for u in uv_cutoffs:
    uvrange = f">{u}klambda"
    test_str = f"range_{uvrange}"
    img_prefix = f"{OUTPUT_DIR}/{test_str}"
    log_path = f"{img_prefix}.log"

    logs.append(log_path)

    # Get the cleaned image
    if os.path.exists(f"{img_prefix}.image.tt0"):
        print(f"Skipping {uvrange} tclean as image exists")
    else:
        run_clean(img_prefix, uvrange)

    # Get the gaussian fit, uses box around the AGN to make sure other sources don't interfere.
    if os.path.exists(log_path):
        print(f"Skipping {uvrange} imfit as log exists")
    else:
        imfit(f'{img_prefix}.image.tt0', logfile=log_path)

# Pull the results
peak_fluxes = []
peak_flux_errors = []
integrated_fluxes = []
integrated_flux_errors = []

def read_log_value(l):
    values = l.split(":")[-1].split("mJy")[0].split("+/-")
    values = [float(v.strip()) for v in values]
    return values

for log in logs:
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

# Plot the results
plt.figure()
plt.errorbar(uv_cutoffs, peak_fluxes, yerr=peak_flux_errors, fmt='o-', label="Peak (mJy/beam)")
plt.errorbar(uv_cutoffs, integrated_fluxes, yerr=integrated_flux_errors, fmt='s--', label="Integrated (mJy)")
plt.xlabel("uv min cut (kλ)")
plt.ylabel("Flux density")
plt.title("RXJ1720+2638 AGN fit vs uv-range cut")
plt.grid(True, which='both', alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=300)
