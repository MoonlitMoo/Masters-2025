# D config 2

Data comes from this group [25A-157.sb47897178.eb48143348.60745.94845704861](../../Data%20Processing/25A-157%20sb47897178%20eb48143348%2060745%2094845704861%201f41feeec5b780458b18ee312b8be945.md) 

# Imaging A478

We want field 4, correlations LL RR + averaging. 

- Max uvdist $B\approx~3500m$
- max uvwave ~135000.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width on average is $4/2048 \text{ GHz } = 1.95 \text{ MHz}$.
- Time on source is 14 scans by ~9 minutes = ~2 hours

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

Brightest ~5.0 mdy

![image-dirty.image.tt0-image-2025-05-30-11-36-39.png](D%20config%202/image-dirty.image.tt0-image-2025-05-30-11-36-39.png)

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

Managed to clean centre one down, no other sources yet. Residuals show secondary point sources at ~.3-.1 mJy.

Running a self calibration for this, ea12 seems ok from the pipeline results. 

```python
gaincal(vis="dconfig_2.ms", caltable=f'dconfig_2.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2.ms", gaintable=['dconfig_2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig_2-p0.ms', 
	datacolumn='corrected')
```

# Second self calibration

Lowering threshold to 0.1 mJy.

```python
tclean(vis="dconfig_2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

```python
gaincal(vis="dconfig_2-p0.ms", caltable=f'dconfig_2.p1', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2-p0.ms", gaintable=['dconfig_2.p1'])
split(vis=f'dconfig_2-p0.ms', outputvis=f'dconfig_2-p1.ms', 
	datacolumn='corrected')
```

Residuals seem to be ~1e-6 at noise level, image at 5e-6. 

# Final image

Adding in scales to pick up diffuse sources, lowering the threshold. 

```python
tclean(vis="dconfig_2-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

Still some PSF in the residuals, but pretty minimal. Not worth continuing to clean, just shows ready to join up with D config data.

![image-p1.image.tt0-image-2025-06-01-11-26-30.png](D%20config%202/image-p1.image.tt0-image-2025-06-01-11-26-30.png)