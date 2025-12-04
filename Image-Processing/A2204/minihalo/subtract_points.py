IMAGE_DIR = "check_flux"
OUTPUT_DIR = "check_flux/scaled_models"
nterms = 2
datasets = ["cconfig", "dconfig1", "dconfig2"]

agn_region = "circle[[16h32m46.95s, 5d34m32.6s], 2arcsec]"
s2_region = "circle[[16h32m46.97s, 5d34m40.8s], 2arcsec]"

if os.path.exists(OUTPUT_DIR):
    os.system(f'rm -r {OUTPUT_DIR}')
os.makedirs(OUTPUT_DIR)

# Get the full model, then grab a fit for the AGN
base_models = [f'{IMAGE_DIR}/full_image/image.model.tt{i}' for i in range(nterms)]
res = imfit(f'{IMAGE_DIR}/full_image/image.image.tt0', region=agn_region, logfile=f"{OUTPUT_DIR}/full_agn.log", append=False)
base_flux = res['results']['component0']['flux']['value'][0]
base_unit = res['results']['component0']['flux']['unit']
print(f"Full model integrated flux: {base_flux:1.2e} {base_unit}")

# Iterate through individual models to get the AGN flux
for ms in datasets:
    # Get the scaling factor
    image_file = f'{IMAGE_DIR}/images/{ms}_checkflux.image.tt0'
    res = imfit(image_file, region=agn_region, logfile=f"{OUTPUT_DIR}/{ms}_agn.log", append=False)
    flux = res['results']['component0']['flux']['value'][0]
    unit = res['results']['component0']['flux']['unit']
    scaling_factor = flux / base_flux
    print(f"{ms} model integrated flux: {flux:1.2e} {unit}, scale of {scaling_factor:.2f}")

    # Copy over the models, scale and select
    scaled_models = [f'{OUTPUT_DIR}/{ms}.model.tt{i}' for i in range(nterms)]
    for bm, sm in zip(base_models, scaled_models):
        os.system(f'cp -r {bm} {sm}')
        ia.open(sm)
        agn_rgn = rg.fromtext(agn_region, shape=ia.shape(), csys=ia.coordsys().torecord())
        # Scale the AGN
        agn_pix = ia.getregion(region=agn_rgn)
        agn_pix *= scaling_factor
        ia.putregion(pixels=agn_pix, region=agn_rgn)
        # Mask for AGN + S2
        s2_rgn = rg.fromtext(s2_region, shape=ia.shape(), csys=ia.coordsys().torecord())
        full_rgn = rg.makeunion({0: agn_rgn, 1: s2_rgn})
        inv_reg = rg.complement(full_rgn)
        ia.set(0.0, region=inv_reg)
        ia.close()


# Create the subtracted models
os.system(f'rm -r *_uvsub.ms')
for ms in datasets:
    clearcal(f'{ms}.ms')
    ft(vis=f'{ms}.ms', nterms=nterms, model=[f'{OUTPUT_DIR}/{ms}.model.tt{i}' for i in range(nterms)], usescratch=True)
    uvsub(f'{ms}.ms')
    split(f'{ms}.ms', outputvis=f'{ms}_uvsub.ms', datacolumn='corrected')
