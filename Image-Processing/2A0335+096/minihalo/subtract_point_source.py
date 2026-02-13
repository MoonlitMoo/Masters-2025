import os

IMAGE_DIR = "check_flux/images"
OUTPUT_DIR = "check_flux/masked_models"
nterms = 2
datasets = ["cconfig", "dconfig1", "dconfig2"]

regions = ["circle[[3h38m41.4s, 9d58m17.5s], 4arcsec]",
    "circle[[3h38m40.6s, 9d58m11.6s], 4arcsec]",
    "circle[[3h38m39.9s, 9d58m07.3s], 4arcsec]",
    "circle[[3h38m40.3s, 9d58m17.9s], 4arcsec]"
]

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
        if len(regs) > 1:
	        reg = rg.makeunion(regs)
        else:
	        reg = regs[0]
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
