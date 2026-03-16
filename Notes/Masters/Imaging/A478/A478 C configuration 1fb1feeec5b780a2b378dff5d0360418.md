# A478 C configuration

Data comes from this group [24A-411.sb45152540.eb45209965.60336.070794328705](../../Data%20Processing/24A-411%20sb45152540%20eb45209965%2060336%20070794328705%201ba1feeec5b780349b9dcf33a649233f.md) 

# Imaging A478

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

![image-dirty.image.tt0-image-2025-05-23-09-22-17.png](A478%20C%20configuration/image-dirty.image.tt0-image-2025-05-23-09-22-17.png)

Brightest ~5.0 m6060Jy

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="cconfig.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

Managed to clean centre one down, no other sources yet. Residuals show secondary point sources at ~.3-.1 mJy.

Running a self calibration for this, ea10 seems ok from the pipeline results. 

```python
gaincal(vis="cconfig.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig.ms', outputvis=f'cconfig-p0.ms', 
	datacolumn='corrected')
```

# Second self calibration

Lowering threshold to 0.1 mJy.

```python
tclean(vis="cconfig-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

```python
gaincal(vis="cconfig-p0.ms", caltable=f'cconfig.p1', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig-p0.ms", gaintable=['cconfig.p1'])
split(vis=f'cconfig-p0.ms', outputvis=f'cconfig-p1.ms', 
	datacolumn='corrected')
```

Residuals seem to be ~1e-6 at noise level, image at 5e-6. 

# Final image

Adding in scales to pick up diffuse sources, lowering the threshold. 

```python
tclean(vis="cconfig-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

Still some PSF in the residuals, but pretty minimal. Not worth trying again, just shows ready to join up with D config data.

![image-p1.image.tt0-image-2025-05-23-12-30-38.png](A478%20C%20configuration/image-p1.image.tt0-image-2025-05-23-12-30-38.png)