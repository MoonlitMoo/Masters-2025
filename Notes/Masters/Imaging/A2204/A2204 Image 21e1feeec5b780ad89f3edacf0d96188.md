# A2204 Image

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

![image-dirty.image.tt0-image-2025-06-30-10-42-19.png](A2204%20Image/image-dirty.image.tt0-image-2025-06-30-10-42-19.png)

Centre is approximately 8 mJy, tails to 1mJy. 

# First self calibration

Clipping

```python
flagdata('cconfig.ms', mode='clip', clipminmax=(0, 0.1))
flagdata('dconfig_1.ms', mode='clip', clipminmax=(0, 0.1))
flagdata('dconfig_2.ms', mode='clip', clipminmax=(0, 0.1))
```

```jsx
tclean(vis=["cconfig.ms", "dconfig_1.ms", "dconfig_2.ms"], 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

Antenna ea12 meh from C, ea11 good from D1, all good in D2.

```python
self_calibrate(1, 'ea11')
```

Assess spw results

- cconfig-p1
    - Drop 22,25,27,29,31 as they alternate all flagged and not for whatever reason.
    - Amp noise spw in remaining microwave, but lot of data left (>90%)
    - Phase calibration ~~[-40, 40] w/ spikes at 30~~31
- dconfig1-p1
    - Drop 10,21~29 90% flagged
    - Amp spikes around 8.2 & 10 GHz, but nothing major.
    - Phase calibration ~[-10, 10], spike in microwave
- dconfig2-p1
    - Drop 21~24,27~29 90% flagged
    - Amp noise at spw 25~26, spike in spw 10
    - Phase calibration ~[-10, 10], spike in microwave

```python
flagdata('cconfig-p1.ms', spw='22,25,27,29,31')
flagdata('dconfig1-p1.ms', spw='10,21~31')
flagdata('dconfig2-p1.ms', spw='22~24,27~31')

```

# Calibration 2

RMS was 4.3 uJy in first image, bring down to 10x.

```python
tclean(vis=["cconfig-p1.ms", "dconfig1-p1.ms", "dconfig2-p1.ms"], 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, 
	deconvolver='mtmfs', pblimit=-1.e-6,
	threshold='0.05mJy', scales=[0, 2, 4, 8],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

```python
self_calibrate(2, 'ea11')
```

- cconfig-p2
    - 21, 23 in review
    - Amp noise spw in remaining microwave, but lot of data left (>90%)
    - Phase calibration ~[-5, 5]
- dconfig1-p2
    - Spw 1 in review
    - Amp spikes around 8.2 & 10 GHz, but nothing major.
    - Phase calibration ~[-4, 4]
- dconfig2-p2
    - Spw 25,26 in review
    - Amp noise at spw 25~26, spike in spw 10
    - Phase calibration ~[-2, 2] up to double in microwave

# Calibration 3

RMS of previous image ~3.5 uJy, setting threshold to 20 uJy (5x). It’s putting some deep negative pixels in model of minihalo, seems like some small scale structure is being scaled out. Swapping to negative robust to try and isolate this. 

```python
tclean(vis=["cconfig-p2.ms", "dconfig1-p2.ms", "dconfig2-p2.ms"], 
	imagename='image-p2',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, 
	deconvolver='mtmfs', pblimit=-1.e-6,
	threshold='0.02mJy', scales=[0, 2, 4, 8], smallscalebias=0.5,
	stokes='I', weighting='briggs', robust=-0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

This worked better, still some negative points, but good enough for self calibration. Likely remove scale 8 and continue since there is a very close unresolved galaxy to the BCG (~8”).

- cconfig-p3
    - 21, 23 in review
    - Amp noise spw in remaining microwave, but lot of data left (>90%)
    - Phase calibration ~[-2, 2], spike at 10.6 GHz
- dconfig1-p3
    - Spw 1 in review
    - Amp spikes around 8.2 & 10 GHz, but nothing major.
    - Phase calibration ~[-2, 2], spike at 8.2 GHZ
- dconfig2-p3
    - Spw 25,26 in review, drop 21 (12% remains)
    - Amp noise at spw 25~26, spike in spw 10
    - Phase calibration ~[-1, 1], spike at 10.6 GHz

```python
flagdata('dconfig1-p3.ms', spw='21')
```

# Calibration 4

Get good negative robust model so that we can subtract outlier points and make a smaller image.

```python
tclean(vis=["cconfig-p3.ms", "dconfig1-p3.ms", "dconfig2-p3.ms"], 
	imagename='image-p3',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, 
	deconvolver='mtmfs', pblimit=-1.e-6,
	threshold='0.015mJy', scales=[0, 2, 4, 8], smallscalebias=0.5,
	stokes='I', weighting='briggs', robust=-0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

Small amount of interactive cleaning to model outlying points. We really only need a 7’x7’ region for the image, which at 0.5” cell size is ~864 cells.

Then selecting outer points for subtraction. No self-calibration this step, only subtraction.

# Calibration 5

Using the smaller image size.

```python
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"], 
	imagename='image-p4',
	imsize=[900, 900], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, 
	deconvolver='mtmfs', pblimit=-1.e-6,
	threshold='0.02mJy', scales=[0, 2, 4], smallscalebias=0.5,
	stokes='I', weighting='briggs', robust=-0.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

```python
self_calibrate(5, 'ea11')
```

- cconfig-p5
    - 21, 23 in review
    - Amp noise spw in remaining microwave, but lot of data left (>90%)
    - Phase calibration ~[-1, 1]
- dconfig1-p3
    - Spw 1 in review
    - Amp spikes around 8.2 & 10 GHz, but nothing major.
    - Phase calibration ~[-1, 1]
- dconfig2-p3
    - Spw 25,26 in review, drop 21 (12% remains)
    - Amp noise at spw 25~26, spike in spw 10
    - Phase calibration ~[-0.5, 1]

Looks good, moving to minihalo imaging.