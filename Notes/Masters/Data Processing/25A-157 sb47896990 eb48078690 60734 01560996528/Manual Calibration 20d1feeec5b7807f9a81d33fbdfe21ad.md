# Manual Calibration

# Pre-calibration flagging

Looking at primary calibration data, there is definite RFI. No spikes in time, spikes in frequency. Saved initial flags as `base_flagging`

- 10, wide spike + single channel spike, not narrow in time
- 11, two smaller freq spikes. Narrow in time
- 16, spike in first 2 channels, noise in time
- 21 wide noise, noise in time
- 22 wide noise, noise in time
- 25,26,27 noisy. Sharp in time
- 28 spikes, noise in time
- 29 serious spikes, noise in time
- 30, 31 tons of freq noise, spikes in time.

```python
# 10~11 
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='10~11' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False", 
	"mode='extend' field='0137+331=3C48' scan='23' spw='10~11' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
	"mode='extend' field='0137+331=3C48' scan='24' spw='10~11' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 16
flagdata(vis=msname, mode='manual', field='0137+331=3C48', spw='16:0~2')
# 21, 22
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='21,22' maxnpieces=5 timecutoff=2.5 freqcutoff=2.5 usewindowstats='sum' extendflags=False", 
	"mode='extend' field='0137+331=3C48' spw='21,22' scan='23' growtime=75.0 extendpols=True",
	"mode='extend' field='0137+331=3C48' spw='21,22' scan='24' growtime=50.0 extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 25~28 and 30,31 (30, 31 still have some time spikes)
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='25~28,30~31' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
  "mode='extend' field='0137+331=3C48' scan='23' spw='25~28,30~31' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
  "mode='extend' field='0137+331=3C48' scan='24' spw='25~28,30~31' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 29, not perfect but works for now
cmdlist = ["mode='manual' field='0137+331=3C48' spw='29:2;9;10;19;40'",
	"mode='tfcrop' field='0137+331=3C48' spw='29' maxnpieces=3 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
  "mode='extend' field='0137+331=3C48' scan='23' spw='29' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
  "mode='extend' field='0137+331=3C48' scan='24' spw='29' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Rest of channels
cmdlist = ["mode='tfcrop' field='0137+331=3C48' spw='0~9,12~15,17~20,23~24' maxnpieces=4 timecutoff=4.0 freqcutoff=4.0 extendflags=False",
	"mode='extend' field='0137+331=3C48' scan='23' spw='0~9,12~15,17~20,23~24' growtime=75.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True",
  "mode='extend' field='0137+331=3C48' scan='24' spw='0~9,12~15,17~20,23~24' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

Confused about the little bow at 9 GHz

![image.png](Manual%20Calibration/image.png)

Said weird bow is because antenna ea10 had a hardware issue in A2C2. This is one of the 3-bit sampler pairs which SHOULD correspond to spw 16~31, but flagging 0~15 is what actually fixed it. Either way, flagging all since unsure.

```python
flagdata(vis=msname, antenna='ea10', flagbackup=False)
```

🚩 **Saved flag as precalibration**

# Initial Primary Calibration

## Antenna positions

```python
gencal(vis=msname, caltable=f'{name}.antpos', caltype='antpos')
```

There are some antenna corrections

## Primary calibrator flux density scaling

Use the 3C48_X model for the source.

```python
setjy(vis=msname, field=p_calibrator, standard='Perley-Butler 2017', model='3C48_X.im', 
	usescratch=True, scalebychan=True)
```

## Basic phase calibration

Using custom func to grab spws to use for initial phase cal

```python
spw_string = get_initial_cal_spw_string(msname, p_calibrator, [i for i in range(32)], "plots")
spw_string = '0:21~23,1:18~20,2:24~26,3:49~51,4:7~9,5:29~31,6:51~53,7:8~10,8:6~8,9:31~33,10:11~13,11:52~54,12:8~10,13:24~26,14:44~46,15:23~25,16:28~30,17:12~14,18:10~12,19:31~33,20:17~19,21:32~34,22:39~41,23:29~31,24:49~51,25:36~38,26:41~43,27:10~12,28:52~54,29:26~28,30:14~16,31:44~46'
```

We can use ea12 as the reference antenna, since it’s centred and doesn’t drop out or have more flagging.

```python
gaincal(vis=msname, caltable=f'{name}.G0all', field=p_calibrator, refant='ea12', spw=spw_string,
	gaintype='G',calmode='p', solint='int', minsnr=5, gaintable=[f'{name}.antpos'])
```

It looks fine on a quick scan through, so we upgrade it to the real initial phase calibraiton

```python
gaincal(vis=msname, caltable=f'{name}.G0', field=p_calibrator, refant='ea12', spw=spw_string,
	gaintype='G',calmode='p', solint='int', minsnr=5, gaintable=[f'{name}.antpos'])
```

## Delay calibration

```python
gaincal(vis=msname, caltable=f'{name}.K0', field=p_calibrator, refant='ea12',
	spw='*:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5,
  gaintable=[f'{name}.antpos', f'{name}.G0'])
```

![image.png](Manual%20Calibration/image%201.png)

Once again, there a a couple out of the normal expected ranges. It kind of looks centred around -5 and mostly in +-5 ns. Bit wider than the previous data, I’ll let it slide for now. 

## Bandpass solution

```python
bandpass(vis=msname, caltable=f'{name}.B0', field=p_calibrator, 
	refant='ea12', combine='scan', solint='inf', bandtype='B', 
	gaintable=[f'{name}.antpos', f'{name}.G0', f'{name}.K0'])
```

Checking the bandpass amplitude solution via

```python
plotms(vis=f'{name}.B0', field=p_calibrator, xaxis='chan', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', gridrows=2, gridcols=2)
```

shows everything seems ok, a couple more unusual shapes, but all are pretty smooth. 

The phase solutions via 

```python
plotms(vis=f'{name}.B0',field=p_calibrator, xaxis='chan', yaxis='phase', coloraxis='corr',
	plotrange=[-1,-1,-180,180], iteraxis='antenna',gridrows=2,gridcols=2)
```

are pretty smooth and flat, with many offset significantly from 0. There are a few points (in SPW 29) that aren’t great, but assuming this is due to RFI which I will be smacking with rflag once a full initial calibration is built. 

## Gain solution

Now we apply a better gain solution based on the new calibrations. 

```python
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	interp=['', '', 'nearest'])
```

We’ll do a better one after rflag is run on the data again. 

## Applying initial calibration

```python
applycal(vis=msname, field=p_calibrator, 
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '', p_calibrator], interp=['', 'nearest', 'nearest', ''], 
	calwt=False, flagbackup=False)
```

# Flag primary with rflag

Removing model from calibrated data 

```python
uvsub(vis=msname
```

Then did a gentler flagging over all spw, though spw 10 needed a harder pass

```python
flagdata(vis=msname, mode='rflag', field=p_calibrator, spw='0~9,11~31', 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, extendflags=False,
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='rflag', field=p_calibrator, spw='10', 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, extendflags=False,
	datacolumn='corrected', action='apply', flagbackup=False)
```

Post-flagging. I could more heavily flag the last columns, but it looks better than previous dataset. 

![image.png](Manual%20Calibration/image%202.png)

🚩 **saved flags as primary_2**

# Initial Secondary Calibration

## Tfcrop flag secondary calibrator

Now we look to the secondary calibrator. Starting with a variety of tfcrop to clean up for the initial fluxscale. 

- 10-11 spikes in freq (multi scan)
- 12-12 noise in freq (one scan)
- 16 spike in freq (multi scan)
- 21-23, spikes in freq (multi scan)
- 24-25, noise in freq (multi scan)
- 26-27, noise in freq (single scan)
- 29~31, spikes in freq (multi scan)

```python
# 10~11 
cmdlist = ["mode='tfcrop' field='J0321+1221' spw='10~11' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False", 
	"mode='extend' field='J0321+1221' spw='10~11' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 12~14
cmdlist = ["mode='tfcrop' field='J0321+1221' spw='12~14' maxnpieces=4 timecutoff=3.0 freqcutoff=3.0 timefit='poly' extendflags=False", 
	"mode='extend' field='J0321+1221' spw='12~14' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 16
flagdata(vis=msname, mode='manual', field='J0321+1221', spw='16:0')
# 21~23
cmdlist = ["mode='tfcrop' field='J0321+1221' spw='21' maxnpieces=5 timecutoff=2.5 freqcutoff=2.5 usewindowstats='sum' extendflags=False", 
	"mode='tfcrop' field='J0321+1221' spw='22' maxnpieces=4 timecutoff=2.25 freqcutoff=2.25 usewindowstats='sum' extendflags=False", 
	"mode='tfcrop' field='J0321+1221' spw='23' maxnpieces=4 timecutoff=2.0 freqcutoff=2.25 usewindowstats='sum' extendflags=False", 
	"mode='extend' field='J0321+1221' spw='21~23' growtime=50.0 extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 25~28 and 30,31 (still not great, but workable into rflag)
cmdlist = ["mode='tfcrop' field='J0321+1221' spw='25~28,30~31' maxnpieces=4 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
  "mode='extend' field='J0321+1221' spw='25~28,30~31' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 29
cmdlist = ["mode='manual' field='J0321+1221' spw='29:1;2;9;18;19;40'",
	"mode='tfcrop' field='J0321+1221' spw='29' maxnpieces=3 timecutoff=2.5 freqcutoff=2.5 timefit='poly' extendflags=False",
	"mode='extend' field='J0321+1221' spw='29' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True extendpols=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

🚩 **Saved as ‘secondary’**

## Actual calibration

Get the gain calibration. We’ll do a phase only one for the secondary, following up with a better gain cal. 

```python
clearcal(vis=msname, field=s_calibrator)
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	interp=['', '', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
  spw='*:5~58', solint='int', refant='ea12', gaintype='G', calmode='p',
  gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
  interp=['', '', ''],
	append=True)
```

Better combined version

```python
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=['', p_calibrator, p_calibrator, p_calibrator], interp=['', '', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea12', gaintype='G', calmode='ap',
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['', p_calibrator, p_calibrator, s_calibrator], 
	interp=["", "nearest", "nearest", "linear"], 
	append=True)
```

Make the fluxscale based on this gain calibration, set into the model column.

```python
myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale1',
	reference=p_calibrator, transfer=[s_calibrator],
	incremental=False)
setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
```

Then make the final gain calibration

```python
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=['', p_calibrator, p_calibrator, p_calibrator], interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea12', gaintype='G', calmode='ap',
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['', p_calibrator, p_calibrator, s_calibrator], 
	interp=["", "nearest", "nearest", "linear"], 
	append=True)
```

Apply it to the secondary calibrator

```python
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0', f'{name}.antpos'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator, ''],
	interp=['linear', 'linear', 'nearest','nearest', ''],
	calwt=False)
```

# Flag secondary with rflag

```python
# 0~9, 11~22, 25~27 
flagdata(vis=msname, mode='rflag', field=s_calibrator, spw='0~9,11~22,25~27', 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
# 10, 23~24, 28
flagdata(vis=msname, mode='rflag', field=s_calibrator, spw='10,23~24,28', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
# 29~31
flagdata(vis=msname, mode='rflag', field=s_calibrator, spw='29~31', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
```

🚩**saved as secondary_2**

# Final secondary calibration

Just redo the previous calibration. Overwriting last parts `rm -r *.G1 *.G2 *.fluxscale1 *.G3`

```python
clearcal(vis=msname, field=s_calibrator)
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	interp=['', '', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
  spw='*:5~58', solint='int', refant='ea12', gaintype='G', calmode='p',
  gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
  interp=['', '', ''],
	append=True)
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=['', p_calibrator, p_calibrator, p_calibrator], interp=['', '', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea12', gaintype='G', calmode='ap',
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['', p_calibrator, p_calibrator, s_calibrator], 
	interp=["", "nearest", "nearest", "linear"], 
	append=True)
myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale1',
	reference=p_calibrator, transfer=[s_calibrator],
	incremental=False)
setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea12', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=['', p_calibrator, p_calibrator, p_calibrator], interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea12', gaintype='G', calmode='ap',
	gaintable=[f'{name}.antpos', f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['', p_calibrator, p_calibrator, s_calibrator], 
	interp=["", "nearest", "nearest", "linear"], 
	append=True)
```

Then apply the calibration to check everything is ok

```python
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0', f'{name}.antpos'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator, ''],
	interp=['linear', 'linear', 'nearest','nearest', ''],
	calwt=False)
```

# Flag 2A0335+096

Apply calibration to science field. 

```python
applycal(vis=msname, field="2A0335+096",
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0', f'{name}.antpos'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator, ''],
	interp=['linear', 'linear', 'nearest','nearest', ''],
	calwt=False)
```

RFI notes 

- 0~9,12~15,17~20,26 freq noise + small/narrow spikes
- 10~11, freq spikes tall/wide
- 16 freq spike first channel
- 21~23 freq noise/spike tall/wide
- 24~25,30~31 freq lots noise
- 27~29, freq spike+noise

```python
# 0~9, 12~20 
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='0~9,12~20', 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 10
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='10', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='10', 
	flagneartime=True, action='apply', flagbackup=False)
# 11
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='11', 
	freqdevscale=2.5, timedevscale=3.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 21~22
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='21~22', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 23
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='23', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='23', 
	flagnearfreq=True, flagneartime=True, action='apply', flagbackup=False)
# 24~26
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='24~26',
	freqdevscale=1.5, timedevscale=1.5, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
# 27
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='27', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 28
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='28', 
	freqdevscale=1.5, timedevscale=1.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='23', 
	flagnearfreq=True, flagneartime=True, action='apply', flagbackup=False)
# 29
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='29:8;18;35',
	action='apply', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='29',
	freqdevscale=0.8, timedevscale=0.8, extendpols=True, extendflags=False,
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='29', 
	growtime=50.0, growfreq=50.0, flagnearfreq=True, flagneartime=True, 
	action='apply', flagbackup=False)
# 30~31
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='30~31',
	freqdevscale=1.0, timedevscale=1.0, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
```

# Split off imaging data

## Finding limits

We want field 2A0335+096, spw *, correlations LL RR + averaging. 

- Max uvdist $B\approx~950m$
- max uvwave ~37500.
- VLA dish size is $D=25m$.
- Observing frequency is $[8, 12]$ GHz, central $10$ GHz.
- Total channels $32 \text{ spw } \times 64\text{ ch} = 2048$.
- Channel width $2 \text{ MHz}$.
- Time on source is 8 scans by ~8 minutes = $64$ minutes

### Calculate averaging

Bandwidth averaging approx $\Delta\nu = x\frac{\nu D}{4B}$ where $x$ is sensitivity (1, 4 smaller the more sensitive). High freq means we could probably do 4. 

$$
\begin{align*}
\Delta\nu &= x\frac{\nu D}{4B} \\
&= 4 \frac{8\times10^{9}\times 25}{4 \times 950}\\
&= 2.11 \times10^9\\
&= 2.11 \text{ GHz}
\end{align*}
$$

Then time averaging appox $\Delta t = x\frac{D}{4\omega B}$ with $\omega = \frac{2\pi}{24\times 3600}=7.27\times10^{-5} \text{ rad s}^{-1}$ (rotation speed of the earth). $x$ as 1 or 3.7 here. 

$$
\begin{align*}
\Delta t &= x \frac{D}{4\omega B}\\
&= 3.7 \frac{25}{4\times7.27\times10^{-5}\times950}\\
&= 335 \text{ s}
\end{align*}
$$

Can average over 16 channels, 60s. 

## Split command

```python
split(vis=msname,
      outputvis='dconfig_1.ms',
      field='2A0335+096', correlation="LL,RR",
      datacolumn='corrected',
      width=16, timebin='60s',
      keepflags=False)
```

## Notes

- keep freq averaging same as c-config, time averaging can be different
- 10/11 (mainly 10) still needs fiddling, same with last spw.

# Flagging 2A0335+096 again

## Rflag version 2

```python
# 0~9, 12~20 
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='0~9,12~20', 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 10 MORE
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='10:54;55;60', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='10', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=False, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='10', 
	flagnearfreq=True, action='apply', flagbackup=False)
# 11
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='11', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 21
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='21', 
	freqdevscale=2.5, timedevscale=2.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 22
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='22', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='22',
	growtime=50.0, growfreq=50.0, action='apply', flagbackup=False)
# 23 (do lhs, then all, helps rhs a lot) 
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='23:0~31', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='23', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 24 (get rid of some time spikes first, also in 25) MORE
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='24~25', timerange='01:23:43.5~01:23:49.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='24~25', timerange='01:26:01.5~01:26:07.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='24~25', timerange='01:28:16.5~01:28:25.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='24~25', timerange='01:30:34.5~01:30:40.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='24~25', timerange='01:32:49.5~01:32:58.5', 
	flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='24', 
	freqdevscale=1.0, timedevscale=1.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 25
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='25', 
	freqdevscale=2.0, timedevscale=2.0, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 26
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='26', 
	freqdevscale=1.75, timedevscale=1.75, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 27 (flag time spikes, also in 28) TOO HARD!!!
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='27~28', timerange='01:23:31.5~01:23:43.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='27~28', timerange='01:26:07.5~01:26:13.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='27~28', timerange='01:28:13.5~01:28:31.5', 
	flagbackup=False)
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='27~28', timerange='01:33:01.5~01:33:04.5', 
	flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='27', 
	freqdevscale=0.75, timedevscale=0.75, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 28 not enough
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='28', 
	freqdevscale=1.5, timedevscale=1.5, extendpols=True, extendflags=True, 
	datacolumn='corrected', action='apply', flagbackup=False)
# 29 (flag sharp channels) not enough
flagdata(vis=msname, mode='manual', field='2A0335+096', spw='29:2;4;9;19;36;46;40', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='29',
	freqdevscale=1.5, timedevscale=1.5, extendpols=True, extendflags=False,
	datacolumn='corrected', action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', field='2A0335+096', spw='29', 
	growtime=50.0, growfreq=50.0, flagnearfreq=True, flagneartime=True, 
	action='apply', flagbackup=False)
# 30~31 Not enough
flagdata(vis=msname, mode='rflag', field='2A0335+096', spw='30~31',
	freqdevscale=1.0, timedevscale=1.0, extendpols=True, extendflags=True,
	datacolumn='corrected', action='apply', flagbackup=False)
```

Time averaging 0

![image.png](Manual%20Calibration/image%203.png)

Time averaging 60s makes spw amplitudes smaller in surrounding cols? 

## AOFlagger

We only want to flag field 1 = 2A0335+096. Separated between the three regions of radar, microwave, and ok. 

```bash
aoflagger -fields 1 -strategy single.lua 25A-157.sb47896990.eb48078690.60734.01560996528.ms
```

![image.png](Manual%20Calibration/image%204.png)

Then there are still some spikes in the ML region so let’s see if we can make it better via shotgun of manual channel flagging.

```bash
flagdata(vis=msname, mode='manual', spw='23:26~34,24:25~46,26:58~61,28:0~4,29:0~27;61~63,30:38~42;59,31:48~63', flagbackup=False)
```

```bash
split(vis=msname,
      outputvis='dconfig_1.ms',
      field='2A0335+096', correlation="LL,RR",
      datacolumn='corrected',
      width=8, timebin='60s',
      keepflags=False)
```

![image.png](Manual%20Calibration/image%205.png)

**Note, I’ll increase channel binning to 16 when combining all datasets.** 

# Light flagging

See what happens when we do a much more relaxed sweep. (just using final sweep = 0.75)

![field_2A0335+096_spw_flagging.png](Manual%20Calibration/field_2A0335096_spw_flagging.png)

Only 80% flagging compares to 95%+.

![image.png](Manual%20Calibration/image%206.png)

# Using VLA Pipeline

Downloaded default script from the website https://science.nrao.edu/facilities/vla/data-processing/pipeline. 

Failed on getting a file for the tec maps, so added `show_tec_maps=False` for the `hifv_priorcals` function. 

## Calibrated Primary Calibrator

![image.png](Manual%20Calibration/image%207.png)

vs mine

![image.png](Manual%20Calibration/image%208.png)

## Calibrated Secondary Calibrator

![image.png](Manual%20Calibration/image%209.png)

vs mine

![image.png](Manual%20Calibration/image%2010.png)

## Calibrated Science Field

![image.png](Manual%20Calibration/image%2011.png)

vs mine

![image.png](Manual%20Calibration/image%2012.png)

## Flagging comparison

![all_fields_flagging.png](Manual%20Calibration/all_fields_flagging.png)

vs mine

![all_fields_flagging.png](Manual%20Calibration/all_fields_flagging%201.png)

# Calibration including apriori cals

Here we add in the extra analysis and the apriori calibrations as learnt from the pipeline.

```python
remove_calibration(name, 'gc')
gencal(vis=msname, caltable=f'{name}.gc', caltype='gc')
# Get the opacity calibration. We specify the spw string because the documentation said it was non-trivial :)
remove_calibration(name, 'opac')
tau = plotweather(vis=msname, doPlot=True, plotName='plots/weather.png')
spw_list = ','.join([str(i) for i in range(32)])
gencal(vis=msname, caltable=f'{name}.opac', caltype='opac', spw=spw_list, parameter=tau)
# Get the requantisation calibration
remove_calibration(name, 'rq')
gencal(vis=msname, caltable=f'{name}.rq', caltype='rq')
remove_calibration(name, 'antpos')
gencal(vis=msname, caltable=f'{name}.antpos', caltype='antpos')
```

## Initial calibration

Then we need the initial calibration. Applying this to the **primary_2** flag version

```python
# Set the flux model for the primary calibrator
setjy(vis=msname, field=p_calibrator, standard='Perley-Butler 2017', model='3C48_X.im',
	usescratch=True, scalebychan=True)
# Get inital phase calibration
remove_calibration(name, 'G0')
gaincal(vis=msname, caltable=f'{name}.G0', field=p_calibrator, refant=refant, 
	spw=spw_string, gaintype='G', calmode='p', solint='int', minsnr=5, 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos'])
# Get the delay calibration
remove_calibration(name, 'K0')
gaincal(vis=msname, caltable=f'{name}.K0', field=p_calibrator, refant=refant, 
	spw='*:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5, 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.G0'])
# Get the bandpass solution
remove_calibration(name, 'B0')
bandpass(vis=msname, caltable=f'{name}.B0', field=p_calibrator, refant=refant, 
	combine='scan', solint='inf', bandtype='B', 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.G0', f'{name}.K0'])
# Get a better amp + phase solution
remove_calibration(name, 'G1')
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58', 
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
```

### Applying

```python
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest', 'linear'],
	calwt=False, flagbackup=False)
```

### Plotting

```python
mkdir plots/initial_cal
mkdir plots/initial_cal/bandpass
mkdir plots/initial_cal/gain
check_flagging(msname, output_dir='plots/initial_cal')
# Delay
plotms(vis=f'{name}.K0', xaxis='antenna1', yaxis='delay', coloraxis='spw', 
	plotfile='plots/initial_cal/delay.png')
# Bandpass
plotms(vis=f'{name}.B0', xaxis='channel', yaxis='amp', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/initial_cal/bandpass/amp.png', 
	exprange='all')
plotms(vis=f'{name}.B0', xaxis='channel', yaxis='phase', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/initial_cal/bandpass/phase.png', 
	exprange='all')
# Gain
plotms(vis=f'{name}.G1', xaxis='freq', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', plotfile='plots/initial_cal/gain/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/initial_cal/spw_amp_calibrated.png')
```

## Final calibration

We will skip here because we have all the flagging done. 

```python
# DO PRIMARY
# Run the phase only calibration
remove_calibration(name, "G1")
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='p', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the phase + amp calibration
remove_calibration(name, "G2")
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the final gain calibration
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
# DO SECONDARY
# Clear any calibration in s_calibrator for cleanup
clearcal(vis=msname, field=s_calibrator)
# Extend the phase calibration, use interp as the default linear
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
	spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='p',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0'],
	append=True)
# Get the phase + amp calibration to create the flux model
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='ap',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'nearest'],
	append=True)
# Add the fluxmodel to secondary calibrator
remove_calibration(name, "fluxscale1")
myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale1',
	reference=p_calibrator, transfer=[s_calibrator],
	incremental=False)
setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
# Create the final gain calibration
gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
	spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='ap',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'nearest'],
	append=True)
```

### Applying calibrations

```python
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest', 'linear', 'linear'],
	calwt=False, flagbackup=False)
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
applycal(vis=msname, field='2A0335+096',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.antpos', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
```

### Plotting

```python
mkdir plots/final_primary_cal
# Gain phase
plotms(vis=f'{name}.G1', field=p_calibrator, xaxis='time', yaxis='phase', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/final_primary_cal/phase.png', exprange='all')
# Gain amp
plotms(vis=f'{name}.G3', field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', plotfile='plots/final_primary_cal/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/final_primary_cal/spw_amp_calibrated.png')
```

```python
mkdir plots/final_secondary_cal
# Gain phase
plotms(vis=f'{name}.G1', field=s_calibrator, xaxis='time', yaxis='phase', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/final_secondary_cal/phase.png', exprange='all')
# Gain amp
plotms(vis=f'{name}.G3', field=s_calibrator, xaxis='freq', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', plotfile='plots/final_secondary_cal/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=s_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/final_secondary_cal/spw_amp_calibrated.png')
```

```python
mkdir plots/2A0335+096_flagging
# Flagging plots
check_flagging(msname, output_dir='plots/2A0335+096_flagging')
# Amplitude plots
plotms(vis=msname, field='2A0335+096', xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/2A0335+096_flagging/spw_amp.png')
plotms(vis=msname, field='2A0335+096', xaxis='time', yaxis='amp', coloraxis='scan', 
	avgchannel='8', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/2A0335+096_flagging/time_amp.png')
# UV coverage plot
plotms(vis=msname, field='2A0335+096', xaxis='Uwave', yaxis='Vwave', coloraxis='spw', 
	avgchannel='8', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/2A0335+096_flagging/uwave_vwave.png')
plotms(vis=msname, field='2A0335+096', xaxis='UVdist', yaxis='amp', coloraxis='spw', 
	avgchannel='8', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/2A0335+096_flagging/uvdist_amp.png')
```

![spw_amp_calibrated.png](Manual%20Calibration/spw_amp_calibrated.png)

![spw_amp_calibrated.png](Manual%20Calibration/spw_amp_calibrated%201.png)

![spw_amp.png](Manual%20Calibration/spw_amp.png)

## Split final imaging data