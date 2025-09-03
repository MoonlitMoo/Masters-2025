mynterms = 2
backup_dir = 'unmasked_models'
os.makedirs(backup_dir, exist_ok=True)

model_list = ["cconfig-p5_agn", "dconfig1-p5_agn", "dconfig2-p5_agn"]
mask_list = ['agn2.mask', 'agn.mask', 'agn.mask']

for model, mask in zip(model_list, mask_list):
    ia.open(mask)
    mpix=ia.getchunk().astype(bool)
    ia.done()

    new_model=[f'{model}.model.tt{i}' for i in range(mynterms)]
    for i in range(mynterms):
        if os.path.exists(f'{backup_dir}/{new_model[i]}'):
            print(f"Warning: Backup file exists for {new_model[i]}, skipping.")
            continue
        os.system(f'cp -r {new_model[i]} {backup_dir}/')
        ia.open(new_model[i])
        pix=ia.getchunk()
        pix[~mpix] = 0.
        ia.putchunk(pix)
        ia.done()
        print(f"Done {new_model[i]}")
