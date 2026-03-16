# RXJ2129+0005 Minihalo

# Check point flux

- Minihalo AGN (S1):
- S3: ENE point source
- S2: SW close point source

```python
datasets = ["cconfig", "cconfig2", "dconfig1", "dconfig2"]
labels = ["S1", "S3", "S2"]
regions = ["circle[[21h29m39.97s, 0d05m21.05s], 5arcsec]",
           "circle[[21h29m46.09s, 0d06m01.45s], 5arcsec]",
           "circle[[21h29m39.15s, 0d05m09.45s], 4arcsec]"]

check_point_flux(datasets, regions, labels)
```

![flux_comparison.png](RXJ2129+0005%20Minihalo/flux_comparison.png)

## Excluding cconfig1 due to bad phase solutions

Didn’t look into this one, but for whatever reason the calibration is bad.

This data was from **24A-411.sb45228321.eb45252099.60350.80962270833** which also has A2626 + ACTJ0022-0046 data. No problems with the others.

Including with imaging made the final result bad.

## Subtract points

Just the AGN.

# Image

```python
tclean(vis=["cconfig2_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"],
	imagename='minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=20000, gain=0.1, threshold='0.01mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16, 32],
	stokes='I', weighting='briggs', robust=1, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

```python
widebandpbcor(vis="../full_image/cconfig-p4.ms", 
	imagename="minihalo", nterms=2, threshold="0.0019mJy", pbmin=0.01,
	spwlist=list(range(30)), chanlist=[2]*30, weightlist=[1.0]*21 + [0.5]*9)
```

## Masking

The mask is shown in magenta in G19, so I estimated it with an ellipse. 

`"ellipse[[21h29m39.5s, +0d05m24.8s], [14.5arcsec, 29.5arcsec], 0deg]”`

Since this contains part of unsubtracted S2, I masked out the associated area.

`"circle[[21h29m39.1s, +0d05m9.8s], 5arcsec]"`

To get the flux density (~2-3x the 3sigma contour):

Error of region circle[[21h29m39.97s, 0d05m21.05s], 5arcsec] was 9.92e-05 Jy from 1.12e-05 Jy/beam for 8.9 beams
Flux 4.10e-04 +/- 1.04e-04
cal error: 2.05e-05, noise error: 2.46e-05, sub_error: 9.92e-05

## 3 sigma contour

Error of region circle[[21h29m39.97s, 0d05m21.05s], 5arcsec] was 9.92e-05 Jy from 1.12e-05 Jy/beam for 8.9 beams
Flux 1.51e-04 +/- 9.98e-05
cal error: 7.56e-06, noise error: 7.73e-06, sub_error: 9.92e-05