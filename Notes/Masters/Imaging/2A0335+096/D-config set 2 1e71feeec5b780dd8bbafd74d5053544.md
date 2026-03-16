# D-config set 2

# Image settings

Max uv-wave is ~37500 wavelengths → $D = 37500\lambda$ and $\theta_{min} = 1/37500 \>\text{rad} = \frac1{37500} \times 206265\> \frac{\text{arcsec}}{\text{rad}} \approx 5.5 \> \text{arcsec}$. So cells can be ~1” wide. I’m going to use the previous settings though, since we’ll be combining the datasets.

```python
tclean(vis="dconfig_2.ms", imagename='dconfig2-dirty',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

Beam size is 9.75” by 7.7” from tclean. 

# Check self calibration

Doing simple model to see if any contaminating RFI.

```jsx
tclean(vis="dconfig_2.ms", imagename='dconfig2-0',
	imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

```jsx
gaincal(vis="dconfig_2.ms", caltable=f'dconfig2.p0', 
        solint='inf', refant='ea12', gaintype='G', calmode='p', solnorm=False)

applycal(vis="dconfig_2.ms", gaintable=['dconfig2.p0'])
split(vis=f'dconfig_2.ms', outputvis=f'dconfig2-p0.ms', 
	datacolumn='corrected')
```

There are a few antenna that are completely flagged + few solutions??