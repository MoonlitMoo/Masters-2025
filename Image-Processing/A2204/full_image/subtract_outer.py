import numpy as np

MASK_DIR = "outlier_model"
nterms = 2
models = [f"image-p3.model.tt{i}" for i in range(nterms)]

if os.path.exists(MASK_DIR):
    os.system(f"rm -r {MASK_DIR}")
os.makedirs(MASK_DIR)

# Create the mask for outer points.
for m in models:
    os.system(f"cp -r {m} {MASK_DIR}/{m}")
    ia.open(f"{MASK_DIR}/{m}")
    pix = np.squeeze(ia.getchunk())
    # Want 8' centre, which is 4' radius = 4*60*2 = 480 cells radius
    radius = 480
    size = pix.shape[0]
    border = int(size/2 - radius)
    pix[border:-border, border:-border] = 0
    ia.putchunk(pix)
    ia.close()

# Set and subtract new model
new_models = [f"{MASK_DIR}/image-p3.model.tt{i}" for i in range(nterms)]
datasets = ["cconfig-p3.ms", "dconfig1-p3.ms", "dconfig2-p3.ms"]

for d in datasets:
    clearcal(d)
    ft(vis=d, nterms=nterms, model=new_models, usescratch=True)
    uvsub(d)
    split(d, outputvis=f'{d[:-4]}4.ms', datacolumn='corrected')
