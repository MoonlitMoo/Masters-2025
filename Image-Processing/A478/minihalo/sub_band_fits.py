import os
from casatasks import split, flagdata

def create_subbands(dataset: str, n_subbands: int, output_dir: str):
    msmd.open(dataset)
    n_spw = msmd.nspw()
    msmd.done()

    # Check if non-divisible
    if n_spw % n_subbands:
        print(f"Given number of sub-bands ({n_subbands}) cannot be evenly distributed for the found {n_spw} spectral windows")
        return []

    band_dirs = []
    # Create sub-bands
    spw_per_band = int(n_spw / n_subbands)
    for i in range(n_subbands):
        min_spw, max_spw = spw_per_band * i, spw_per_band * (i + 1) - 1
        band_dir = f"{output_dir}/spw{min_spw}-{max_spw}"
        band_dirs.append(band_dir)
        os.makedirs(band_dir, exist_ok=True)
        ms_path = f"{band_dir}/{dataset}"
        if os.path.exists(ms_path):
            os.system(f"rm -r {ms_path}")
        split(dataset, outputvis=ms_path, spw=f"{min_spw}~{max_spw}", datacolumn='data')
        # Output checks for flagged amount
        assess_spws(ms_path)
    return band_dirs


OUTPUT_DIR = "subband_agn"
IMAGE_DIR = f"{OUTPUT_DIR}/images"
DATASETS = ["cconfig.ms", "dconfig1.ms", "dconfig2.ms"]

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Split the datasets
for d in DATASETS:
    create_subbands(d, 4, OUTPUT_DIR)


subbands = [f"{OUTPUT_DIR}/{d}" for d in os.listdir(OUTPUT_DIR) if "images" not in d]

# Image the chunks, reusing mask from full image. Increased threshold due to less image data.
for bd in subbands:
    band_datasets = [f"{bd}/{d}" for d in DATASETS]
    imagename = f"{IMAGE_DIR}/image_{bd.split('/')[-1]}"
    tclean(vis=band_datasets,
            imagename=imagename,
            imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
            specmode='mfs', niter=10000, gain=0.1, threshold='0.025mJy',
            deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
            stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
            usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
            lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
            uvrange=">12klambda")
