# L band

# Full image

Using the following settings, the majority of the images are cleaned quite well. There is a point to the top which has a lot of difficulty in being fit for whatever reason. Setting threshold to 50 uJy since RMS ~15 uJy (3x).

Worked really well with increased sidelobethreshold, testing to see if biasing smaller scales also helps with some of the negative impressions.

```python
tclean(vis='G049.20+30.86_sc2.ms', imagename='image', 
	imsize=[3600], cell=['1arcsec'], 
	gridder='wproject', wprojplanes=128, pblimit=-1e-6, niter=20000,
	deconvolver='mtmfs', nterms=3, weighting='briggs', robust=0.5, 
	scales=[0, 2, 4, 8, 16], smallscalebias=0.5, threshold='0.04mJy', 
	outlierfile='outliers_am_sc2.txt',
	usemask='auto-multithresh', pbmask=0, 
	sidelobethreshold=7, fastnoise=False
)
```

## Subtract outlier map points

Trying to subtract outlier points. Subtract, split to self (overwrite), subtract again.

```python
nterms = 3
outliers = ["outlier1_sc2_ms_am_br0start", "outlier2_sc2_ms_am_br0start**"**]
in_ms = "G049.20+30.86_sc2.ms"
out_ms = "G049.20+30.86_sc2_sub.ms"
clearcal(in_ms)
split(in_ms, outputvis=out_ms, datacolumn='corrected')
for o in outliers:
	models = [f'{o}.model.tt{i}' for i in range(nterms)]
	ft(vis=out_ms, nterms=nterms, model=models, usescratch=True)
	uvsub(out_ms)
	split(out_ms, outputvis=f'{out_ms}_temp', datacolumn='corrected')
	os.system(f'rm -r {out_ms}')
	os.system(f'mv {out_ms}_temp {out_ms}')
```

## Subtract image outer points

We open each of the models and select the area we want to image better via a region format. Then set the model to 0 in that area and save it. Following that, we apply the model to the dataset, subtract and split.

```python
nterms = 3
OUTPUT_DIR = 'masked_models'
os.makedirs(OUTPUT_DIR, exist_ok=True)
ms = "G049.20+30.86_sc2_sub.ms"
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
uvsub(ms)
split(ms, outputvis=f'{ms}_temp', datacolumn='corrected')
os.system(f'rm -r {ms}')
os.system(f'mv {ms}_temp {ms}')
```

## Checking subtracted image

```python
tclean(vis='G049.20+30.86_sc2.ms', imagename='image_subtracted', 
	imsize=[3600], cell=['1arcsec'], 
	gridder='wproject', wprojplanes=128, pblimit=-1e-6, niter=20000,
	deconvolver='mtmfs', nterms=3, weighting='briggs', robust=0.5, 
	scales=[0, 2, 4, 8, 16], smallscalebias=0.5, threshold='0.04mJy', 
	outlierfile='outliers_am_sc2.txt',
	usemask='auto-multithresh', pbmask=0, 
	sidelobethreshold=7, fastnoise=False
)
```

# Minihalo

Checking image.

```python
tclean(vis='G049.20+30.86_sc2_sub.ms', imagename='new_sub', 
	imsize=[1024], cell=['0.75arcsec'], 
	gridder='standard', pblimit=-1e-6, niter=20000,
	deconvolver='mtmfs', nterms=3, weighting='briggs', robust=0.5, 
	scales=[0, 2, 4, 8, 16], smallscalebias=0.5, threshold='0.04mJy', 
	usemask='auto-multithresh', pbmask=0, 
	sidelobethreshold=7, fastnoise=False
)
tclean(vis='sub_outer_br0p5.ms', imagename='old_sub', 
	imsize=[1024], cell=['0.75arcsec'], 
	gridder='standard', pblimit=-1e-6, niter=20000,
	deconvolver='mtmfs', nterms=3, weighting='briggs', robust=0.5, 
	scales=[0, 2, 4, 8, 16], smallscalebias=0.5, threshold='0.04mJy', 
	usemask='auto-multithresh', pbmask=0, 
	sidelobethreshold=7, fastnoise=False
)
```

# TO-DO

- Calculate flux same process for this one as X-band.
- Compare L-band 1.4 Ghz + X-band Shape of u-v graph.
- Compare uvrange of G14 to X-band.