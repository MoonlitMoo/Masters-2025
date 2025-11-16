from casatasks import tclean

datasets = ['cconfig-p5', 'dconfig1-p5', 'dconfig2-p5']
OUTPUT_DIR = "head_tail_models2"

# Create the individual models
for ms in datasets:
    tclean(vis=f"{ms}.ms",
        imagename=f'{OUTPUT_DIR}/{ms}',
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=20000, gain=0.1,
        deconvolver='mtmfs', pblimit=-1.e-6,
        threshold='0.012mJy', scales=[0, 2, 4, 8],
        stokes='I', weighting='briggs', robust=0.5, pbcor=False,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False
    )

# Create the custom models
nterms = 2
base_model = "image-p5"
MODEL_DIR = "custom_models2"
head_tail_region = "ellipse[[4h13m36.61s, 10d28m23.96s], [20arcsec, 40arcsec], 30deg]"

if os.path.exists(MODEL_DIR):
    os.system(f'rm -r {MODEL_DIR}')
os.makedirs(MODEL_DIR)

for ms in datasets:
    base_models = [f'{base_model}.model.tt{i}' for i in range(nterms)]
    fitted_models = [f'{OUTPUT_DIR}/{ms}.model.tt{i}' for i in range(nterms)]
    new_models = [f'{MODEL_DIR}/{ms}.model.tt{i}' for i in range(nterms)]

    for b, f, n in zip(base_models, fitted_models, new_models):
        # Copy base model
        os.system(f'cp -r {b} {n}')
        # Open the new model and insert the fitted region
        ia.open(n)
        ia.insert(infile=f, region=head_tail_region)
        ia.close()

# Apply model to the datasets
for ms in datasets:
    models = [f'{MODEL_DIR}/{ms}.model.tt{i}' for i in range(nterms)]
    ft(vis=f'{ms}.ms', nterms=nterms, model=models, usescratch=True)
