# Smaller data set (1)

Trying with 16 ch, 45s averaging

```python
split(vis=msname,
      outputvis='imageattempt1.ms',
      field='2', spw='16~47', correlation="LL,RR",
      datacolumn='corrected',
      width=16, timebin='45s',
      keepflags=False)
```

Then cleaning, using the smaller pixel size as earlier 

```python
tclean(vis="imagetry2.ms", imagename='2A0335+096-p0',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3072,3072], cell=['0.3arcsec','0.3arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')

```

## Self calibration 1

```python
gaincal(vis="imagetry2.ms", caltable=f'imagetry2.p0', 
        solint='15min', scan='combine', refant='ea22', gaintype='G', calmode='p', solnorm=False)
```

A couple antenna looked bad, but went ahead anyway. Applied and split to new ms

```python
applycal(vis="imageattempt1.ms", gaintable=['imageattempt1.p0'])
split(vis=f'imageattempt1.ms', outputvis=f'imageattempt2.ms', 
	datacolumn='corrected')
```