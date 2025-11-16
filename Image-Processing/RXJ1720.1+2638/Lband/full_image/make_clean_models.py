nterms = 3
outliers = ["outlier1_sc2_ms_am_br0start", "outlier2_sc2_ms_am_br0start"]

in_ms = "G049.20+30.86_sc2.ms"
out_ms = "G049.20+30.86_sc2_sub.ms"
clearcal(in_ms)
os.system(f'rm -r {out_ms}')


# Remove the outlier field points
split(in_ms, outputvis=out_ms, datacolumn='corrected')
for o in outliers:
	models = [f'{o}.model.tt{i}' for i in range(nterms)]
	ft(vis=out_ms, nterms=nterms, model=models, usescratch=True)
	uvsub(out_ms)
	split(out_ms, outputvis=f'{out_ms}_temp', datacolumn='corrected')
	os.system(f'rm -r {out_ms}')
	os.system(f'mv {out_ms}_temp {out_ms}')

# Remove the outer image points
OUTPUT_DIR = 'masked_models'
os.system(f'rm -r {OUTPUT_DIR}')
os.makedirs(OUTPUT_DIR, exist_ok=True)
crtf = "centerbox[[17h20m07.73s, 26d36m49.91s], [12.5arcmin, 12.5arcmin]]"

full_models = [f'image.model.tt{i}' for i in range(nterms)]
masked_models = [f'{OUTPUT_DIR}/{m}' for m in full_models]
for o, m in zip(full_models, masked_models):
    os.system(f'cp -r {o} {m}')
    ia.open(m)
    reg = rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord())
    ia.set(0.0, region=reg)
    ia.close()

ft(vis=ms, nterms=nterms, model=masked_models, usescratch=True)
uvsub(out_ms)
split(ms, outputvis=f'{out_ms}_temp', datacolumn='corrected')
os.system(f'rm -r {out_ms}')
os.system(f'mv {out_ms}_temp {out_ms}')
