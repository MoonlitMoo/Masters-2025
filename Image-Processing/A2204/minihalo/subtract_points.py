import os

FULL_IMAGE_DIR = "check_flux/full_image"
IMAGE_DIR = "check_flux/images"
OUTPUT_DIR = "check_flux/masked_models"
nterms = 2
datasets = ["cconfig", "dconfig1", "dconfig2"]
regions = ["circle[[16h32m46.94s, 5d34m32.5s], 5arcsec]"]

# Clean up
if os.path.exists(OUTPUT_DIR):
    os.system(f'rm -r {OUTPUT_DIR}')
os.makedirs(OUTPUT_DIR)
os.system("rm -r *_uvsub.ms")

# Get the joint model and base flux scales
full_models = [f"{FULL_IMAGE_DIR}/image.model.tt{i}" for i in range(nterms)]
point_fluxes = []
for d in datasets:
    

# Create and apply scaled models
for d, flux in zip(datasets, point_fluxes):
    scaled_models = [f"{OUTPUT_DIR}/{d}_scaled.model.tt{i}" for i in range(nterms)]
    # Get full scale in mJy
    res = imfit(f"{IMAGE_DIR}/{d}_checkflux.image.tt0", region=agn_region, logfile=f"{OUTPUT_DIR}/fu$
    base_scale = res["results"]["component0"]["flux"]["value"][0]
    if res["results"]["component0"]["flux"]["unit"] == "Jy":
        base_scale *= 1000
    
    # Make the scaled model
    for o, s in zip(full_models, scaled_models):
        os.system(f'cp -r {o} {s}')
        # Get model AGN flux
        ia.open(s)
        reg = rg.fromtext(agn_region, shape=ia.shape(), csys=ia.coordsys().torecord())
        ind_agn = ia.getregion(reg)
        ind_agn *= flux / base_scale
        ia.putregion(ind_agn, region=agn_region)
        ia.close()
    
    # Apply, subtract, split
    clearcal(f'{d}.ms')
    ft(vis=f'{d}.ms', nterms=nterms, model=scaled_models, usescratch=True)
    uvsub(f'{ms}.ms')
    split(f'{ms}.ms', outputvis=f'{ms}_uvsub.ms', datacolumn='corrected')
