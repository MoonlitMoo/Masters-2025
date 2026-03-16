# D config 2

Data comes from this group [**25A-157.sb47896182.eb48256644.60761.48394760417**](../../Data%20Processing/25A-157%20sb47896182%20eb48256644%2060761%2048394760417%2023e1feeec5b780c098fedbcbebc9b7f3.md) 

# Imaging MS1455+2232

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

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="dconfig_2.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='briggs',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```jsx
gaincal(vis="dconfig_2.ms", caltable=f'dconfig_2.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_2.ms", gaintable=['dconfig_2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig_2-p0.ms', 
	datacolumn='corrected')
```

# Final Image

```jsx
tclean(vis="dconfig_2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.75,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```