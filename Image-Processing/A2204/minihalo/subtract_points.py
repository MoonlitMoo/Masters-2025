IMAGE_DIR = "check_flux/images"
OUTPUT_DIR = "check_flux/masked_models"
nterms = 2
datasets = ["cconfig", "dconfig1", "dconfig2"]

regions = ["circle[[16h32m46.94s, 5d34m33.9s], 5arcsec]"]
cc_region = ["circle[[16h32m45.90s, 5d34m55.27s], 2arcsec]"]

if os.path.exists(OUTPUT_DIR):
    os.system(f'rm -r {OUTPUT_DIR}')
os.makedirs(OUTPUT_DIR)

for ms in datasets:
    original_models = [f'{IMAGE_DIR}/{ms}_checkflux.model.tt{i}' for i in range(nterms)]
    masked_models = [f'{OUTPUT_DIR}/{ms}_checkflux.model.tt{i}' for i in range(nterms)]
    for o, m in zip(original_models, masked_models):
        os.system(f'cp -r {o} {m}')
        ia.open(m)
        if ms == "cconfig":
            regs = {i: rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord()) for i, crtf in enumerate(regions + cc_region)}
            reg = rg.makeunion(regs) if len(regs) > 1 else regs[regs]
        else:
            reg = rg.fromtext(regions[0], shape=ia.shape(), csys=ia.coordsys().torecord())
        inv_reg = rg.complement(reg)
        ia.set(0.0, region=inv_reg)
        ia.close()

os.system(f'rm -r *_uvsub.ms')

for ms in datasets:
    clearcal(f'{ms}.ms')
    ft(vis=f'{ms}.ms', nterms=nterms,
       model=[f'{OUTPUT_DIR}/{ms}_checkflux.model.tt{i}' for i in range(nterms)],
       usescratch=True)
    uvsub(f'{ms}.ms')
    split(f'{ms}.ms', outputvis=f'{ms}_uvsub.ms', datacolumn='corrected')
