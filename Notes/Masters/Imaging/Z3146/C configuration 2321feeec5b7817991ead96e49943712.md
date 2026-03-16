# C configuration

Data comes from this group [24A-411.sb45152792.eb45228190.60344.213862488425](../../Data%20Processing/24A-411%20sb45152792%20eb45228190%2060344%20213862488425%202161feeec5b780faadbedeb125a25b17.md) 

# Imaging Z3148

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

![image-dirty.image.tt0-image-2025-07-28-11-38-35.png](C%20configuration/image-dirty.image.tt0-image-2025-07-28-11-38-35.png)

# First self calibration

```python
tclean(vis="cconfig.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='briggs',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```python
gaincal(vis="cconfig.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
applycal(vis="cconfig.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig.ms', outputvis=f'cconfig-p0.ms', 
	datacolumn='corrected')
```

1% → 4%

# Second self calibration

Using settings from dconfig experiments.

```python
tclean(vis="cconfig-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.02mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[1,4,8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=-1, uvtaper=['9arcsec'], pbcor=False, 
	savemodel='modelcolumn')
```