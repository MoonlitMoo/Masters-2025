# Full image RFI checking

Cleaning the data more carefully.

# Check only noise image

First we want to check what the data would look like if it was pure noise, no RFI. Copy into a new test ms so that we can replace all visibility measurements with gaussian sampled noise.

```python
cp -r cconfig.ms test.ms
```

To get the estimate of the noise we can use the [VLA Exposure Calculator](https://obs.vla.nrao.edu/ect/)

Via Yvette this is $1.7243\sqrt{n_{chan}}$, not that I can recreate it. 

```python
import numpy as np

rms_per_vis = 395

ms.open('test.ms', nomodify=False)
data = ms.getdata(['data'], average=False, ifraxis=True)
print(f"Loaded data shape: {data['data'].shape}, average: {np.average(data['data'], axis=None)}")

rand_re=np.random.normal(size=data['data'].shape) * rms_per_vis*1e-3 # in Jy
rand_im=np.random.normal(size=data['data'].shape) * rms_per_vis*1e-3 # in Jy

data['data'] = rand_re + 1j*rand_im # replace the existing data with noise
print(f"Altered data shape: {data['data'].shape}, average: {np.average(data['data'], axis=None)}")

ms.putdata(data)
ms.close()

```

Then we can run tclean to see what the image would look like (dirty). This [`test.ms`](http://test.ms) is the copied cconfig from the first full image. 

```python
tclean(vis=["test.ms"], 
	imagename='image-dirty',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'], 
	specmode='mfs', niter=0, gain=0.1, threshold='1.0mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	interactive=True, 
	stokes='I', weighting='briggs',robust=1.5,pbcor=False)
```

# Cleaning C config

## Initial corrected dataset

Un-averaged

![image.png](Full%20image%20RFI%20checking/image.png)

![field_RXJ1720+2638_spw_flagging.png](Full%20image%20RFI%20checking/field_RXJ17202638_spw_flagging.png)

16 channel, 60 s averaging emulating the split call.

![image.png](Full%20image%20RFI%20checking/image%201.png)

Updating the flagging code to increase flagging in weather and microwave regions.

- Weather 2 → 1
- Microwave 0.8 → 0.75

# Cleaning D config 1

![image.png](Full%20image%20RFI%20checking/image%202.png)

![field_RXJ1720.1+2638_spw_flagging.png](Full%20image%20RFI%20checking/field_RXJ1720.12638_spw_flagging.png)

![image.png](Full%20image%20RFI%20checking/image%203.png)

# Cleaning D config 2

![image.png](Full%20image%20RFI%20checking/image%204.png)

![field_RXJ1720.1+2638_spw_flagging.png](Full%20image%20RFI%20checking/field_RXJ1720.12638_spw_flagging%201.png)

![image.png](Full%20image%20RFI%20checking/image%205.png)

# Flagging

Trying various levels of flagging and inspecting %, averaging etc, nothing seems to make it especially better. Sometimes it gets worse.

Honestly the cconfig is the lightest offender so we can ignore it for now and try bring the other two into submission.

This can be done by killing the spike at 9.4 GHz and then killing the last couple spws. Since it is constant through time, have to do this frequency wise. Using the uvsub models since we are just flagging spw instead of flagging points, means we don’t need to re-phase correct etc.

 

```python
flagdata('dconfig1.ms', spw='10,29~31', flagbackup=False)
flagdata('dconfig2.ms', spw='10,29~31', flagbackup=False)
```

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"]
	imagename='image-r1.5-ssb-0.5',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=-0.5,
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

No real difference in background patterns. Not perfect, but good enough to see that the removal doesn’t make life better.

Got a flux density of  $9.29 \pm 0.49 \>mJy$ with an RMS of $5.15 \> \mu Jy$. 

## Blitzkreig

Destroy all the bad spws, see if the background improves. Ignoring image quality here.

```python
flagdata('cconfig_uvsub.ms/', spw='10,22~31', flagbackup=False)
flagdata('dconfig1_uvsub.ms/', spw='10,22~31', flagbackup=False)
flagdata('dconfig2_uvsub.ms/', spw='10,22~31', flagbackup=False)
```

```python
tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"]
	imagename='image-r1.5-ssb-0.5-blitzkreig',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=10000, gain=0.1, threshold='0.015mJy',
	deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=-0.5,
	stokes='I', weighting='briggs', robust=1.5, pbcor=False,
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
```

Got a flux density of $8.89 \pm 0.46 \>mJy$ with an RMS of $4.17 \> \mu Jy$.

```python
def do_check(msname):
	pre_sum = flagdata(vis=msname, mode="summary")
	flagdata(msname, spw='10,22~31', flagbackup=False)
	post_sum = flagdata(vis=msname, mode="summary")
	pre_unflagged = pre_sum['total'] - pre_sum['flagged']
	print(f"Pre data: {pre_unflagged}")
	post_unflagged = post_sum['total'] - post_sum['flagged']
	print(f"Post data: {post_unflagged}")
	print(f"Increase in flagging: {post_sum['flagged'] / pre_sum['flagged'] * 100 - 100}")
	print(f"Decrease in data: {post_unflagged / pre_unflagged * 100 - 100}")
```

Image definitely looks better, but we did also just take 10 spw out behind the shed. ~ 1/3. Worth checking how much we are actually killing

- cconfig flagged
    
    Pre data: 1619876.0
    
    Post data: 1617708.0
    
    Increase in flagging: 0.05679014156672224
    
    Decrease in data: -0.13383740483840256
    
- dconfig1
    
    Pre data: 1390460.0
    
    Post data: 1387376.0
    
    Increase in flagging: 0.2644622429554033
    
    Decrease in data: -0.22179710311695544
    
- dconfig2
    
    Pre data: 1788992.0
    
    Post data: 1786520.0
    
    Increase in flagging: 0.24873219029220195
    
    Decrease in data: -0.138178370836755
    

Ok so the number of flagged points increases by less than a percent because they are already almost flagged out.