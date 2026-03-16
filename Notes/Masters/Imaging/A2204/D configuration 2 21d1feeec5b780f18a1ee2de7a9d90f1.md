# D configuration 2

Data comes from this group [25A-157.sb47895952.eb48256632.60761.33700966435](../../Data%20Processing/25A-157%20sb47895952%20eb48256632%2060761%2033700966435%202141feeec5b7802a99b1f7fc60716984.md) 

# Imaging A2204

We want field 1, correlations LL RR + averaging. 

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
tclean(vis="dconfig_2.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

Looks better than prev dconfig_1 dataset

![image-dirty.image.tt0-image-2025-06-26-12-18-27.png](D%20configuration%202/image-dirty.image.tt0-image-2025-06-26-12-18-27.png)

# First self calibration

Using high threshold to make a simple point source model. Trying same settings as cconfig here.

```python
tclean(vis="dconfig_2.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='1.2mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_2.ms", caltable=f'dconfig_2.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2.ms", gaintable=['dconfig_2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig_2-p0.ms', 
	datacolumn='corrected')
```

Flagging 5% → 7.7%.

# Second self calibration

```python
tclean(vis="dconfig_2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```jsx
gaincal(vis="dconfig_2-p0.ms", caltable=f'dconfig_2.p1', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2-p0.ms", gaintable=['dconfig_2.p1'])
split(vis=f'dconfig_2-p0.ms', outputvis=f'dconfig_2-p1.ms', 
	datacolumn='corrected')
```

7.6% → 7.8% 

# Final Image

```jsx
tclean(vis="dconfig_2-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

Looking good for final imaging. Still a bit of psf, centre needs work, but ok otherwise.

![image-p1.image.tt0-image-2025-06-26-14-29-49.png](D%20configuration%202/image-p1.image.tt0-image-2025-06-26-14-29-49.png)