# 2A0335+096 C-configuration

Data comes from this group [24A-411.sb45152540.eb45209965.60336.070794328705](../../Data%20Processing/24A-411%20sb45152540%20eb45209965%2060336%20070794328705%201ba1feeec5b780349b9dcf33a649233f.md) 

# Imaging 2A0335+096

We want field 2, spw 16~47, correlations LL RR + averaging. 

- Max uvdist $B\approx~3500m$
- max uvwave ~125000.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width on average is $4/2048 \text{ GHz } = 1.95 \text{ MHz}$.
- Time on source is 5 scans by ~9 minutes = $45$ minutes

### Calculate averaging

Bandwidth averaging approx $\Delta\nu = x\frac{\nu D}{4B}$ where $x$ is sensitivity (1, 4 smaller the more sensitive). High freq means we could probably do 4. 

$$
\begin{align*}
\Delta\nu &= x\frac{\nu D}{4B} \\
&= 4 \frac{10^{10}\times 25}{4 \times 3500}\\
&= 7.14 \times10^7\\
&= 71 \text{ MHz}
\end{align*}
$$

Then time averaging appox $\Delta t = x\frac{D}{4\omega B}$ with $\omega = \frac{2\pi}{24\times 3600}=7.27\times10^{-5} \text{ rad s}^{-1}$ (rotation speed of the earth). $x$ as 1 or 3.7 here. 

$$
\begin{align*}
\Delta t &= x \frac{D}{4\omega B}\\
&= 3.7 \frac{25}{4\times7.27\times10^{-5}\times3500}\\
&= 91 \text{ s}
\end{align*}
$$

Can average over 8 channels, 30s. 

### Split command

```python
split(vis=msname,
      outputvis='imageattempt1.ms',
      field='2', spw='16~47', correlation="LL,RR",
      datacolumn='corrected',
      width=8, timebin='30s',
      keepflags=False)
```

### Image settings

Max uv-wave is ~125000 wavelengths → $D = 135000\lambda$ and $\theta_{min} = 1/125000 \>\text{rad} = \frac1{135000} \times 206265\> \frac{\text{arcsec}}{\text{rad}} \approx 1.528 \> \text{arcsec}$. 

Then pixel size should be 4-5 pixels per 1.528” → .3” per pixel. According to https://ui.adsabs.harvard.edu/abs/1988MNRAS.234..847P/abstract the diameter is ~12’. This gives us $12*60 / 0.3 \approx 2400$. Then we want a factor in $2^x \times 3 \times 5$ and $x=7 → 1920$ and $x=8→3840$. 

Image size is [3840, 3840] by this logic.

```python
tclean(vis="imageattempt1.ms", imagename='2A0335+096',
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy', 
	deconvolver='multiscale', scales=[0, 5, 15, 45], smallscalebias=0.9, 
	interactive=True, imsize=[3840,3840], cell=['0.3arcsec','0.3arcsec'], pblimit=-1.e-6
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Version 2 used threshold as 0.15mJ.

Version 3 used threshold as 0.08mJ

### Notes

- pblimit, gives you a bigger image, stops clipping outside of a particular beam extent.
- mtmfs - multi term multi frequency synthesis. For wider frequency / bandwidth  data.
- Self-calibration, phase usually the problem. Amplitude sometimes but not always (and you can accidentally mess up your data)
- Can probably trim further to make faster, 16 ch (45s?). Reduce image size to 2^10 * 3 = 3072
- Look at mpi?

```python
tclean(vis="imageattempt1.ms", imagename='2A0335+096-p0',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3840,3840], cell=['0.3arcsec','0.3arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

- Solution interval harder since less SNR, fainter source. solint=’inf’ without combine=’scan’ does each scan individually.

```python
gaincal(vis="imageattempt1.ms", caltable=f'imageattempt1.p0', 
        solint='inf', refant='ea22', gaintype='G', calmode='p', solnorm=False)
```

- how many don’t fit + weird/wiggly = maybe combine 2 scans etc. Do via explicit time + combine=’scan’
- Look fine then maybe try increase sols per scan.
- Everything is on fire: average per spw. combine=’scan, spw’
- Then apply it and go back to imaging.

Repeat above until happy. Phase solutions should approach 0, images should stop adjusting.

- daisy chain by splitting calibrated data to new ms “attempt2”.

### Self calibration

```python
gaincal(vis="imageattempt1.ms", caltable=f'imageattempt1.p0', 
        solint='inf', refant='ea22', gaintype='G', calmode='p', solnorm=False)
```

A couple antenna looked bad, but went ahead anyway. Applied and split to new ms

```python
applycal(vis="imageattempt1.ms", gaintable=['imageattempt1.p0'])
split(vis=f'imageattempt1.ms', outputvis=f'imageattempt2.ms', 
	datacolumn='corrected')
```

Then went through on a second round of cleaning (overwrote first image initially cause I’m smart).

```python
tclean(vis="imageattempt2.ms", imagename='2A0335+096-p1',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3840,3840], cell=['0.3arcsec','0.3arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Not a huge fan of the results so redid, but bumped threshold to 0.08mJ, since I’m masking pretty heavily.

```python
gaincal(vis="imageattempt2.ms", caltable=f'imageattempt2.p1',solint='inf', 
	refant='ea22', gaintype='G', calmode='p', solnorm=False)

applycal(vis="imageattempt2.ms", gaintable=['imageattempt2.p1'])
split(vis=f'imageattempt2.ms', outputvis=f'imageattempt3.ms', 
	datacolumn='corrected')
```

Then imaging again, but dropping pixels to 3072 now. 

```python
tclean(vis="imageattempt3.ms", imagename='2A0335+096-p2',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.08mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3072,3072], cell=['0.3arcsec','0.3arcsec'], pblimit=-1/.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Recalibrate

```python
gaincal(vis="imageattempt3.ms", caltable=f'imageattempt3.p2',solint='inf', 
	refant='ea22', gaintype='G', calmode='p', solnorm=False)
	
applycal(vis="imageattempt3.ms", gaintable=['imageattempt3.p2'])
split(vis=f'imageattempt3.ms', outputvis=f'imageattempt4.ms', 
	datacolumn='corrected')
```

Re-image, dropping threshold by about half

```python
tclean(vis="imageattempt4.ms", imagename='2A0335+096-p3',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.045mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3072,3072], cell=['0.3arcsec','0.3arcsec'], pblimit-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Comparing to https://articles.adsabs.harvard.edu/pdf/1995ApJ...451..125S we have found the following points. 

![image.png](2A0335+096%20C-configuration/image.png)

## Try smaller data set

[Smaller data set (1)](2A0335+096%20C-configuration/Smaller%20data%20set%20(1)%201cf1feeec5b780c4be25d8ed55a4130c.md)

Didn’t really work. 

# Break to fix RFI in the original dataset

Phase solutions showed diagonal traces, so cleaned RFI further in the original dataset.

[RFI 2A0335+096 part 2](https://www.notion.so/RFI-2A0335-096-part-2-1ce1feeec5b78092a76ce04cba4f7b0f?pvs=21) 

# Imaging 2A0335+096 part 2

Split and start again to see if phase calibration is better

```python
split(vis=msname,
      outputvis='imagetry2.ms',
      field='2', spw='16~47', correlation="LL,RR",
      datacolumn='corrected',
      width=8, timebin='30s'
      keepflags=False)
```

Reapply calibration

```python
applycal(vis=msname, field='2',
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=['1','1','0','0'],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False)
```

Then make the initial model and phase calibration

```python
tclean(vis="imagetry2.ms", imagename='2A0335+096-start',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.15mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[3840,3840], cell=['0.3arcsec','0.3arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')

gaincal(vis="imagetry2.ms", caltable=f'imagetry2.p0', 
        solint='inf', refant='ea22', gaintype='G', calmode='p', solnorm=False)
```

Looks good so we continue by applying and splitting to the new dataset.

```python
applycal(vis="imagetry2.ms", gaintable=['imagetry2.p0'])
split(vis=f'imagetry2.ms', outputvis=f'imagetry2-p0.ms', 
	datacolumn='corrected')
```

Run tclean again, reducing threshold to 0.08mJy

```python
tclean(vis="imagetry2-p0.ms", imagename='2A0335+096-p0',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.08mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Saw that the resolution was given as `Beam : 2.8137 arcsec, 2.02465 arcsec, 9.15468 deg` so I could use a pixel size of 0.5 arc seconds. For a width of 12’ we could go to 1440 pixels, or 1536 (2^9 * 3).

Then see how a new calibration turns out.

```python
gaincal(vis="imagetry2-p0.ms", caltable=f'imagetry2.p1', 
        solint='inf', refant='ea22', gaintype='G', calmode='p', solnorm=False)
```

Seems fine, other than a few antenna being flagged (which aren’t in the previous calibration)

```python
applycal(vis="imagetry2-p0.ms", gaintable=['imagetry2.p1'])
split(vis=f'imagetry2-p0.ms', outputvis=f'imagetry2-p1.ms', 
	datacolumn='corrected')
```

Then we can try cleaning again

```python
tclean(vis="imagetry2-p1.ms", imagename='2A0335+096-p1',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.08mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False, savemodel='modelcolumn')
```

Can do another round of self calibration. 

```python
gaincal(vis="imagetry2-p1.ms", caltable=f'imagetry2.p2', 
        solint='inf', refant='ea22', gaintype='G', calmode='p', solnorm=False)
applycal(vis="imagetry2-p1.ms", gaintable=['imagetry2.p2'])
split(vis=f'imagetry2-p1.ms', outputvis=f'imagetry2-p2.ms', 
	datacolumn='corrected')
```

Try cleaning, but also with briggs weighting. 

```python
tclean(vis="imagetry2-p2.ms", imagename='2A0335+096-p2',
	specmode='mfs', niter=20000, gain=0.1, threshold='0.08mJy',
	deconvolver='mtmfs', nterms=2,
	interactive=True, imsize=[1536, 1536], cell=['0.5arcsec','0.5arcsec'], pblimit=-1.e-6,
	stokes='I', weighting='briggs',robust=0.5,pbcor=False, savemodel='modelcolumn')
```