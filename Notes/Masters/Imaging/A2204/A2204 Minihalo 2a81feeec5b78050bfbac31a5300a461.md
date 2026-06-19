# A2204 Minihalo

Red shift for A2204 is z = 0.152, which is 4 kpc per arcsec, which is then 2 kpc per cell. 

## Observation Data

- **cconfig** 3/2/2024
    - uvwave range  [0, 136000]
- **dconfig 1** 19/3/25
    - uvwave range [0, 35000]
- **dconfig 2** 27/3/25
    - uvwave range [0, 35000]

So 1 year between C and D configurations, 1 month between D configs.

## Last fixes

Uvrange data, dconfig2 looks like it has RFI. Flagging out last of the microwave, and two spikes.

```python
flagdata('dconfig2.ms', spw='10:3,21:3,25,26')
```

# Check point fluxes

Identified 

- S1 (Minihalo AGN): `"circle[[16h32m46.94s, 5d34m32.5s], 4arcsec]"`
- S2 (nearby galaxy): `"circle[[16h32m46.94s, 5d34m40.7s], 4arcsec]"`
- S3 (E): `"circle[[16h32m41.15s, 5d34m16.87s], 1.5arcsec]"`
- S4 (S): `"circle[[16h32m45.88s, 5d31m57.99s], 1.25arcsec]"`

```python
datasets = ['cconfig', 'dconfig1', 'dconfig2']
labels = ["S1", "S2", "S3", "S4"]
regions = ["circle[[16h32m46.94s, 5d34m32.5s], 4arcsec]",
           "circle[[16h32m46.94s, 5d34m40.7s], 4arcsec]",
           "circle[[16h32m41.15s, 5d34m16.87s], 3arcsec]",
           "circle[[16h32m45.88s, 5d31m57.99s], 2.5arcsec]"]
check_point_flux(datasets, regions, labels, 
	clean_params={"sidelobethreshold": 2.5})
```

The sidelobethreshold was skipped was only used for the C configuration data.

![flux_comparison.png](A2204%20Minihalo/flux_comparison.png)

![secondary_models.png](A2204%20Minihalo/secondary_models.png)

Secondary models align very closely, the point comparisons don’t show systematic variation.

# Subtracting point sources

Subtract large region around the source to include the mini nearby points. 

Subtraction was ok, not perfect. See if residual errors are from weird masked models.

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"], 
	imagename='minihalo',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=20000, gain=0.1, 
	deconvolver='mtmfs', pblimit=-1.e-6,
	threshold='0.02mJy', scales=[0, 2, 4, 8, 16],
	stokes='I', weighting='briggs', robust=1, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=2.5,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

Wideband corr

```python
widebandpbcor(vis="../full_image/cconfig-p4.ms", 
	imagename="minihalo", nterms=2, threshold="0.003mJy", pbmin=0.01,
	spwlist=list(range(32)), chanlist=[2]*32, weightlist=[1.0]*21 + [0.5]*11)
```

# High error estimate

BCG flux 11.1322 ± 1.2937