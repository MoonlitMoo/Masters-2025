# D-config set 1

Note this is for the final version, not the checking if flagging was enou

# Image settings

Max uv-wave is ~37500 wavelengths → $D = 37500\lambda$ and $\theta_{min} = 1/37500 \>\text{rad} = \frac1{37500} \times 206265\> \frac{\text{arcsec}}{\text{rad}} \approx 5.5 \> \text{arcsec}$. So cells can be ~1” wide. I’m going to use the previous settings though, since we’ll be combining the datasets.

```python
tclean(vis="dconfig_1.ms", imagename='dconfig1-dirty',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

Beam size is 9.75” by 7.7” from tclean. 

# Attempt 1

Do a simple central model to do a calibration with to check everything seems ok

```python
tclean(vis="dconfig_1.ms", imagename='dconfig1-0',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Try a calibration

```python
gaincal(vis="dconfig_1.ms", caltable=f'dconfig1.p0', 
        solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
```

First attempt phase notes

- ea04, ea15, ea18, ea20 are bad
- The two nasty regions still very mid.

Decided to flag bad antenna, then use to self calibrate

```bash
flagdata(vis='dconfig1.p0', mode='manual', antenna='ea18,ea20,ea04,ea15')
applycal(vis="dconfig_1.ms", gaintable=['dconfig1.p0'])

split(vis=f'dconfig_1.ms', outputvis=f'dconfig1-p0.ms', 
	datacolumn='corrected')
```

# Deleting half

Flag 10,11,22~31 spw.

Run gain cal, check phase, still bad antenna, but spw aren’t bad

```bash
gaincal(vis="dconfig_1.ms", caltable=f'dconfig1.p0', 
        solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
flagdata(vis='dconfig1.p0', mode='manual', antenna='ea18,ea20,ea04,ea15')
applycal(vis="dconfig_1.ms", gaintable=['dconfig1.p0'])

split(vis=f'dconfig_1.ms', outputvis=f'dconfig1-p0.ms', 
	datacolumn='corrected')
```

Seems mostly ok, bar a few outliers. Might as well look at the image to see if it has improved. 

```bash
tclean(vis="dconfig-p0.ms", imagename='dconfig1-p0',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

## Self calibration 2

```bash
gaincal(vis="dconfig1-p0.ms", caltable=f'dconfig1.p1', 
        solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
applycal(vis="dconfig1-p0.ms", gaintable=['dconfig1.p1'])

split(vis=f'dconfig1-p0.ms', outputvis=f'dconfig1-p1.ms', 
	datacolumn='corrected')
```

```bash
tclean(vis="dconfig1-p1.ms", imagename='dconfig1-p1',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

# Dataset 2

Using the lower flag dataset `dconfig1-2.ms` to try make an image directly. 

```bash
tclean(vis="dconfig1-2.ms", imagename='dconfig1-2-0',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Not a fan, so will try to self calibrate next, but using a simpler model as I don’t love the pattern. 

```bash
tclean(vis="dconfig1-2.ms", imagename='dconfig1-2-02',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Trying a self calibration, the same antenna are bad so I’ll flag them again. Lots of noise in phase solutions for microwave spw.

```bash
flagdata(vis='dconfig1-2.ms', mode='manual', antenna='ea18,ea20,ea04,ea15')
gaincal(vis="dconfig1-2.ms", caltable=f'dconfig1-2.p0', 
        solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)
        
applycal(vis="dconfig1-2.ms", gaintable=['dconfig1-2.p0'])
split(vis=f'dconfig1-2.ms', outputvis=f'dconfig1-2-p0.ms', 
	datacolumn='corrected')
```

![image.png](D-config%20set%201/image.png)

```bash
tclean(vis="dconfig-p0.ms", imagename='dconfig1-p0',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```