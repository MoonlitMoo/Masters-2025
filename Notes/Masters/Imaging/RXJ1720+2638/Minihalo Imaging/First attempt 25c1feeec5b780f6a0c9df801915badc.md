# First attempt

# AGN image

Using uniform weighting to try only image the AGN so we can subtract it. 

Still a little minihalo so setting uvwave, [0, 115000] in cconcfig, [0, 35000] in dconfig. Killing less than 5k seems to mask out the minihalo.

RMS is 8e-6

```python
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"], 
	imagename='image-p4-uniform',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.024mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	uvrange='>7klambda', savemodel='modelcolumn')
```

## Checking AGN flux

From https://www.arxiv.org/pdf/1403.2820v1 (Giacintucci, S., et al, 2014)

![image.png](First%20attempt/image.png)

From https://academic.oup.com/mnras/article/508/2/2862/6373941?login=true (Perrott, C Y., et al, 2022)

4.4 (0.13) mJy at 15.5 GHz

My result is ~1.2 mJy, which agrees with G14, but not P22?

Might as well continue and see what’s what.

 

## Subtract and image minihalo

Technically the model also includes the head tail (almost noise) and the thing to the right (not noise, line 3 from P22?).

 Adding larger scale. 4.6 uJy RMS (robust .5, trying 1.5)

```python
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"], 
	imagename='image-p4-minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

Save the model and recalibrate to see what happens 

```python
self_calibrate(5, 'ea12')
```

Almost no extra flagging

# Minihalo image 2

```python
tclean(vis=["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"], 
	imagename='image-p5-uniform',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.024mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=-2.0, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	uvrange='>7klambda', savemodel='modelcolumn')
```

Subtract and then image again. Robust 0.5 works better than 1.5 and now 5.7 uJy residuals.

```python
tclean(vis=["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"], 
	imagename='image-p5-minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

Clean down lower interactively since the minihalo is still visible in the residuals. The centre has lower residuals around it so getting close to noise level here.

```python
tclean(vis=["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"], 
	imagename='image-p5-minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=10000, gain=0.1, threshold='0.005mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	interactive=True)
```

## Check flux

Using imfit

```python
imfit("image-p5-uniform.image.tt0",  logfile='agn.log')
```

Gets 

- Integrated:   1.262 +/- 0.017 mJy
- Peak:         1.1257 +/- 0.0091 mJy/beam

Using the peak value since it should be an unresolved source. 

Fitting power law to G14 then comparing own point gives 

- alpha = 0.846 ± 0.022
S_10GHz(pred) = 1.250 ± 0.059 mJy
S_10GHz(meas) = 1.126 mJy  →  Δ = -0.1238 mJy,  z_fit = -2.10,  z_combined = -2.07

So underestimating it a wee bit. 

Trying the integrated value gets a much closer value to the expected

- alpha = 0.846 ± 0.022
S_10GHz(pred) = 1.250 ± 0.059 mJy
S_10GHz(meas) = 1.262 mJy  →  Δ = 0.0125 mJy,  z_fit = 0.21,  z_combined = 0.20