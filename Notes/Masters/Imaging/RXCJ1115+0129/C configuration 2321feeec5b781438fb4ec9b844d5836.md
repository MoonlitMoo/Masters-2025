# C configuration

Data comes from this group [24A-411.sb45152792.eb45228190.60344.213862488425](../../Data%20Processing/24A-411%20sb45152792%20eb45228190%2060344%20213862488425%202161feeec5b780faadbedeb125a25b17.md) 

# Imaging RXJ1720.1+2232

# Dirty image

```python
tclean(vis="cconfig.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

![image-dirty.image.tt0-image-2025-07-25-10-25-39.png](C%20configuration/image-dirty.image.tt0-image-2025-07-25-10-25-39.png)

# First self calibration

Using high threshold to make a simple point source model. Lot of point sources.

```python
tclean(vis="cconfig.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```python
gaincal(vis="cconfig.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig.ms', outputvis=f'cconfig-p0.ms', 
	datacolumn='corrected')
```

Flagging 0.8% → 5%

# Second self calibration

Lowering threshold to 0.05 mJy based on residuals. Also using diffuse scales. 

```python
tclean(vis="cconfig-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.05mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

rms ~3e-6

```jsx
gaincal(vis="cconfig-p0.ms", caltable=f'cconfig.p1', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig-p0.ms", gaintable=['cconfig.p1'])
split(vis=f'cconfig-p0.ms', outputvis=f'cconfig-p1.ms', 
	datacolumn='corrected')
```

# Third calibration

```jsx
tclean(vis="cconfig-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.009mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

![image-p1.image.tt0-image-2025-07-25-13-48-53.png](C%20configuration/image-p1.image.tt0-image-2025-07-25-13-48-53.png)

Not bad, need to take care with left line thing.