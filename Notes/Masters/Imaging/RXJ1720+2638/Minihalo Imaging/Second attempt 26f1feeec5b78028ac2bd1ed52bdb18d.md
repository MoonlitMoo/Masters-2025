# Second attempt

This one has some issues with the data containing RFI

Using agn test script to find a good uvrange cut. 

The models look like a single point with crap around it. Checking magnitude it tends to be ~scale of noise (1 uJy). Probably could have been fixed by removing scales.

## Investigating uvrange cutoffs vs AGN flux fits

The following was done using code found here https://github.com/MoonlitMoo/Masters-2025/blob/aec121185e69535e9fb4f1eff151facad9d521e2/Image-Processing/RXJ1720.1%2B2638/minihalo/uvrange_test.py. 

![uvcutoff_vs_flux.png](Second%20attempt/uvcutoff_vs_flux.png)

Curious uptick as dconfig is resolved/selected out, potentially variation due to the 1 year time between observations. Investigating individual observations next to see trends. 

![uvcutoff_vs_flux.png](Second%20attempt/uvcutoff_vs_flux%201.png)

Can clearly see the dconfig has minihalo flux until it flattens ~14 klambda. 15 and 20 klambda have weird fits for dconfig, while 25 and 30 fits failed. There is minimal/within uncertainty fits for the two dconfig, and tends to be about 15% higher than the cconfig data. 

## Extra comparisons

Selecting dconfig region around point source and comparing the flux density measurements.

![flux_comparison.png](Second%20attempt/flux_comparison.png)

# Component AGN tests

## Subtract AGN model

Setting AGN model with uvrange `>14klambda` per testing. Operating per dataset since cconfig seems to be lower than dconfig.

```python
uvrange = ">14klambda"
for dataset in ["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"]:
	imagename = f"agn_images/{dataset.split('.')[0]}_agn"
	tclean(vis=dataset,
    imagename=imagename,
    imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
    specmode='mfs', niter=10000, gain=0.1, threshold='0.018mJy',
    deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
    stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
    usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
    lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
    uvrange=uvrange)
```

Apparently said model despises being applied via tclean so will be using a point source component as the model. Using the integrated flux value, all fits were <beam size and categorised as a point source.

```python
imfit(imagename='agn_images/cconfig-p5_agn.image.tt0')
cl.addcomponent(flux=1.131, fluxunit='mJy',shape='point', dir='J2000 17:20:10.036 26.37.32.10')
cl.rename("cconfig.cl")
cl.close()
ft(vis='cconfig-p5.ms', complist='cconfig.cl', usescratch=True)
uvsub('cconfig-p5.ms')
split('cconfig-p5.ms', outputvis='cconfig_uvsub.ms', datacolumn='corrected')

```

```python
imfit(imagename='agn_images/dconfig1-p5_agn.image.tt0')
cl.addcomponent(flux=1.262, fluxunit='mJy',shape='point', dir='J2000 17:20:10.031 26.37.32.17')
cl.rename("dconfig1.cl")
cl.close()
ft(vis='dconfig1-p5.ms', complist='dconfig1.cl', usescratch=True)
uvsub('dconfig1-p5.ms')
split('dconfig1-p5.ms', outputvis='dconfig1_uvsub.ms', datacolumn='corrected')
```

```python
imfit(imagename='agn_images/dconfig2-p5_agn.image.tt0')
cl.addcomponent(flux=1.281, fluxunit='mJy',shape='point', dir='J2000 17:20:10.029 26.37.32.24')
cl.rename("dconfig2.cl")
cl.close()
ft(vis='dconfig2-p5.ms', complist='dconfig2.cl', usescratch=True)
uvsub('dconfig2-p5.ms')
split('dconfig2-p5.ms', outputvis='dconfig2_uvsub.ms', datacolumn='corrected')
```

## Imaging minihalo

Testing the resulting image and we get an RMS of 5.5 uJy. Using automasking to clean to 15 uJy, to check image quality.

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='image-minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='image-minihalo-r0.5',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

- There is a hole where agn was, unsure if this is a subset of the ms, or common to all
- Bad negative where agn was, leading to imaging artefacts.

# Using model image

We need to apply the model from the agn imaging to the ms, but only in the region of the AGN. To do this we create a region mask in CARTA and save it as `agn_region.rtf` which contains only the AGN. Then we turn it into an actual mask. Note that I made a region from the dconfig and the cconfig and then two masks, since they they hated being applied between configs for some reason. 

```python
makemask(mode='copy', inpimage='dconfig1-p5_agn.model.tt0', 
	inpmask='agn_region.rtf', output='agn.mask', overwrite=True)
```

Then we multiply this to the existing masks to get the clean ones

```python
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
```

Write into the model column for the ms, don’t use tclean since it hates doing it for some reason

```python
datasets = ["cconfig-p5", "dconfig1-p5", "dconfig2-p5"]
for ms in datasets:
	ft(vis=f'{ms}.ms', nterms=2, 
	model=[f'agn_images/{ms}_agn.model.tt0', f'agn_images/{ms}_agn.model.tt1'], 
	usescratch=True)
```

Subtract and split off 

```python
uvsub('cconfig-p5.ms')
split('cconfig-p5.ms', outputvis='cconfig_uvsub.ms', datacolumn='corrected')
uvsub('dconfig1-p5.ms')
split('dconfig1-p5.ms', outputvis='dconfig1_uvsub.ms', datacolumn='corrected')
uvsub('dconfig2-p5.ms')
split('dconfig2-p5.ms', outputvis='dconfig2_uvsub.ms', datacolumn='corrected')
```

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='image-minihalo-r1.5',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

## Testing small scale bias and robust

Did a small grid search over robust and small scale bias

- smallscalebias = [-0.5, 0, 0.5]
- robust = [0.5, 1, 1.5, 2]

As robust increases, so does noise in surrounding regions. On the other hand, sensitivity is increasing. A robust of 1 seems to be an ok middle ground, but still not perfect.

The best models are for smallscalebias of -0.5, 0. This biases towards the larger scales which makes sense for the minihalo. There are few point-like noise parts in the model.

Best to then try out a deeper interactive clean for the r=1, ssb=-0.5 set. RMS is 4.7 uJy, setting clean depth for centre to 10 uJy.

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='minihalo_r=1_ssb=-0.5',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='10uJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=-0.5,
	stokes='I', weighting='briggs', robust=1, pbcor=False,
	interactive=True)
```

## Calculating flux with 3 sigma contour

To  do this automatically, we can do the following

1. Use imstat to get the sigma
2. Open the image we want to calculate the flux for. 
3. Feed the image data and 3 sigma into a contour making function to get a mask. Select the largest region (which should be the minihalo, if not we can add a seed value).
4. Save a new image which masks using the contour.
5. Use imstat to get the flux.

## Results for grid search

![flux_comparison.png](Second%20attempt/flux_comparison%201.png)

Neat to really see how the robust values impact the noise level. 

- Small scale bias increases flux as we bias towards small scale, but only by about 1-2%.
- Robust increases flux as we bias towards natural weighting + sensitivity by up to 30%, but mostly ~25%.
- Robust increases sigma as we bias towards natural weighting + sensitivity by up to 30%, but mostly ~40%.

## Results for interactively cleaned image

Flux: 7.32 mJy

Sigma: 6.04e-06 uJy

This has slightly lower values than the original image (7.79 mJy and 6.06 uJy, respectively)

# Looking at another selfcalibration

Applying model from non-interactive cleaned version. Doing via `ft` since I still don’t trust `tclean`.

```python
datasets = ["cconfig", "dconfig1", "dconfig2"]
for ms in datasets:
	ft(vis=f'{ms}_uvsub.ms', nterms=2, 
	model=['grid_search/minihalo_r=1_ssb=-0.5.model.tt0', 'grid_search/minihalo_r=1_ssb=-0.5.model.tt1'], 
	usescratch=True)
```

Self calibrate and split

```python
gaincal(vis="cconfig_uvsub.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
gaincal(vis="dconfig1_uvsub.ms", caltable=f'dconfig1.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
gaincal(vis="dconfig2_uvsub.ms", caltable=f'dconfig2.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
```

```python
applycal(vis="dconfig2_uvsub.ms", gaintable=['dconfig2.p0'])
split(vis=f'dconfig2_uvsub.ms', outputvis=f'dconfig2_uvsub-p0.ms', 
	datacolumn='corrected')
applycal(vis="dconfig1_uvsub.ms", gaintable=['dconfig1.p0'])
split(vis=f'dconfig1_uvsub.ms', outputvis=f'dconfig1_uvsub-p0.ms', 
	datacolumn='corrected')
applycal(vis="cconfig_uvsub.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig_uvsub.ms', outputvis=f'cconfig_uvsub-p0.ms', 
	datacolumn='corrected')
```

Missing spw 10, 22~31 from solutions.

```python
tclean(vis=["cconfig_uvsub-p0.ms", "dconfig1_uvsub-p0.ms", "dconfig2_uvsub-p0.ms"], 
	imagename='minihalo_r=1_ssb=-0.5-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='10uJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=-0.5,
	stokes='I', weighting='briggs', robust=1, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

The image has higher RMS and the solution looks worse than the not corrected version.