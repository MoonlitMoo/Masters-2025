# First model the right galaxy with uvcut and negative robust
OUTPUT_DIR = "right_image"
MASK_DIR = 'masked_models'

data_list = ["cconfig_uvsub", "dconfig1_uvsub", "dconfig2_uvsub"]
uvrange = ">12klambda"

# Clean up previous runs
os.system(f"rm -r {OUTPUT_DIR}/*")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/{MASK_DIR}", exist_ok=True)

for dataset in data_list:
	imagename = f"{OUTPUT_DIR}/{dataset}"
	tclean(
        vis=f"{dataset}.ms",
        imagename=imagename,
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=10000, gain=0.1, threshold='0.02mJy',
        deconvolver='mtmfs', pblimit=-1.e-6,
        scales=[0, 4, 8, 16, 32], smallscalebias=0.5,
        stokes='I', weighting='briggs', robust=-0.5, pbcor=False, uvrange=uvrange,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False
    )

# Then mask the models to the point
crtf = "circle[[17h20m1.17s, 26d36m32.99s], 7.5arcsec]"
mynterms = 2

for dataset in data_list:
    full_models = [f'{OUTPUT_DIR}/{dataset}.model.tt{i}' for i in range(mynterms)]
    new_models = [f'{OUTPUT_DIR}/{MASK_DIR}/{os.path.basename(m)}' for m in full_models]
    for o, m in zip(full_models, new_models):
        os.system(f'cp -r {o} {m}')
        ia.open(m)
        reg = rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord())
        inv_reg = rg.complement(reg)
        ia.set(0.0, region=inv_reg)
        ia.close()

# Then apply the model to the dataset, subtract, and split
# Final dataset is X_final.ms
for ms in data_list:
	ft(vis=f'{ms}.ms', nterms=mynterms,
	model=[f'{OUTPUT_DIR}/{MASK_DIR}/{ms}.model.tt{i}' for i in range(mynterms)],
	usescratch=True)
	uvsub(f'{ms}.ms')
	split(f'{ms}.ms', outputvis=f'{ms.split("_")[0]}_final.ms', datacolumn='corrected')
	uvsub(f'{ms}.ms', reverse=True)
