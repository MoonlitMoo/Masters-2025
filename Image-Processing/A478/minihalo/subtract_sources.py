IMAGE_DIR = "check_flux/images"
OUTPUT_DIR = "check_flux/masked_models"
nterms = 2
datasets = ["cconfig", "dconfig1", "dconfig2"]

regions = ["circle[[4h13m38.37s, 10d28m08.54s], 1.25arcsec]",
           "circle[[4h13m25.28s, 10d27m54.5s], 5arcsec]"]

if os.path.exists(OUTPUT_DIR):
    os.system(f'rm -r {OUTPUT_DIR}')
os.makedirs(OUTPUT_DIR)

for ms in datasets:
    original_models = [f'{IMAGE_DIR}/{ms}_checkflux.model.tt{i}' for i in range(nterms)]
    masked_models = [f'{OUTPUT_DIR}/{ms}_checkflux.model.tt{i}' for i in range(nterms)]
    for o, m in zip(original_models, masked_models):
        os.system(f'cp -r {o} {m}')
        ia.open(m)
        regs = {i: rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord()) for i, crtf in enumerate(regions)}
        reg = rg.makeunion(regs)
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
