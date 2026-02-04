mynterms = 2
OUTPUT_DIR = 'masked_models'
os.makedirs(OUTPUT_DIR, exist_ok=True)

model_list = ["cconfig-p5_agn", "dconfig1-p5_agn", "dconfig2-p5_agn"]

crtf = "circle[[17h20m10.03s, 26d37m31.9s], 15arcsec]"

for model in model_list:
    full_models = [f'{model}.model.tt{i}' for i in range(mynterms)]
    new_models = [f'{OUTPUT_DIR}/{m}' for m in full_models]
    for o, m in zip(full_models, new_models):
        os.system(f'cp -r {o} {m}')
        ia.open(m)
        reg = rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord())
        inv_reg = rg.complement(reg)
        ia.set(0.0, region=inv_reg)
        # ia.set(1.0, region=reg)
        ia.close()
        print(f"Done {m}")
