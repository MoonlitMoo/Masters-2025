# First calibration

# RFI

## Dealing with the RFI Field 0

SPW 16~38 all similar looking. No massive RFI spikes etc, just some stuff I’m not sure about in the first 1.5 minutes of observation. SPW 32 does have some scatter above the 0.12 amplitude mark, extending to about 0.15. This seems to be primarily localised to the first two channels.

![image.png](First%20calibration/image.png)

SPW 39~43 (not SPW 42) exhibits what I would call RFI. Locating this in channels 45~64.

- Can find good look at 3C48, scan 5, ea04&&ea05.
- Short time burst, wide frequency.

![image.png](First%20calibration/image%201.png)

SPW 26, 27 have some RFI as well. 

SPW 45 is super noisy for some reason. Might bleed a little into 44, 46~47, but closer to the noise in SPW 32. 

- Primary RFI channels are 11,12. Gaussian-like bleed around it.
- Sharp points in the 43, 45, 53, 54
- Occurs throughout entirety of scans

![image.png](First%20calibration/image%202.png)

```python
# Flag first two channels of SPW 32
flagdata(vis=msname, mode='manual', field='0', spw='32:0~1', flagbackup=False)
# Deal with channels 26, 27. Remove ch 60, then sweep. 
cmdlist = ["mode='manual' field='0' spw=26:60", 
	"mode='tfcrop' field='0' spw='26~27' freqdevscale=3.0 timecutoff=2.5 extendflags=False extendpols=True", 
	"mode='extend' field='0' spw='26~27' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Deal with the RFI in 39~43, note still a little in 39,43
cmdlist = ["mode='tfcrop' field='0' spw='39~43' freqdevscale=3.0 timecutoff=2.5 extendflags=False", 
	"mode='extend' field='0' spw='39~43' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Dealing with RFI in 45, first remove worst channels, then TFcrop
cmdlist = ["mode='manual' field='0' spw='45:6~16'", 
  "mode='tfcrop' field='0' spw='45' freqcutoff=2.0 timecutoff=2.5 extendflags=False extendpols=True", 
  "mode='extend' field='0' spw='45' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Deal with the remaining columns 44, 46, 47
cmdlist = ["mode='tfcrop' field='0' spw='44,46,47' freqcutoff=3.0 timecutoff=2.5 extendflags=False extendpols=True", 
	"mode='extend' field='0' spw='44,46,47' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

## Dealing with the RFI Field 1

- 20 tiny spike
- 26, 27 big spikes
- 32~38 low noise
- 39 big spike + low noise
- 40~47 low noise + few spikes. 45 big spike

```python
# Deal with 20
flagdata(vis=msname, mode='tfcrop', field='1', spw='20', flagbackup=False)
# Deal with 26, 27
cmdlist = ["mode='manual' field='1' spw='26:53~56'",
	"mode='tfcrop' field='1' spw='26, 27' freqdevscale=3.0 timecutoff=2.5 extendflags=False",
	"mode='extend' field='1' spw='26,27' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Deal with 32~38
cmdlist = ["mode='tfcrop' field='1' spw='32~38' freqdevscale=3.0 timecutoff=2.5 extendflags=False", 
	"mode='extend' field='1' spw='32~38' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Deal with 39
cmdlist = ["mode='tfcrop' field='1' spw='39' freqdevscale=3.0 timecutoff=2.5 extendflags=False extendpols=True",
	"mode='extend' field='1' spw='39' growtime=50.0 growfreq=50.0 flagnearfreq=True flagneartime=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Deal with 45
cmdlist = ["mode='manual' field='1' spw='45:11~12'",
	"mode='tfcrop' field='1' spw='39' freqdevscale=3.0 timecutoff=2.5 extendflags=False extendpols=True",
	"mode='extend' field='1' spw='39' growtime=50.0 growfreq=50.0 flagnearfreq=True flagneartime=True"]

# Deal with 40-47
cmdlist = ["mode='tfcrop' field='1' spw='40~44,46~47' freqdevscale=2.5 timecutoff=2.5 extendflags=False extendpols=True",
	"mode='extend' field='1' spw='40~44,46~47' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

![image.png](First%20calibration/image%203.png)

# Initial Calibration

### Antenna correction

From earlier I know that there aren’t any antenna positions that need to be corrected. 

“Got error as “No offsets found”,  when using `gencal` with `antpos` assuming this means that antenna positions are correct.”

### Flux density scaling

Use the primary calibrator to set the flux density scaling. Used 3C48_X for all channels, unsure if 3C48_C would be better for lower spectral windows.

```python
setjy(vis=msname, field='0', standard='Perley-Butler 2017', model='3C48_X.im', 
	usescratch=True, scalebychan=True)
```

### Initial phase calibration

Now make an initial phase calibration using the primary calibrator. First we grab a couple decent columns from all the spw. I used my custom function to do this for me. 

```python
spw_string = get_initial_cal_spw_string(msname, 0, [i for i in range(16, 48)], "plots")
spw_string = '16:27~29,17:17~19,18:24~26,19:25~27,20:7~9,21:27~29,22:16~18,23:41~43,24:5~7,25:32~34,26:20~22,27:12~14,28:6~8,29:23~25,30:51~53,31:46~48,32:19~21,33:38~40,34:15~17,35:21~23,36:48~50,37:33~35,38:15~17,39:35~37,40:48~50,41:53~55,42:56~58,43:26~28,44:52~54,45:48~50,46:25~27,47:44~46'
```

![image.png](First%20calibration/image%204.png)

From this any are good to select since none seem to drop out. ea22 is pretty close to the centre so this will be the reference antenna.

```python
gaincal(vis=msname, caltable=f'{name}.G0all', field='0', refant='ea22', spw=spw_string,
	gaintype='G',calmode='p', solint='int', minsnr=5)
```

Then iterating through each spw and antenna, with manual flagging. Save the versions as pre/post_phase via flagmanager. **This was done wrong I think**

[Phase flagging (1)](First%20calibration/Phase%20flagging%20(1)%201f11feeec5b78066bb78ea9c47a92cb9.md)

### Phase calibration 2

```python
gaincal(vis=msname, caltable=f'{name}.G0', field='0', refant='ea22', spw=spw_string, 
	calmode='p', solint='int', minsnr=5)
```

### Delay solution

Then we do delay solution

```python
gaincal(vis=msname, caltable=f'{name}.K0', field='0', refant='ea22',
	spw='16~47:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5,
  gaintable=[f'{name}.G0'])
```

Check via the following. Some of the solutions >4ns which is weird. Maybe flag antenna?

```python
plotms(vis=f'{name}.K0',xaxis='antenna1',yaxis='delay',coloraxis='baseline')
```

![image.png](First%20calibration/image%205.png)

### Bandpass solution

```python
bandpass(vis=msname, caltable=f'{name}.B0', field='0', spw='16~47', 
	refant='ea22', combine='scan', solint='inf', bandtype='B', 
	gaintable=[f'{name}.G0', f'{name}.K0'])
```

With checks

```python
plotms(vis=f'{name}.B0', field='0', xaxis='chan', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', gridrows=2, gridcols=2)
plotms(vis=f'{name}.B0',field='0', xaxis='chan', yaxis='phase', coloraxis='corr',
	plotrange=[-1,-1,-180,180], iteraxis='antenna',gridrows=2,gridcols=2)	
```

### Gain calibration

First step is the complex amplitude and phase gains for the primary calibrator. 

```python
gaincal(vis=msname, caltable=f'{name}.G1', field='0', spw='16~47:5~58',
        solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
        gaintable=[f'{name}.K0', f'{name}.B0'],
        interp=['', 'nearest'])
```

Then we can add the secondary calibrator. 

```python
gaincal(vis=msname, caltable=f'{name}.G1', field='1',
        spw='16~47:5~58', solint='inf', refant='ea22', gaintype='G', calmode='ap',
        gaintable=[f'{name}.K0', f'{name}.B0'],
				append=True)
```

Checks performed via

```python
plotms(vis=f'{name}.G1', xaxis='time', yaxis='phase', correlation='/', coloraxis='baseline', plotrange=[-1,-1,-180,180], iteraxis='spw')
```

### Full set of commands

Flag state is `after_field1`

```python
setjy(vis=msname, field='0', standard='Perley-Butler 2017', model='3C48_X.im', 
        usescratch=True, scalebychan=True)
spw_string = get_initial_cal_spw_string(msname, 0, [i for i in range(16, 48)], "plots")
gaincal(vis=msname, caltable=f'{name}.G0all', field='0', refant='ea22', spw=spw_string,
        gaintype='G',calmode='p', solint='int', minsnr=5)
gaincal(vis=msname, caltable=f'{name}.G0', field='0', refant='ea22', spw=spw_string, 
        calmode='p', solint='int', minsnr=5)
gaincal(vis=msname, caltable=f'{name}.K0', field='0', refant='ea22',
        spw='16~47:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5,
  gaintable=[f'{name}.G0'])
bandpass(vis=msname, caltable=f'{name}.B0', field='0', spw='16~47', 
        refant='ea22', combine='scan', solint='inf', bandtype='B', 
        gaintable=[f'{name}.G0', f'{name}.K0'])
gaincal(vis=msname, caltable=f'{name}.G1', field='0', spw='16~47:5~58',
        solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
        gaintable=[f'{name}.K0', f'{name}.B0'],
        interp=['', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field='1',
        spw='16~47:5~58', solint='inf', refant='ea22', gaintype='G', calmode='ap',
        gaintable=[f'{name}.K0', f'{name}.B0'], append=True)
```

## Applying calibration

To primary to check quality

```python
applycal(vis=msname, field='0',gaintable=[f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '0'], interp=['nearest', 'nearest'], calwt=False)
```

![image.png](First%20calibration/image%206.png)

# RFlag for Field 0

[rflag testing (1)](First%20calibration/rflag%20testing%20(1)%201f11feeec5b7805aa0a6dc85ddcc89f1.md)

Now we subtract the model so that we can perform `rflag` on the calibrated data. Need to do this since `rflag` assumes that your data has a flat base. 

Really, the bit we want to focus on is 26 and 39+. We’ll ignore the tiny bit in 27

```python
uvsub(vis=msname)
# Deal with SPW 26, split into 2 timeranges since otherwise it flags everything in the lower
flagdata(vis=msname, mode='rflag', field='0', spw='26', timerange="<2024/01/27/01:50:45", 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, datacolumn='corrected', 
	action='apply', flagbackup=False)
flagdata(vis=msname, mode='rflag', field='0', spw='26', timerange=">2024/01/27/01:50:45", 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, datacolumn='corrected', 
	action='apply', flagbackup=False)
# Then SPW 37~42. but 39~41 also need to be split into 2
flagdata(vis=msname, mode='rflag', field='0', spw='37~38', freqdevscale=3.5, 
	timedevscale=3.5, extendpols=True, datacolumn='corrected', action='apply', 
	flagbackup=False)
flagdata(vis=msname, mode='rflag', field='0', spw='39~41', timerange=">2024/01/27/01:50:45", 
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, datacolumn='corrected', 
	action='apply', flagbackup=False)
# Now for the last section, 43, 46, 47 all need to be split for the second timerange
flagdata(vis=msname, mode='rflag', field='0', spw='43,46,47', timerange=">2024/01/27/01:50:45",
	freqdevscale=3.5, timedevscale=3.5, extendpols=True, datacolumn='corrected',
	action='apply', flagbackup=False)
# And 44 is default
flagdata(vis=msname, mode='rflag', field='0', spw='44', freqdevscale=3.5, timedevscale=3.5, 
	extendpols=True, datacolumn='corrected',action='apply', flagbackup=False)
# 45 is special and I couldn't get it nicer
uvsub(vis=msname, reverse=True)
```

# Final Field0 calibration

```python
# Gain calibration
gaincal(vis=msname, caltable=f'{name}.G1', field='0', spw='16~47:5~58',
  solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
  gaintable=[f'{name}.K0', f'{name}.B0'],
  interp=['', 'nearest'])
gaincal(vis=msname, caltable=f'{name}.G1', field='1',
  spw='16~47:5~58', solint='inf', refant='ea22', gaintype='G', calmode='ap',
  gaintable=[f'{name}.K0', f'{name}.B0'],
	append=True)
```

And then the reapply

```python
applycal(vis=msname, field='0',gaintable=[f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '0'], interp=['nearest', 'nearest'], calwt=False)
```

```python
applycal(vis=msname, field='1',gaintable=[f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '1'], interp=['nearest', 'nearest'], calwt=False)

```

## Create flux scale

```python
myscale = fluxscale(vis=msname,	caltable=f'{name}.G1', 
	fluxtable=f'{name}.fluxscale1',	reference='0', transfer=['1'], 
	incremental=False)
```

## Calibrate secondary calibrator

```python
applycal(vis=msname, field='1', 
	gaintable=[f'{name}.fluxscale1', f'{name}.K0', f'{name}.B0'],
         gainfield=['1','',''], 
         interp=['nearest','nearest','nearest'],
         calwt=False)
```

# Rflag for Field 1

Now we want to clean up the secondary calibrator using rflag. First we need to set up the residuals

```python
# First yoink the flux scale into a model
for i in range(16, 48):
	fluxval = myscale["1"][str(i)]['fluxd']
  setjy(vis=msname, field='1', spw=str(i), standard='manual', fluxdensity=fluxval)
# The spw 45 model looks bad, so I'll just interpolate it
interpolated_flux = (myscale["1"][44]['fluxd'] + myscale["1"][46]['fluxd']) / 2
setjy(vis=msname, field='1', spw='45', standard='manual', fluxdensity=interpolated_flux)

# Then subtract it
uvsub(vis=msname)
```

Now we can actually smack the bad spw/channels

```python
# Smack a little bit of spw 16, since the first channelis bad
flagdata(vis=msname, mode='manual', field='1', spw='16:0', flagbackup=False)
# Deal with spw 26 and 27
flagdata(vis=msname, mode='rflag', field='1', spw='26~27', freqdevscale=3.5, 
	timedevscale=3.5, extendpols=True, datacolumn='corrected', 
	action='apply', flagbackup=False)
# Then 37~42
flagdata(vis=msname, mode='rflag', field='1', spw='37~42', freqdevscale=3.5, 
	timedevscale=3.5, extendpols=True, datacolumn='corrected', action='apply',
	flagbackup=False)
# Then the last cols, again dealing with 45 by itself
flagdata(vis=msname, mode='rflag', field='1', spw='43, 44, 46, 47', freqdevscale=3,
	timedevscale=3.5, extendpols=True, datacolumn='corrected', action='apply',
	flagbackup=False)
cmdlist = ["mode='manual' spw='45' field='1' scan='6'",
	"mode='rflag' field='1' spw='45' timerange='>2024/01/27/01:56:10' freqdevscale=2.5 timedevscale=2.5 extendflags=False extendpols=True",
	"mode='extend' spw='45' field='1' growtime=50.0 growfreq=50.0 timerange='>2024/01/27/01:56:10'"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Add the model back in
```

# Final full Calibration

We just rerun the gain calibrations to get a better secondary calibration. Need to do both to fully regenerate. Also fixed some problems from before. 

```python
clearcal(vis=msname, field='1')  # remove model from secondary calibrator
```

- Change solution to phase, for each integration time ‘p’ and ‘int’
- Amplitude can still be across full time.
- Split into separate phase + amplitude

```python
gaincal(vis=msname, caltable=f'{name}.G1', field='0', spw='16~47:5~58', 
	solint='int', refant='ea22', gaintype='G', calmode='p', solnorm=False, 
	gaintable=[f'{name}.K0', f'{name}.B0'],
	interp=['', 'nearest'])  # Phase only
gaincal(vis=msname, caltable=f'{name}.G1', field='1',
	spw='16~47:5~58', solint='int', refant='ea22', gaintype='G', calmode='p',
	gaintable=[f'{name}.K0', f'{name}.B0'], 
	append=True)  # Phase only
```

The amplitude comes from the bandpass, but phase from G1.

Then we do the combined with the more accurate phase calibration called G2

```python
gaincal(vis=msname, caltable=f'{name}.G2', field='0', spw='16~47:5~58',
	solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield='0', interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G2', field='1',
	spw='16~47:5~58', solint='inf', refant='ea22', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['0', '0', '1'], interp=["nearest", "nearest", "linear"], 
	append=True)
```

Then create the fluxscale and apply it into the model column for the secondary calibrator.

```python
myscale = fluxscale(vis=msname,	caltable=f'{name}.G1', 
	fluxtable=f'{name}.fluxscale1',	reference='0', transfer=['1'], 
	incremental=False)
setjy(vis=msname, field='1', standard='fluxscale', fluxdict=myscale)
```

Then create G3 which is G2, but ran with the model column populated. We make sure to use the right gain field for the secondary calibrator.

```python
gaincal(vis=msname, caltable=f'{name}.G3', field='0', spw='16~47:5~58',
	solint='inf', refant='ea22', gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"], 
	gainfield='0', interp=['', 'nearest', 'linear'])
gaincal(vis=msname, caltable=f'{name}.G3', field='1',
	spw='16~47:5~58', solint='inf', refant='ea22', gaintype='G', calmode='ap',
	gaintable=[f'{name}.K0', f'{name}.B0', f"{name}.G1"],
	gainfield=['0', '0', '1'], interp=["nearest", "nearest", "linear"], 
	append=True)
```

Then we can actually calibrate the secondary calibrator + science field. [K0, B0, G1, G3], associating the calibrations with the right field.

```python
applycal(vis=msname, field='1~2',
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=['1','1','0','0'],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False)
```

# Remove RFI from 2A0335+096

- 16, narrow spikes
- 19, one narrow spike
- 20~22 small/wide spike
- 26, couple wide spikes lots in later channels. Bleeds into 27
- 32 first channel, little in second + noise
- 34~35 little spike + noise
- 36 lots of noise, broad
- 37 wide spikes
- 38 lots of noise + wide faint spikes
- 39~44 noise
- 45 noise + sharp peaks
- 46, 47 noise

```python
# SPW 16-25, basic sweep
cmdlist = ["mode='rflag' field='2' spw='16~18,23~25' extendpols=True",
	"mode='extend' field='2' spw='16~18,23~25' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# Slightly harder on 19, 20~22
cmdlist = ["mode='rflag' field='2' spw='19~22' freqdevscale=4.0 timedevscale=4.0 extendpols=True",
"mode='extend' field='2' spw='19~22' growtime=50.0 growfreq=50.0 flagneartime=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)# SPW 26 & 27
# Then the 26,27 spike, can also deal with 32
cmdlist = ["mode='rflag' field='2' spw='26~27,32' freqdevscale=3.5 timedevscale=3.5 extendpols=True",
	"mode='extend' field='2' spw='26~27,32' growtime=50.0 growfreq=50.0"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 28~31 + 33~35 is fine
# 36 to 44
cmdlist = ["mode='rflag' field='2' spw='36~44' freqdevscale=3.5 timedevscale=4.0 extendpols=True",
	"mode='extend' field='2' spw='36~44' growtime=50.0 growfreq=50.0 flagneartime=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 45 alone
cmdlist = ["mode='manual' field='2' spw='45:11~12'",
	"mode='rflag' field='2' spw='45' freqdevscale=2.5 timedevscale=3.0 extendpols=True",
	"mode='extend' field='2' spw='45' growtime=50.0 growfreq=50.0 flagneartime=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
# 46, 47
cmdlist = ["mode='rflag' field='2' spw='46,47' freqdevscale=3.0 timedevscale=4.0 extendpols=True",
	"mode='extend' field='2' spw='46,47' growtime=50.0 growfreq=50.0 flagneartime=True flagnearfreq=True"]
flagdata(vis=msname, mode='list', inpfile=cmdlist, action='apply', flagbackup=False)
```

# Calibrate 2A0335+096

Then we just transfer the calibration from the secondary onto the science field. Note that we use the fluxscale interpolation as linear instead of nearest. (Copied from before)

```python
applycal(vis=msname, field='2',
	gaintable=[f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0'],
	gainfield=['1','1','0','0'],
	interp=['linear', 'linear', 'nearest','nearest'],
	calwt=False)
```

## Notes

- phase vs freq, diagonal is RFI
- imhead, tclean spit out beam size. Check cell size is fine.
- Add scales? Might not make much difference.
- 2x datasets ~43 GB ea taken in D-configuration for this source.
- Separate calibrations, initial image + 1 round of self calibration to double check.
- Image all together, joint self calibration.
    - tclean vis can be a list of strings. Or
    - Concat to glue them into a single ms.
- D config should have a better behaved beam + better for extended emission (than C config)

# RFI 2A0335+096 part 2

Problems with self calibration during imaging showed remaining RFI via diagonal components along phase calibration. In freq domain there is scattered noise (esp in later channels), time domain shows a 4 single timestep spikes. Might as well flag thoise times.

```python
flagdata(vis=msname, mode='manual', field='2', correlation='RR,LL', 
	timerange='02:13:22.50')
flagdata(vis=msname, mode='manual', field='2', correlation='RR,LL', 
	timerange='02:39:22.50')
flagdata(vis=msname, mode='manual', field='2', correlation='RR,LL', 
	timerange='02:27:55~02:27:59')
flagdata(vis=msname, mode='rflag', field='2', spw='16~47', correlation='RR,LL',
	timedevscale=4.0, freqdevscale=4.0,
	action='apply', flagbackup=False)

```

#