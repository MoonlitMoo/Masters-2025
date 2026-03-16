# D config 2

Data comes from this group [25A-157.sb47895952.eb48256632.60761.33700966435](../../Data%20Processing/25A-157%20sb47895952%20eb48256632%2060761%2033700966435%202141feeec5b7802a99b1f7fc60716984.md) 

# Imaging A478

We want field 3, correlations LL RR + averaging. 

- Max uvdist $B\approx~3500m$
- max uvwave ~135000.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width on average is $4/2048 \text{ GHz } = 1.95 \text{ MHz}$.
- Time on source is 4 scans by ~9 minutes = 36 minutes

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

Brightest ~2 mJy. Its so beautiful compared to the other one.

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="dconfig_2.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

Selected two sources. Residuals show noise ~1 mJy. This is really high, probably cause the data is pretty bad.

```jsx
gaincal(vis="dconfig_2.ms", caltable=f'dconfig_2.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2.ms", gaintable=['dconfig_2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig_2-p0.ms', 
	datacolumn='corrected')
```

Flagging 1.6% → 10.4%.

# Final Image

```jsx
tclean(vis="dconfig_2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.05mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

Got down a lot, not yet to noise level. Able to go further but no point as not final image yet. Actually looks really clean.

![image-p0.image.tt0-image-2025-06-22-12-07-08.png](D%20config%202/image-p0.image.tt0-image-2025-06-22-12-07-08.png)