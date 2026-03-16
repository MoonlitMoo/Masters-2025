# D config 2

Data comes from this group [25A-157.sb47894310.eb48188934.60750.12720050926](../../Data%20Processing/25A-157%20sb47894310%20eb48188934%2060750%2012720050926%202281feeec5b780b3acb3e6be55d79baa.md) 

# Imaging RXCJ1115+0129

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
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
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

Check to see if we can get down deeper 8

```jsx
tclean(vis="dconfig_2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.009mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```

![image-start.image.tt0-image-2025-07-25-18-26-17.png](D%20config%202/image-start.image.tt0-image-2025-07-25-18-26-17.png)

Seems like higher noise, but still good.