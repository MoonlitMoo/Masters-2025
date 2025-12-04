from casatasks import tclean

datasets = ['cconfig-p3', 'dconfig1-p3', 'dconfig2-p3']
OUTPUT_DIR = "calibration4"
full_model = "image-p3"

# Create the full model
os.system(f'rm -r {full_model}.*')

tclean(vis=[f"{d}.ms" for d in datasets],
       imagename=full_model,
       imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
       specmode='mfs', niter=20000, gain=0.1,
       deconvolver='mtmfs', pblimit=-1.e-6,
       threshold='0.02mJy', scales=[0, 2, 4, 8],
       stokes='I', weighting='briggs', robust=0.5, pbcor=False,
       usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
       lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
)

# Create the individual models
for ms in datasets:
    os.system(f'rm -r {OUTPUT_DIR}/{ms}.*')
    tclean(vis=f"{ms}.ms",
        imagename=f'{OUTPUT_DIR}/{ms}',
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=20000, gain=0.1,
        deconvolver='mtmfs', pblimit=-1.e-6,
        threshold='0.02mJy', scales=[0, 2, 4, 8],
        stokes='I', weighting='briggs', robust=0.5, pbcor=False,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
    )


# Create the custom models
nterms = 2
MODEL_DIR = "calibration4/models"
# Quasar region S of minihalo
variable_region = "circle[[14h57m10.80s, 22d18m44.71s], 5arcsec]"

if os.path.exists(MODEL_DIR):
    os.system(f'rm -r {MODEL_DIR}')
os.makedirs(MODEL_DIR)

for ms in datasets:
    base_models = [f'{full_model}.model.tt{i}' for i in range(nterms)]
    fitted_models = [f'{OUTPUT_DIR}/{ms}.model.tt{i}' for i in range(nterms)]
    new_models = [f'{MODEL_DIR}/{ms}.model.tt{i}' for i in range(nterms)]

    for b, f, n in zip(base_models, fitted_models, new_models):
        # Copy base model
        os.system(f'cp -r {b} {n}')
        # Open the new model and insert the fitted region
        ia.open(n)
        ia.insert(infile=f, region=variable_region)
        ia.close()

# Apply model to the datasets
for ms in datasets:
    models = [f'{MODEL_DIR}/{ms}.model.tt{i}' for i in range(nterms)]
    ft(vis=f'{ms}.ms', nterms=nterms, model=models, usescratch=True)
