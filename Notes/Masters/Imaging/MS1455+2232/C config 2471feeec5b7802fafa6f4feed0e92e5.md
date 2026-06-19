# C config

Data comes from this group [24A-411.sb45153015.eb45227399.60343.435757858795](../../Data%20Processing/24A-411%20sb45153015%20eb45227399%2060343%20435757858795%2020e1feeec5b780ccb385dfec6b9f93eb.md) 

# Imaging **MS1455+2232**

# Dirty image

Using same settings from 2A0335+096.

```python
tclean(vis="cconfig.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='briggs',robust=0.5,pbcor=False)
```

# First self calibration

Using high threshold to make a simple point source model.

```python
tclean(vis="cconfig.ms", 
	imagename='image-init',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='briggs',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

RMS is 3.52 uJy. 

```jsx
gaincal(vis="cconfig.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig.ms', outputvis=f'cconfig-p0.ms', 
	datacolumn='corrected')
```

# Final image

Running automask to see if it has any issues in regions. 

```jsx
tclean(vis="cconfig-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

There is trouble in cleaning the middle section with these settings, though likely more controlled selfcalibration would work well.

![image-p0.image.tt0-image-2025-08-06-16-04-12.png](C%20config/image-p0.image.tt0-image-2025-08-06-16-04-12.png)