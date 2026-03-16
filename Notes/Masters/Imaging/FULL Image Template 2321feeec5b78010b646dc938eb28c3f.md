# FULL Image Template

Using the same image proportions as the 2A0335+096 image which is ~19.2”.

The data was collected with channel averaging of 16, time averaging of 60s. 

# Dirty Image

```jsx
tclean(vis=["cconfig.ms", "dconfig_1.ms", "dconfig_2.ms"], 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

# First self calibration

```jsx
	tclean(vis=["cconfig.ms", "dconfig_1.ms", "dconfig_2.ms"], 
		imagename='image-init',
		imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
		specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
		deconvolver='mtmfs', pblimit=-1.e-6,
		interactive=True, 
		stokes='I', weighting='natural', robust=0.5, pbcor=False, 
		savemodel='modelcolumn')
```

```jsx
gaincal(vis="dconfig_2.ms", caltable=f'dconfig2.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
gaincal(vis="dconfig_1.ms", caltable=f'dconfig1.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
gaincal(vis="cconfig.ms", caltable=f'cconfig.p0', 
	solint='inf', refant='ea10', gaintype='G', calmode='p', solnorm=False)
```

```jsx
applycal(vis="dconfig_2.ms", gaintable=['dconfig2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig2-p0.ms', 
	datacolumn='corrected')
applycal(vis="dconfig_1.ms", gaintable=['dconfig1.p0'])
split(vis=f'dconfig_1.ms', outputvis=f'dconfig1-p0.ms', 
	datacolumn='corrected')
applycal(vis="cconfig.ms", gaintable=['cconfig.p0'])
split(vis=f'cconfig.ms', outputvis=f'cconfig-p0.ms', 
	datacolumn='corrected')
```

cconfig: 0% → 36%

dconfig_1: 0% → 38%

dconfig_2: 0% → 31%

# Calibration 2

Adding statwt.

```jsx
statwt(vis='dconfig1-p0.ms', datacolumn='data')
statwt(vis='dconfig2-p0.ms', datacolumn='data')
statwt(vis='cconfig-p0.ms', datacolumn='data')
```

Noise is ~.01 mJy, diffuse structures so using scales now.

```jsx
tclean(vis=["cconfig-p0.ms", "dconfig1-p0.ms", "dconfig2-p0.ms"], 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.012mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```