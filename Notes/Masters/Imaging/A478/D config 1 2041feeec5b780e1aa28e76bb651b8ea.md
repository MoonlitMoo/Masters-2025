# D config 1

Data from [25A-157.sb47896788.eb48078564.60733.06076180555 ](../../Data%20Processing/25A-157%20sb47896788%20eb48078564%2060733%2006076180555%201f41feeec5b780f6a278e16dab64995d.md) 

# Imaging A478

We want field 4, correlations LL RR + averaging. 

- Max uvdist $B\approx~3500m$
- max uvwave ~135000.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width on average is $4/2048 \text{ GHz } = 1.95 \text{ MHz}$.
- Time on source is 14 scans by ~9 minutes = ~2 hours

# First attempt

Uses the bad phase solutions, but good looking secondary calibrator `dconfig_1`. 

## Dirty Image

Using same settings from rest.

```python
tclean(vis="dconfig_1.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

![image-dirty.image.tt0-image-2025-06-01-12-34-26.png](D%20config%201/image-dirty.image.tt0-image-2025-06-01-12-34-26.png)

## Self calibration 1

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

```python
gaincal(vis="dconfig_1.ms", caltable=f'dconfig_1.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1.ms", gaintable=['dconfig_1.p0'])
split(vis=f'dconfig_1.ms', outputvis=f'dconfig_1-p0.ms', 
	datacolumn='corrected')
```

## Self calibration 2

```python
tclean(vis="dconfig_1-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_1-p0.ms", caltable=f'dconfig_1.p1', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1-p0.ms", gaintable=['dconfig_1.p1'])
split(vis=f'dconfig_1-p0.ms', outputvis=f'dconfig_1-p1.ms', 
	datacolumn='corrected')
```

# Second attempt

Uses good phase solutions, bad secondary calibrator `dconfig_1-2`. 

## Dirty image

```python
tclean(vis="dconfig_1-2.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

![image-dirty.image.tt0-image-2025-06-01-12-33-53.png](D%20config%201/image-dirty.image.tt0-image-2025-06-01-12-33-53.png)

## Self calibration 1

```python
tclean(vis="dconfig_1-2.ms", 
	imagename='image-start',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.5mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,  
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_1-2.ms", caltable=f'dconfig_1-2.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1-2.ms", gaintable=['dconfig_1-2.p0'])
split(vis=f'dconfig_1-2.ms', outputvis=f'dconfig_1-2-p0.ms', 
	datacolumn='corrected')
```

Only spw 29 and 31 had difficulties, 14/14/7 and 28/28/15 respectively, flagging 2% → 2.5%.

## Self calibration 2

```python
tclean(vis="dconfig_1-2-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_1-2-p0.ms", caltable=f'dconfig_1-2.p1', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1-2-p0.ms", gaintable=['dconfig_1-2.p1'])
split(vis=f'dconfig_1-2-p0.ms', outputvis=f'dconfig_1-2-p1.ms', 
	datacolumn='corrected')
```

# Third attempt (after Yvette script)

```python
tclean(vis="dconfig_1.ms", 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

![.png](D%20config%201.png)

```python
gaincal(vis="dconfig_1.ms", caltable=f'dconfig_1.p0', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1.ms", gaintable=['dconfig_1.p0'])
split(vis=f'dconfig_1.ms', outputvis=f'dconfig_1-p0.ms', 
	datacolumn='corrected')
```

## Self cal 2

```python
tclean(vis="dconfig_1-p0.ms", 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False,
	savemodel='modelcolumn')
```

```python
gaincal(vis="dconfig_1-p0.ms", caltable=f'dconfig_1.p1', 
	solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig_1-p0.ms", gaintable=['dconfig_1.p1'])
split(vis=f'dconfig_1-p0.ms', outputvis=f'dconfig_1-p1.ms', 
	datacolumn='corrected')
```

## Final Cal

```python
tclean(vis="dconfig2-p1.ms", 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=2000, gain=0.1, threshold='0.012mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	interactive=True, 
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	savemodel='modelcolumn')
```