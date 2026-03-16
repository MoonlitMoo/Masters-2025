# D configuration 1

Data comes from this group [**25A-157.sb47896383.eb48084831.60734.58634814815**](../../Data%20Processing/25A-157%20sb47896383%20eb48084831%2060734%2058634814815%2020f1feeec5b7809f8318c01d7acbe228.md) 

# Imaging A2204

We want field 2, correlations LL RR + averaging. 

- Max uvdist $B\approx~3500m$
- max uvwave ~135000.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width on average is $4/2048 \text{ GHz } = 1.95 \text{ MHz}$.
- Time on source is 5 scans by ~9 minutes = $45$ minutes

### Can average over 16 channels, 60s like previous data

# Dirty image

Using same settings from 2A0335+096. 

```python
tclean(vis="dconfig_1.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

Max ~7mJy (more because not sel 100%), psf ~1mJy from it? Definitely not as clean as the cconfig data. 

![image-dirty.image.tt0-image-2025-06-26-09-11-56.png](D%20configuration%201/image-dirty.image.tt0-image-2025-06-26-09-11-56.png)

# First self calibration

Using high threshold to make a simple point source model. Trying same settings as cconfig here.

```python
tclean(vis="dconfig_1.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='1.2mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_1.ms", caltable=f'dconfig_1.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1.ms", gaintable=['dconfig_1.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig_1-p0.ms', 
	datacolumn='corrected')
```

Flagging 5% → 7%.

# Second self calibration

```python
tclean(vis="dconfig_1-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```jsx
gaincal(vis="dconfig_1-p0.ms", caltable=f'dconfig_1.p1', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1-p0.ms", gaintable=['dconfig_1.p1'])
split(vis=f'dconfig_1-p0.ms', outputvis=f'dconfig_1-p1.ms', 
	datacolumn='corrected')
```

6.9% → 7.9% spw 25,29 not calibrated 

Drop to 20 uJy, slightly higher than previous one.

# Final Image

```jsx
tclean(vis="dconfig_1-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

Looking good for final imaging. Much better in the centre, could go deeper to try get rid of psf in outer edges.

![image-p1.image.tt0-image-2025-06-26-11-57-20.png](D%20configuration%201/image-p1.image.tt0-image-2025-06-26-11-57-20.png)