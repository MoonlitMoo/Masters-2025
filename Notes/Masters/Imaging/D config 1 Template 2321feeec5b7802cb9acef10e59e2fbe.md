# D config 1 Template

Data comes from this group **PAGELINK**

# Imaging **NAME**

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

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="dconfig_1.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

Selected two sources. 

```jsx
gaincal(vis="dconfig_1.ms", caltable=f'dconfig_1.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1.ms", gaintable=['dconfig_1.p0'])
split(vis=f'dconfig_1.ms', outputvis=f'dconfig_1-p0.ms', 
	datacolumn='corrected')
```

# Final image

```jsx
tclean(vis="dconfig_1-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.05mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```