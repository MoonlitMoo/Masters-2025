# C configuration

Data comes from this group [24A-411.sb45153015.eb45227399.60343.435757858795](../../Data%20Processing/24A-411%20sb45153015%20eb45227399%2060343%20435757858795%2020e1feeec5b780ccb385dfec6b9f93eb.md) 

# Imaging A2204

We want field 4, correlations LL RR + averaging. 

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
tclean(vis="cconfig.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

Max ~7mJy, psf ~1mJy from it?

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="cconfig.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='1.2mJy',
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

Flagging 0.5% → 1%. Looks like ridges ~.1mJy. 

# Second self calibration

```python
tclean(vis="cconfig-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```jsx
gaincal(vis="cconfig-p0.ms", caltable=f'cconfig.p1', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig-p0.ms", gaintable=['cconfig.p1'])
split(vis=f'cconfig-p0.ms', outputvis=f'cconfig-p1.ms', 
	datacolumn='corrected')
```

1% → 1%

Drop to 10 uJy. 

# Final Image

```jsx
tclean(vis="cconfig-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

![image-p1.image.tt0-image-2025-06-25-15-31-04.png](C%20configuration/image-p1.image.tt0-image-2025-06-25-15-31-04.png)

Cleaned too deep in centre, but looking good for final imaging.