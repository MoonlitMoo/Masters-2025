# RXCJ1115+0129 Image

Using the same image proportions as the 2A0335+096 image which is ~19.2”.

The data was collected with channel averaging of 16, time averaging of 60s. 

# Dirty Image

```jsx
tclean(vis=["cconfig.ms", "dconfig_1.ms", "dconfig_2.ms"], 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='natural',robust=0.5,pbcor=False)
```

# First self calibration

```jsx
tclean(vis=["cconfig.ms", "dconfig_1.ms", "dconfig_2.ms"], 
	imagename='image-p0',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.1mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='natural', robust=0.5, pbcor=False, 
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

```jsx
self_calibrate(1, 'ea11')
```

- cconfig-p1
    - Drop 30~31.
    - Amp noise spw 21~31 up to ~0.5.
    - Phase calibration [-50, 50] up to [-100, 100] at high freq.
- dconfig1-p1
    - Drop 24,26,28~29 less than 35% remaining.  Review 23,25,27
    - High noise 10.7-12 GHz, up to ~40.
    - Phase calibration [-50, 50] up to [-150, 150] at high freq.
- dconfig2-p1
    - drop 23,24,26,28,29 less than 35% remaining. 22,27 in review
    - High noise 10.7-12 GHz, up to ~17.5.
    - Phase calibration [-50, 50] up to [-150, 150] at high freq.

```jsx
flagdata('cconfig-p1.ms', spw='30~31', flagbackup=False)
flagdata('dconfig1-p1.ms', spw='24,26,28,29', flagbackup=False)
flagdata('dconfig2-p1.ms', spw='23,24,26,28,29', flagbackup=False)
flagdata('cconfig-p1.ms', mode='clip', clipminmax=[0, 0.15], flagbackup=False)
flagdata('dconfig1-p1.ms', mode='clip', clipminmax=[0, 0.15], flagbackup=False)
flagdata('dconfig2-p1.ms', mode='clip', clipminmax=[0, 0.15], flagbackup=False)
```

# Second Calibration

Try for point models with negative robust. RMS 4.5 uJy, not going too deep as testing.

```jsx
tclean(vis=["cconfig-p1.ms", "dconfig1-p1.ms", "dconfig2-p1.ms"], 
	imagename='image-p1',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.02mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=-0.5, pbcor=False, 
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

```jsx
self_calibrate(2, 'ea11')
```

- cconfig-p2
    - Drop 29
    - Amp noise spw 21~31 up to ~0.14.
    - Phase calibration [-10, 10] up to [-50, 100] at spike ~11 GHz
- dconfig1-p2
    - Review 23,25,27
    - Noise 10.7-12 GHz, up to ~14 + spike at 9.4. Clip to 0.08.
    - Phase calibration [-5, 5] up to [-20, 20] at high freq.
- dconfig2-p2
    - Drop 27 less than 35% remaining. 22 in review
    - Noise 10.7-12 GHz, up to ~0.14, spike at 9.4. Clip to 0.08
    - Phase calibration [-5, 5] up to [-40, 80] at high freq spikes.

```jsx
flagdata('cconfig-p2.ms', spw='29', flagbackup=False)
flagdata('dconfig2-p2.ms', spw='27', flagbackup=False)
flagdata('dconfig1-p2.ms', mode='clip', clipminmax=[0, 0.08], flagbackup=False)
flagdata('dconfig2-p2.ms', mode='clip', clipminmax=[0, 0.08], flagbackup=False)
```

# Calibration 3

Last image was good, sources seem small. RMS was 4.2 uJy. Use positive robust to see if we stay reasonable.

```jsx
tclean(vis=["cconfig-p2.ms", "dconfig1-p2.ms", "dconfig2-p2.ms"], 
	imagename='image-p2',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
	stokes='I', weighting='briggs', robust=0.5, pbcor=False, 
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
	savemodel='modelcolumn')
```

```jsx
self_calibrate(3, 'ea11')
```

- cconfig-p3
    - Drop 29
    - Amp noise spw 21~31 up to ~0.14.
    - Phase calibration [-5, 5] up to [-40, 20] at spike ~11 GHz
- dconfig1-p3
    - Review 23,25,27
    - Noise 10.7-12 GHz, up to ~14 + spike at 9.4. Clip to 0.08.
    - Phase calibration [-5, 5] up to [-20, 20] at high freq.
- dconfig2-p3
    - 22 in review
    - Noise 10.7-12 GHz, up to ~0.14, spike at 9.4. Clip to 0.08
    - Phase calibration [-2, 2] up to [-20, 2] at high freq spikes.

# Calibration 4

Model is good, try for deeper clean to pick up minihalo. RMS was 2.6 uJy. 

The cconfig data has minihalo AGN ~25% lower flux than the dconfig sets. The SE point is still a little scuffed. Might need some extra attention.

Try rerun the cleaning without ssb after clearing that model point.

```jsx
tclean(vis=["cconfig-p3.ms", "dconfig1-p3.ms", "dconfig2-p3.ms"],
  imagename='image-p3',
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=20000, gain=0.1, threshold='0.01mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8], smallscalebias=0.5,
  stokes='I', weighting='briggs', robust=0.5, pbcor=False,
  usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
  lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
  savemodel='modelcolumn')
```

```python
for m in ["p3-input.tt0", "p3-input.tt1"]:
	ia.open(m)
	data = ia.getchunk(blc=[782, 916], trc=[961, 1037])
	data *= 0 
	ia.putchunk(pixels=data, blc=[782, 916])
	ia.close()
```

```python
tclean(vis=["cconfig-p3.ms", "dconfig1-p3.ms", "dconfig2-p3.ms"],
  imagename='image-p3-2', startmodel=["p3-input.tt0", "p3-input.tt0"], restart=False,
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=20000, gain=0.1, threshold='0.01mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
  stokes='I', weighting='briggs', robust=0.5, pbcor=False,
  usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
  lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
  savemodel='modelcolumn')
```

```jsx
self_calibrate(4, 'ea11')
```

- cconfig-p4
    - 22~24 in review.
    - Amp noise spw 21~31 up to ~0.14, spike at 10 GHz.
    - Phase calibration [-5, 5] up to [-60, 60] at spike ~11 GHz
- dconfig1-p4
    - Review 23,25,27
    - Noise 10.7-12 GHz, up to ~0.08 + spike at 9.4.
    - Phase calibration [-2, 2] up to [-20, 20] at high freq + spike.
- dconfig2-p4
    - 22 in review
    - Noise 10.7-12 GHz, up to ~0.14, spike at 9.4.
    - Phase calibration [-2, 2] up to [-10, 30] at noise.

# Final Image

Try and get a good image to make sure self calibration is all okay. Last RMS was 2.7 uJy. The SE point might need extra attention, or individual self cal. Maybe try delete model in that region, redo with larger scale bias?

```jsx
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"],
  imagename='image-p4',
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=20000, gain=0.1, threshold='0.008mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8], smallscalebias=0.5,
  stokes='I', weighting='briggs', robust=0.5, pbcor=False,
  usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
  lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False,
  savemodel='modelcolumn')
```

## Trying with startmodel

Clearing the SE point from the model, then restarting without scalebias since that worked better for SE from memory. Didn’t work for whatever reason, fine to final image in any case.

```python
nterms = 2
fm = [f"image-p4.model.tt{i}" for i in range(nterms)]
im = [f"startmodel.model.tt{i}" for i in range(nterms)]
for fm, im in zip(fm, im):
	os.system(f"cp -r {fm} {im}")
	ia.open(im)
	data = ia.getchunk(blc=[756, 885], trc=[888, 1005])
	data *= 0
	ia.putchunk(pixels=data, blc=[756, 885])
	ia.close()
```

```python
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"],
  imagename='image-p4-2', startmodel=['startmodel.tt0', 'startmodel.tt1'], restart=False
  imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
  specmode='mfs', niter=20000, gain=0.1, threshold='0.008mJy',
  deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8],
  stokes='I', weighting='briggs', robust=0.5, pbcor=False,
  usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
  lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```