# Minihalo Imaging

[First attempt](Minihalo%20Imaging/First%20attempt%2025c1feeec5b780f6a0c9df801915badc.md)

[Second attempt](Minihalo%20Imaging/Second%20attempt%2026f1feeec5b78028ac2bd1ed52bdb18d.md)

Arcsec to kpc at z=0.160 using standard cosmology is ~2.8 kpc per 1“. Each cell is .5” so ~1.4 kpc. Beam resolution is ~1.8” which is 3.92 kpc. 

## Observation Data

- **cconfig** 3/2/2024
    - uvwave range  [0, 115000]
- **dconfig 1** 28/2/25
    - uvwave range [0, 35000]
- **dconfig 2** 27/3/25
    - uvwave range [0, 35000]

So 1 year between C and D configurations, 1 month between D configs.

## RFI fixes

Using the p5 self calibrated models from the `full_image` dataset, that was re-modelled and processed with `assess_spw`.

# Checking the config testing

This was done using almost the same dataset, slightly less flagged and slightly worse calibrated.

## Check where to uvcut

![uvcutoff_vs_flux.png](Minihalo%20Imaging/uvcutoff_vs_flux.png)

From this plot it seems like anything >10 klambda will give us what we want. No more weird variation as seen in the previous attempt, likely because the dataset is much cleaner. All of them also converge towards the same value, so separate fits/models probably aren’t necessary (but doing it anyway).

Weirdly the dconfig2 set is lower by ~10%, possibly just calibration error.

# Fit AGN model

Now using the final dataset, which is cleaned properly.

The uvrange cutoff set to a little after the flattening at 12 klambda. Residual noise was ~12 uJy after checking so the threshold 2x this with automasking should work well enough for a point source only image. 

```python
uvrange = ">12klambda"
for dataset in ["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"]:
	imagename = f"agn_images/{dataset.split('.')[0]}_agn"
	tclean(vis=dataset,
    imagename=imagename,
    imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
    specmode='mfs', niter=10000, gain=0.1, threshold='0.025mJy',
    deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 2, 4],
    stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
    usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
    lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
    uvrange=uvrange)
```

## Checking the flux modelling between sources

We want to make sure that there isn’t a significant systematic calibration error between the datasets. To do this we can then compare a few point sources between the datasets and their measured flux. There are three of them, the AGN itself, the head-tail galaxy, and whatever is down to the right of the AGN. 

The regions of these are given as following, also contained in `check_flux.py`.

```python
"circle[[17h20m10.03s, 26d37m31.9s], 5.5arcsec]"
"circle[[17h20m13.86s, 26d38m25.96s], 5.5arcsec]"
"circle[[17h20m01.16s, 26d36m33.3s], 2.75arcsec]"]
```

![flux_comparison.png](Minihalo%20Imaging/flux_comparison.png)

It looks like there is a somewhat consistent difference between the two dconfig measurements, not seen in the previous attempt. Uncertainties do mitigate this a little, but maybe a problem?

Masking models to AGN

Then we mask each model to only contain the AGN by using masking all model values outside the region defined by (done via `make_clean_models.py`)

```python
"circle[[17h20m10.03s, 26d37m31.9s], 15arcsec]"
```

Then we can just apply these models to the datasets and uvsubtract to remove the AGN.

```python
datasets = ["cconfig-p5", "dconfig1-p5", "dconfig2-p5"]
for ms in datasets:
	ft(vis=f'{ms}.ms', nterms=2, 
	model=[f'agn_images/masked_models/{ms}_agn.model.tt0', f'agn_images/{ms}_agn.model.tt1'], 
	usescratch=True)
	uvsub(f'{ms}.ms')
	split(f'{ms}.ms', outputvis=f'{ms.split("-")[0]}_uvsub.ms', datacolumn='corrected')
```

# Test robust + scales

**The grid search was done with a slightly less processed dataset, but should still be representative of the final results. The final has better final self-cal + flagging.**

Now that we have the correctly agn-less data, we can image the minihalo itself. Making a test image to check what the residual RMS is. 

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='test_image',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=-0.5,
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

The RMS of the image is 5.76 uJy, residuals is 3.2 uJy.

Right object has a lot of difficulty being modelled with these settings. It is likely worth cleaning this separately with small scales and bias towards small to prevent overfitting before we try to fix it.

## Testing small scale bias and robust

Did a small grid search over robust and small scale bias

- smallscalebias = [-0.5, 0, 0.5]
- robust = [0.5, 1, 1.5, 2]

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"],
  imagename=image_name,
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=ssb,
  stokes='I', weighting='briggs', robust=r, pbcor=False,
  usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
  lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

![flux_comparison.png](Minihalo%20Imaging/flux_comparison%201.png)

Definitely prefer larger scale preference for modelling to get lower RMS. The robustness doesn’t have too much of an effect > 0.5 on the flux, but its definitely not fully cleaned. 

# Fit right galaxy

There is a radio galaxy to the down/right of the minihalo that has proved difficult to clean, since it is close to the beam size. Cleaning deeper than ~100 uJy results in negative radial spikes around the galaxy. 

Fitting this using a negative robust and subtracting the point-like behaviour from it worked. Required using a uvcut to get the point, not including this left negative radial spikes after subtraction.

RMS of images is ~6.6 uJy.

```python
# First model the right galaxy with uvcut and negative robust
OUTPUT_DIR = "right_image"
MASK_DIR = 'masked_models'

data_list = ["cconfig_uvsub", "dconfig1_uvsub.ms", "dconfig2_uvsub"]
uvrange = ">12klambda"

# Clean up previous runs
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.system(f"rm -r {OUTPUT_DIR}/*")
os.makedirs("{OUTPUT_DIR}/{MASK_DIR}", exist_ok=True)

for dataset in data_list:
	imagename = f"{OUTPUT_DIR}/{dataset}"
	tclean(
        vis=f"{dataset}.ms",
        imagename=imagename,
        imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
        specmode='mfs', niter=10000, gain=0.1, threshold='0.02mJy',
        deconvolver='mtmfs', pblimit=-1.e-6,
        scales=[0, 4, 8, 16, 32], smallscalebias=0.5,
        stokes='I', weighting='briggs', robust=-0.5, pbcor=False, uvrange=uvrange,
        usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
        lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False
    )

# Then mask the models to the point
crtf = "circle[[17h20m1.17s, 26d36m32.99s], 7.5arcsec]"
mynterms = 2

for model in model_list:
    full_models = [f'{OUTPUT_DIR}/{model}.model.tt{i}' for i in range(mynterms)]
    new_models = [f'{OUTPUT_DIR}/{MASK_DIR}/{m}' for m in full_models]
    for o, m in zip(full_models, new_models):
        os.system(f'cp -r {o} {m}')
        ia.open(m)
        reg = rg.fromtext(crtf, shape=ia.shape(), csys=ia.coordsys().torecord())
        inv_reg = rg.complement(reg)
        ia.set(0.0, region=inv_reg)
        ia.close()

# Then apply the model to the dataset, subtract, and split
# Final dataset is X_final.ms
for ms in datasets:
	ft(vis=f'{ms}.ms', nterms=mynterms,
	model=[f'{OUTPUT_DIR}/{MASK_DIR}/{ms}.model.tt{i}' for i in range(mynterms)],
	usescratch=True)
	uvsub(f'{ms}.ms')
	split(f'{ms}.ms', outputvis=f'{ms.split("_")[0]}_final.ms', datacolumn='corrected')
	uvsub(f'{ms}.ms', reverse=True)
```

# Final Image

**The following is done with the final dataset**

Using robust of 1, smallscalebias of -0.5 since it works the best in terms of RMS and hopefully a better beam will deal with the right feature a bit nicer. Interactively cleaning this feature with smaller scales and flipped smallscalebias should help the modelling behave better.

```python
tclean(vis=["cconfig_final.ms", "dconfig1_final.ms", "dconfig2_final.ms"],
  imagename="minihalo",
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=10000, gain=0.1, threshold='0.02mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, 
  scales=[0, 4, 8, 16, 32], smallscalebias=-0.5,
  stokes='I', weighting='briggs', robust=1, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

RMS ~3.4 u Jy, using interactive to go closer to noise level.

```python
tclean(vis=["cconfig_final.ms", "dconfig1_final.ms", "dconfig2_final.ms"],
  imagename="minihalo",
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=10000, gain=0.1, threshold='0.01mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, 
  scales=[0, 4, 8, 16, 32], smallscalebias=-0.5,
  stokes='I', weighting='briggs', robust=1, pbcor=False,
	interactive=True)
```

Also tested different robusts to try see better sensitivity.

Wide band correction for final image

```python
widebandpbcor(vis="../full_image/cconfig-p6.ms", 
	imagename="minihalo", nterms=2, threshold="0.0034mJy", pbmin=0.01,
	spwlist=list(range(32)), chanlist=[2]*32, weightlist=[1.0]*21 + [0.5]*11)
```

## Getting G14 Mask

![image.png](Minihalo%20Imaging/image.png)

Central part is an ellipse centred at RA 17:20:10.5 D26:38:02, major axis 69.6”, minor axis 60”, angle 63 degrees tilted to the right (-37). In terms of position angle this is +90 and +37 = +127 to rotate anticlockwise (to east).

```python
centre="ellipse[[17:20:09.4, +026.37.30], [30.0arcsec, 34.8arcsec], 127deg]]"
```

The tail can be approximated via a poly

```python
tail_mask = "poly[[17:20:10.50000, +026.38.02.0000], [17:20:11.40000, +026.38.07.5000], " + \
    "[17:20:14.20000, +026.37.34.0000], [17:20:14.20000, +026.37.00.0000], " + \
    "[17:20:13.00000, +026.36.33.0000], [17:20:11.20000, +026.36.23.0000], " + \
    "[17:20:09.70000, +026.36.30.0000], [17:20:09.30000, +026.36.35.0000], " + \
    "[17:20:09.70000, +026.36.56.0000]]"
```

## Calculating minihalo flux error

G14 uses $\sigma_{tot} = \sqrt{(\sigma_{cal}S_{MH})^2 + (rms\sqrt{N_{beam}})^2 + \sigma_{sub}^2}$ 

- $\sigma_{cal}$ is the calibration error that we can assume is 5% for now
- $S_{MH}$ is the flux of the minihalo
- $rms$ is obvious, using the value sigma from the residuals.
- $N_{beam}$ is the number of beams covering the minihalo. Can calculate this via number of pixels in the mask, area of a pixel, and the area of the beam.
- $\sigma_{sub}$ is the error from the AGN point subtraction estimated as $\sigma_{sub}^2 = (I_{MH, agn}A_{agn})^2$ where the first term is the averaged intensity of the minihalo in the agn region, and the second is the approximate area of the agn.

The first term is then the calibration error associated with the flux, the second term is the noise of the beam over the region, the third is from the point source subtraction of the AGN assuming it is fully wrong. 

The agn error seems very conservative, assuming we are confident that in the AGN modelling we removed any minihalo flux before the subtraction, we can instead use the associated RMS from the AGN modelling as the error. 

Our model shouldn’t contain any minihalo flux as otherwise we would likely see a negative impression in the minihalo image that isn’t present. 

$\sigma_{sub, new}^2 = \left(rms_{agn}\sqrt{N_{beam, agn}}\right)^2$ with $N_{beam,agn} = A_{agn} / A_{beam}$ 

The largest residual noise from the AGN images is 15.6 uJy.

## Statistics

Using the G14 mask to compute the minihalo flux so that I can compare the values accurately.

![image.png](Minihalo%20Imaging/image%201.png)

![image.png](Minihalo%20Imaging/image%202.png)

![image.png](Minihalo%20Imaging/image%203.png)

### Total Minihalo flux

Error of region circle[[17h20m10.03s, 26d37m31.9s], 3arcsec] was 3.48e-04 Jy from 2.84e-04 Jy/beam for 1.2 beams
Flux 8.61e-03 +/- 5.56e-04
cal error: 4.31e-04, noise error: 5.89e-05, sub_error: 3.48e-04

### Central Minihalo flux

Error of region circle[[17h20m10.03s, 26d37m31.9s], 3arcsec] was 3.48e-04 Jy from 2.84e-04 Jy/beam for 1.2 beams
Flux 7.60e-03 +/- 5.17e-04
cal error: 3.80e-04, noise error: 4.04e-05, sub_error: 3.48e-04

### Tail Minihalo flux

Error of region circle[[17h20m10.03s, 26d37m31.9s], 3arcsec] was 3.48e-04 Jy from 2.84e-04 Jy/beam for 1.2 beams
Flux 1.01e-03 +/- 3.54e-04
cal error: 5.03e-05, noise error: 4.29e-05, sub_error: 3.48e-04

## UV-constrained

Using 1-50 klambda to image you get

Flux 8.50 +/- 0.42 mJy
cal error: 4.25e-04, noise error: 5.89e-05, sub_error: 1.62e-06

# Checks

- Tail + centre comparisons ✅
- Noise level on AGN map for err calc
- L-band, perhaps fiddle to make a bit nicer.
    - wideband imaging effects since beam big
    - outer field subtraction not perfect.
- Check secondary flux ✅

## Check secondary flux for the dconfig calibrators.

![secondary_models.png](Minihalo%20Imaging/secondary_models.png)

There’s very little difference between the two D config measurements, with a relative difference of ~0.7% which is below expected calibration differences.

![rxj1720_seds.png](Minihalo%20Imaging/rxj1720_seds.png)