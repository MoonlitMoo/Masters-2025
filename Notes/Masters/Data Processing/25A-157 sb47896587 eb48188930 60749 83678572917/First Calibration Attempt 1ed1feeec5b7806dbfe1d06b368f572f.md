# First Calibration Attempt

# Flagging 0137+331=3C48

It’s field 0.

It has the weird bow from similar dataset, flagging ea10 fixed this again. 

```jsx
flagdata(vis=msname, antenna='ea10', flagbackup=False)
```

Running aoflagger with the script from the 25A-tab9 settings. 

- Full sweep with 3.0 as thresholds.
- Weather Radar with 1.75
- Microwave Link shifted to only band 29, thresholds at 1.5

Flagging graphs. Went from ~4% → 30% total. Secondary + science also modified since we killed ea10 (not shown)

![image.png](First%20Calibration%20Attempt/image.png)

![field_0137+331=3C48_antenna_flagging.png](First%20Calibration%20Attempt/field_01373313C48_antenna_flagging.png)

![field_0137+331=3C48_spw_flagging.png](First%20Calibration%20Attempt/field_01373313C48_spw_flagging.png)

# Initial Calibration

## Antenna positions

There isn’t any antenna position updates required here.

## Flux model

Setting flux model for primary calibrator

```jsx
setjy(vis=msname, field=p_calibrator, standard='Perley-Butler 2017', model='3C48_X.im', 
	usescratch=True, scalebychan=True)
```

## Initial Phase

Getting the initial cal string

```bash
spw_string = get_initial_cal_spw_string(msname, 0, [i for i in range(32)], "plots", 10)
spw_string = '0:27~29,1:16~18,2:10~12,3:20~22,4:20~22,5:26~28,6:33~35,7:10~12,8:21~23,9:51~53,10:6~8,11:51~53,12:25~27,1
3:46~48,14:12~14,15:33~35,16:20~22,17:39~41,18:38~40,19:30~32,20:48~50,21:32~34,22:13~15,23:39~41,24:35~37,25:30~32,
26:40~42,27:12~14,28:49~51,29:14~16,30:25~27,31:44~46'
```

**Note: Changed 10 (correct above) and 12, 29 could be a little funky, but kept.**

Using ea02 as the reference antenna, since it doesn’t seem to drop out and is central. 

```jsx
gaincal(vis=msname, caltable=f'{name}.G0all', field=p_calibrator, refant='ea02', spw=spw_string,
	gaintype='G',calmode='p', solint='int', minsnr=5)
```

Which seems mostly okay, so we can continue along. 

```jsx
gaincal(vis=msname, caltable=f'{name}.G0', field=p_calibrator, refant='ea02', spw=spw_string,
	gaintype='G',calmode='p', solint='int', minsnr=5)
```

## Delay Calibration

```jsx
gaincal(vis=msname, caltable=f'{name}.K0', field=p_calibrator, refant='ea02',
	spw='*:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5,
  gaintable=[f'{name}.G0'])
```

Seems fine apart from a couple weirder antenna

![image.png](First%20Calibration%20Attempt/image%201.png)

## Bandpass calibration

```jsx
bandpass(vis=msname, caltable=f'{name}.B0', field=p_calibrator, 
	refant='ea02', combine='scan', solint='inf', bandtype='B', 
	gaintable=[f'{name}.G0', f'{name}.K0'])
```

Checks

```jsx
plotms(vis=f'{name}.B0', field=p_calibrator, xaxis='chan', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', gridrows=2, gridcols=2)
```

```jsx
plotms(vis=f'{name}.B0',field=p_calibrator, xaxis='chan', yaxis='phase', coloraxis='corr',
	plotrange=[-1,-1,-180,180], iteraxis='antenna',gridrows=2,gridcols=2)
```

The solutions for the first antenna look kinda freaky. There are also some random points ~6 per antenna that are not great.

Observe: The Antenna ea01 Corkscrew

![image.png](First%20Calibration%20Attempt/image%202.png)

Manual flagged the majority of the weird points.

## Gain solution

```jsx
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0'],
	interp=['', 'nearest'])
```

## Applying initial calibration

```jsx
applycal(vis=msname, field=p_calibrator, 
	gaintable=[f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', p_calibrator], interp=['nearest', 'nearest', ''], 
	calwt=False, flagbackup=False)
```

Checking the quality and it isn’t good. 

![image.png](First%20Calibration%20Attempt/image%203.png)

# Flagging primary part 2

## Method 1

Try uvsub, rerun aoflagger (including initial primary flags), un uvsub

Added `flagdata(vis=msname, antenna='ea01', flagbackup=False)` 

- Benefits would be definitely removing anything from the first pass, now just focusing on the new data

![image.png](First%20Calibration%20Attempt/image%204.png)

![field_0137+331=3C48_antenna_flagging.png](First%20Calibration%20Attempt/field_01373313C48_antenna_flagging%201.png)

![field_0137+331=3C48_spw_flagging.png](First%20Calibration%20Attempt/field_01373313C48_spw_flagging%201.png)

Looks noisy but that should still be ok. **Choosing this to make the second calibration**

## Method 2

Restore base flagging, uvsub, aoflagger, un uvsub

- Potential benefits would be not removing anything that might be ok, but aoflagger got too excited about in the first uncalibrated pass

![image.png](First%20Calibration%20Attempt/image%205.png)

Looks better than uncalibrated pass, but still pretty crap. 

## Method 3

Run aoflagger on calibrated but not uvsubbed data

![image.png](First%20Calibration%20Attempt/image%206.png)

# Secondary flagging

![image.png](First%20Calibration%20Attempt/image%207.png)

```jsx
!aoflagger -fields 1 -strategy secondary.lua 25A-157.sb47896587.eb48188930.60749.83678572917.ms
```

![image.png](First%20Calibration%20Attempt/image%208.png)

![field_J0321+1221_spw_flagging.png](First%20Calibration%20Attempt/field_J03211221_spw_flagging.png)

![field_J0321+1221_antenna_flagging.png](First%20Calibration%20Attempt/field_J03211221_antenna_flagging.png)

## Initial full calibration

Phase only 

```jsx
clearcal(vis=msname, field=s_calibrator)
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='p', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0'],
	interp=['', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
  spw='*:5~58', solint='int', refant='ea02', gaintype='G', calmode='p',
  gaintable=[f'{name}.K0', f'{name}.B0'],
  interp=['', ''],
	append=True)
```

Amp + phase

```jsx
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=[p_calibrator, p_calibrator, p_calibrator], interp=['', '', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea02', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=[p_calibrator, p_calibrator, s_calibrator], 
	interp=["nearest", "nearest", "linear"], 
	append=True)
```

Add the flux model

```jsx
myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale1',
	reference=p_calibrator, transfer=[s_calibrator],
	incremental=False)
setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
```

Make the final gain calibration using phase only as reference + model from G2

```jsx
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=[p_calibrator, p_calibrator, p_calibrator], interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea02', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=[p_calibrator, p_calibrator, s_calibrator], 
	interp=["nearest", "nearest", "linear"], 
	append=True)
```

## Apply calibration to secondary

```jsx
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False, flagbackup=False)
```

![image.png](First%20Calibration%20Attempt/image%209.png)

## Flagging secondary 2

Using same method of applying calibration → uvsub → aoflagger (same script) → un uvsub. Seemed to give most reasonable results from primary attempt.

```jsx
uvsub(vis=msname)
!aoflagger -fields 1 -strategy secondary_2.lua -column "CORRECTED_DATA" 25A-157.sb47896587.eb48188930.60749.83678572917.ms
uvsub(vis=msname, reverse=True)
```

# Final calibration

```jsx
clearcal(vis=msname, field=s_calibrator)
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0'],
	interp=['', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
  spw='*:5~58', solint='int', refant='ea02', gaintype='G', calmode='p',
  gaintable=[f'{name}.K0', f'{name}.B0'],
  interp=['', ''],
	append=True)
```

```jsx
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=[p_calibrator, p_calibrator, p_calibrator], interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea02', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=[p_calibrator, p_calibrator, s_calibrator], 
	interp=["nearest", "nearest", "linear"], 
	append=True)
```

```jsx
myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale2',
	reference=p_calibrator, transfer=[s_calibrator],
	incremental=False)
setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
```

```jsx
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant='ea02', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield=[p_calibrator, p_calibrator, p_calibrator], interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
	spw='*:5~58', solint='inf', refant='ea02', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=[p_calibrator, p_calibrator, s_calibrator], 
	interp=["nearest", "nearest", "linear"], 
	append=True)
```

Then apply calibration

```jsx
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False)
```

# Flagging 2A0335+096

![image.png](First%20Calibration%20Attempt/image%2010.png)

![image.png](First%20Calibration%20Attempt/image%2011.png)

```jsx
!aoflagger -fields 2 -strategy science.lua 25A-157.sb47896587.eb48188930.60749.83678572917.ms
```

![image.png](First%20Calibration%20Attempt/image%2012.png)

![image.png](First%20Calibration%20Attempt/image%2013.png)

![field_2A0335+096_spw_flagging.png](First%20Calibration%20Attempt/field_2A0335096_spw_flagging.png)

![field_2A0335+096_antenna_flagging.png](First%20Calibration%20Attempt/field_2A0335096_antenna_flagging.png)

# Split imaging data

```jsx
applycal(vis=msname, field='2A0335+096',
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=[s_calibrator, s_calibrator, p_calibrator, p_calibrator],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False)
```

Losing 80% of data due to flagging. Checking what calibration is killing it off.

```jsx
split(vis=msname,
      outputvis='dconfig_2.ms',
      field='2A0335+096', correlation="LL,RR",
      datacolumn='corrected',
      width=8, timebin='60s',
      keepflags=False)
```