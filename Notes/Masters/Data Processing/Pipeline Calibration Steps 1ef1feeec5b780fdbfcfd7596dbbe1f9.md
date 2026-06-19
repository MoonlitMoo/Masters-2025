# Pipeline Calibration Steps

https://science.nrao.edu/facilities/vla/data-processing/pipeline/

# hifv_importdata()

- Loads basic information about the ms, like SPW, freq bands, associated information.

 

# hifv_hanning()

- Applies hanning smoothing to the data
- Weblog killed itself trying to show things.

# hifv_flagdata()

- VLA Deterministic Flagging, apriori flags
    - **ANOS**: Online flagging template?
    - **Unwanted intents**: Flags setup scans with intents like ‘atmosphere’, ‘focus’, etc
    - **Other online flags**: Anything else it finds online
    - **Flagging template**: Anything you decide to give it
    - **autocorr**: Flags the auto-correlations (correlations of antenna to itself)
    - **Edge channels**: Quite literally the first and last channel of every SPW
    - **Clipping**: Any 0 values
    - **Quack**: First 4.5 seconds of every scan
    - **Baseband**: Flags 10 channels at start and end of each baseband (2 in C-band 0~7, 8~15 and 2 in X-band 16~31, 32~47)
- Note usually applied when you download data anyway.

# hifv_vlasetjy()

- Sets the flux model for any primary calibrators

# hifv_priorcals()

- Sets the apriori calibrations that aren’t data dependent

## Gain Curve

```python
gencal(vis=msname, caltable='name.gc', caltype='gc')
```

## Opacity

First needs to grab opacities from plotweather

```python
tau = plotweather(vis=msname)
gencal(vis=msname, caltable='name.opac', caltype='opac', parameter=tau)
```

## Requantiser gains

```python
gencal(vis=msname, caltable='name.rq', caltype='rq')
```

## Switching Power

Doesn’t seem to be used later

```python
gencal(vis=msname, caltable='name.swpow', caltype='swpow')
```

## Antenna position

Allows corrections to be made up to 150 days after the observation.

```python
gencal(vis=msname, caltable='name.ant', caltype='antpos', ant_pos_time_limit=150)
```

# hifv_syspower()

- Not written to cal table, only used to produce plots

# hifv_testBPdcals

- 

## Get good antennas to use for calibration

First yoinks the flagging statistics. Note 0, 2 are the secondary and primary calibrators respectively. 

```python
flagdata(vis=msname, mode='summary', field='0,2', flagbackup=False)
```

Then it uses that to calculate a score and picks the best ones (like 10 of them or something)

## Get an initial phase calibration for delay calibrator

Uses all the X-band SPW with central 22 channels which is about a third of the range. Combine scans but do one solution per interval.

Also uses `parang=True` but this only needed for polarization calibration so we literally do not care.

```python
gaincal(vis=msname, caltable='name.testdelayinitialgain_X', 
	field='2', spw='*:21~43', solint='int', combine='scan', refant='the good ones',
	gaintype='G', smodel=[], calmode='p', gaintable=['gc', 'opac', 'rq', 'ants'], 
	parang=True)
```

## Get an initial delay calibration

Get a single delay solution for each antenna and spectral window. Combines scans with infinite solution interval.

```python
gaincal(vis=msname, caltable='testdelay_X', field='2', spw='', solint='inf', 
	combine='scan', refant='', gaintype='K', calmode='p', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'testdelayinitialgain_X'], 
	parang=True)
```

## Get an initial gain calibration for primary calibrator

Using the test delay calibration, get a better gain calibration using the 22 middle channels. Doing it per interval and combining over scan.

```python
gaincal(vis=msname, caltable='testBPdinitialgain_X', field='2', spw='*:21~43', 
	solint='int', combine='scan', refant='', gaintype='G', calmode='ap', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'testdelay_X'], parang=True)
```

Following this it checks how many solutions are flagged total and per antenna. Potentially to see if it needs to fix something. 

## Get initial bandpass calibration

Since we now have a test gain calibration for the delay and bandpass calibration (both the primary calibrator), we can make a bandpass calibration. 

Also since there’s like nothing flagged it says it will use int for the solution interval, but also this command literally says inf. It also upped the `minsnr` to 5. 

```python
bandpass(vis=msname, caltable='testBPcal_X', field='2', spw='*', solint='inf', 
	combine='scan', refant='', minsnr=5.0, bandtype='B', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'testdelay_X', 'testBPdinitialgain_X'], 
	parang=True)
```

It then cleans up the bandpass using flagdata in clip mode to clip everything not in [0, 2] for the CPARAM data column.

```python
flagdata(vis='testBPcal_X', mode='clip', correlation='ABS_ALL', 
	clipminmax=[0.0, 2.0], datacolumn='CPARAM', apply', flagbackup=False)
```

## Applies initial calibrations to the calibrators

Then it applies to the bandpass and delay calibrators (just the primary in this case).

It uses `linear, linearflag` for interp on the bandpass with the overall applymode `calflagstrict`. 

This means that it does linear interpolation in time and frequency, but that it will flag frequency channels that are missing. The apply mode applies the calibration but will flag whole SPWs that are missing calibrations instead of just warning and passing them through. 

```python
applycal(vis=msname, spw='', gaintable=['gc', 'opac', 'rq', 'ants', 'testdelay_X',
		 'testBPdinitialgain_X', 'testBPcal_X'], 
	 interp=['', '', '', '', '', '', 'linear,linearflag'], 
	 parang=True, applymode='calflagstrict', flagbackup=True)
```

## Test for bad deformatters

Checks phase and amplitudes for each antenna and baseband, flagging any with more than 4 bad SPW. 

# hifv_checkflag()

- Checks for RFI using rflag and tfcrop.
- This one is only targetting the primary calibrator

## Save initial state

Saves the starting flags and the initial time-averaged visibilities, drops all the flags to trim the dataset. 

```python
flagdata(vis=msname, mode='summary', spw='', field='2', scan='23,24', 
	name='before')
mstransform(vis=msname, outputvis='before.bpd-vla.averaged', field='2', spw='', 
	correlation='LL,RR', datacolumn='corrected', keepflags=False, timeaverage=True,
	timebin='1e8', timespan='scan', reindex=False)
flagmanager(vis=msname, mode='save', versionname='hifv_checkflag_bpd-vla_stage8_20250506-004239', 
	comment='flagversion before running hifv_checkflag()')
```

## Rflag the calibrator

It first processes the crosshands with rflag using ABS_RL and ABS_LR. First it calculates a bunch of time and frequency thresholds using the default values, then it uses them in the followup call. It then extends only across polarisations. 

```python
# Outputs two txt files about thresholds
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='ABS_RL', 
	datacolumn='corrected', extendflags=False, action='calculate', 
	flagbackup=False)  
# Uses said thresholds
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='ABS_RL', 
	datacolumn='corrected', extendflags=False, 
	timedev='prev_calc_time', freqdev='prev_calc_freq'
	action='apply', flagbackup=False)
# Run an extend to only match the pols
flagdata(vis=msname, mode='extend', spw='', field='2', extendpols=True, 
	growtime=100.0, growfreq=100.0, action='apply', flagbackup=False)
# Other cross hand
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='ABS_LR', 
	datacolumn='corrected', extendflags=False, action='calculate', 
	flagbackup=False)  
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='ABS_LR', 
	datacolumn='corrected', extendflags=False, 
	timedev='prev_calc_time', freqdev='prev_calc_freq'
	action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', extendpols=True, 
	growtime=100.0, growfreq=100.0, action='apply', flagbackup=False)

```

It then tries to use the residuals to rflag onto for the straight polarisations, which is automatically `CORRECTED-MODEL`, so it doesn’t need to uvsub.

```python
# Outputs two txt files about thresholds
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='REAL_RR', 
	datacolumn='residual', extendflags=False, action='calculate', 
	flagbackup=False)
# Uses said thresholds
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='REAL_RR', 
	datacolumn='residual', extendflags=False, 
	timedev='prev_calc_time', freqdev='prev_calc_freq'
	action='apply', flagbackup=False)
# Run an extend to only match the pols
flagdata(vis=msname, mode='extend', spw='', field='2', extendpols=True, 
	growtime=100.0, growfreq=100.0, action='apply', flagbackup=False)
# Rounds 2
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='REAL_LL', 
	datacolumn='corrected', extendflags=False, action='calculate', 
	flagbackup=False)  
flagdata(vis=msname, mode='rflag', spw='', field='2', correlation='REAL_LL', 
	datacolumn='corrected', extendflags=False, 
	timedev='prev_calc_time', freqdev='prev_calc_freq'
	action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', extendpols=True, 
	growtime=100.0, growfreq=100.0, action='apply', flagbackup=False)
```

## tfcrop the calibrator

It then uses tfcrop to continue, doing a frequency only analysis on the corrected data, before extending across polarisations. It does this for each polarisation individually. Then we follow up with a `flagnearfreq`.

```python
# First cross hand
flagdata(vis=msname, mode='tfcrop', spw='', field='2', correlation='ABS_RL', 
	datacolumn='corrected', ntime=3.0, timecutoff=4.0, freqcutoff=4.0, 
	freqfit='line', flagdimension='freq', extendflags=False, action='apply', 
	flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', ntime='scan', 
	extendflags=False, extendpols=True, action='apply', flagbackup=False)
# Second cross hand
flagdata(vis=msname, mode='tfcrop', spw='', field='2', correlation='ABS_LR', 
	datacolumn='corrected', ntime=3.0, timecutoff=4.0, freqcutoff=4.0, 
	freqfit='line', flagdimension='freq', extendflags=False, action='apply', 
	flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', ntime='scan', 
	extendflags=False, extendpols=True, action='apply', flagbackup=False)
# First straight hand
flagdata(vis=msname, mode='tfcrop', spw='', field='2', correlation='ABS_RR', 
	datacolumn='corrected', ntime=3.0, timecutoff=4.0, freqcutoff=4.0, 
	freqfit='line', flagdimension='freq', extendflags=False, action='apply', 
	flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', ntime='scan', 
	extendflags=False, extendpols=True, action='apply', flagbackup=False)
# Second straight hand
flagdata(vis=msname, mode='tfcrop', spw='', field='2', correlation='ABS_LL', 
	datacolumn='corrected', ntime=3.0, timecutoff=4.0, freqcutoff=4.0, 
	freqfit='line', flagdimension='freq', extendflags=False, action='apply', 
	flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', ntime='scan', 
	extendflags=False, extendpols=True, action='apply', flagbackup=False)
flagdata(vis=msname, mode='extend', spw='', field='2', ntime='scan', 
	extendflags=False, extendpols=True, flagnearfreq=True, action='apply', 
	flagbackup=False)
```

## Get finishing statistics

```python
flagdata(vis=msname, mode='summary', spw='', field='2', name='after')
mstransform(vis=msname, outputvis='after.bpd-vla.averaged', field='2', spw='', 
	correlation='LL,RR', datacolumn='corrected', keepflags=False, 
	timeaverage=True, timebin='1e8', timespan='scan', reindex=False)
```

# hivf_semiFinalBPdcals

- Makes an middle of flagging calibration for the calibrators
- Follows the same process as the initial test calibration, but using the better flagged data.

Grabs initial flag summary to calculate statistics for the good antennas

```python
flagdata(vis=msname, mode='summary', field='0,2', flagbackup=False)
```

## Make new initial phase cal for delay

```python
gaincal(vis=msname, caltable='semiFinaldelayinitialgain_X.tbl', field='2', 
	spw='*:21~43', solint='int', combine='scan', refant='goodones', solnorm=False, 
	gaintype='G', calmode='p', gaintable=['gc', 'opac', 'rq', 'ants'], parang=True)
```

## Make new delay calibration

```python
gaincal(vis=msname, caltable='delay_X', field='2', spw='', solint='inf', 
	combine='scan', refant='', solnorm=False, gaintype='K', calmode='p', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'semiFinaldelayinitialgain_X'], 
	parang=True)
```

## Make new gain calibration

```python
gaincal(vis=msname, caltable='BPinitialgain_X', field='2', spw='*:21~43', 
	solint='int', combine='scan', refant='the good ones', solnorm=False, 
	gaintype='G', calmode='p', gaintable=['gc', 'opac', 'rq', 'ants', 'delay_X'], 
	parang=True)
```

## Make the new bandpass

```python
bandpass(vis=msname, caltable='BPcal_X', field='2', spw='', solint='inf', 
	combine='scan', refant='', bandtype='B', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'delay_X', 'BPinitialgain_X'], 
	parang=True)
```

This time we don’t follow up by flagging the bandpass

## Apply to all calibrators

Uses scan to select the calibrator data

```python
applycal(vis=msname, spw='', scan='calibratorscans',
	gaintable=['gc', 'opac', 'rq', 'ants', 'delay_X', 'BPcal_X'], 
	interp=['', '', '', '', '', 'linear,linearflag'], parang=True, 
	applymode='calflagstrict', flagbackup=True)
```

# hifv_checkflag() # part 2 electric boogaloo

Custom pipeline

It does the exact same thing to the secondary calibrator.

# hifv_solint()

- Determine the solution interval for a scan-average equivalent and do test gain calibrations to establish a short solution interval.

First splits the calibrators into a smaller ms of calibrated data but without any of the flagged data

```python
split(vis=msname, outputvis='calibrators.ms', keepmms=True, 
	scan='4,5,6,8,10,12,14,16,18,20,22,23,24', datacolumn='corrected', 
	keepflags=False)
```

It then calculates all the scan durations and beginning → end time. It also grabs the flag summary to identfy good antennas. 

## Get initial gain calibration

Gets the initial amp + phase calibration for fields individually

```python
gaincal(vis='calibrators.ms', caltable='testgaincal_X', field='0', spw='', 
	scan='', solint='int', combine='scan', refant='goodones',  solnorm=False, 
	gaintype='G', calmode='ap', parang=True)
gaincal(vis='calibrators.ms', caltable='testgaincal_X', field='2', spw='', 
	scan='', solint='int', combine='scan', refant='goodones',  solnorm=False, 
	gaintype='G', calmode='ap', parang=True, append=True)
```

Then it does some heuristics to evaluate how many solutions are flagged and what the shortest solution interval can be. In this case it can be `int`

```python
gaincal(vis='calibrators.ms', caltable='testgaincallimit_X', field='0', spw='', 
	scan='', solint='int', combine='scan', refant='', solnorm=False, gaintype='G', 
	calmode='ap', parang=True)
gaincal(vis='calibrators.ms', caltable='testgaincallimit_X', field='2', spw='', 
	scan='', solint='int', combine='scan', refant='', solnorm=False, gaintype='G', 
	calmode='ap', parang=True, append=True)
```

# hifv_fluxboot()

- Make a gain table that includes gain and opacity corrections for final amp cal and for flux density bootstrapping.
- Fit the spectral index of calibrators with a power-law and put the fit in the model column.

## Sets primary calibrator model

```python
setjy(vis='calibrators.ms', field='2', spw='', scalebychan=True, 
	standard='Perley-Butler 2017', model='3C48_X.im', usescratch=True)
```

## Make short interval phase calibration

Then it grabs the good antennas and gets a phase calibration with short solution intervals for the calibrators.

```python
gaincal(vis='calibrators.ms', caltable='fluxphaseshortgaincal.g', 
	field='0', spw='', solint='int', combine='scan', refant='goodones', 
	minsnr=3.0, solnorm=False, gaintype='G', calmode='p', parang=True)
gaincal(vis='calibrators.ms', caltable='fluxphaseshortgaincal.g', 
	field='2', spw='', solint='int', combine='scan', refant='goodones', 
	minsnr=3.0, solnorm=False, gaintype='G', calmode='p', parang=True, append=True)
```

## Make long interval gain calibration

Makes a long interval amp + phase calibration for the calibrators using the short interval one. Also normalises the squared gain amplitudes. 

```python
gaincal(vis='calibrators.ms', caltable='fluxflag.g', field='J0321+1221', spw='', 
	selectdata=False, solint='222.0s', combine='scan', refant='goodones', 
	minsnr=5.0, solnorm=True, gaintype='G', calmode='ap', 
	gaintable=['fluxphaseshortgaincal.g'], parang=True)
gaincal(vis='calibrators.ms', caltable='fluxflag.g', field='J0321+1221', spw='', 
	selectdata=False, solint='222.0s', combine='scan', refant='goodones', 
	minsnr=5.0, solnorm=True, gaintype='G', calmode='ap', 
	gaintable=['fluxphaseshortgaincal.g'], parang=True)
```

Then it cleans up the solutions and applies the flagged solutions to the measurement set

```python
flagdata(vis='fluxflag.g', mode='clip', correlation='ABS_ALL', 
	clipminmax=[0.9, 1.1], datacolumn='CPARAM', clipoutside=True, 
	action='apply', flagbackup=False)
applycal(vis='calibrators.ms', gaintable=['fluxflag.g'], 
	applymode='flagonlystrict', flagbackup=True)
```

Then it makes the actual one with the better flagged data.

```python
gaincal(vis='calibrators.ms', caltable='fluxgaincal.g', field='0', spw='', 
	solint='222.0s', combine='scan', refant='', gaintype='G', calmode='ap', 
	gaintable=['fluxphaseshortgaincal.g'], parang=True)
gaincal(vis='calibrators.ms', caltable='fluxgaincal.g', field='2', spw='', 
	solint='222.0s', combine='scan', refant='', gaintype='G', calmode='ap', 
	gaintable=['fluxphaseshortgaincal.g'], parang=True, append=True)
```

## Make the fluxscale and set as the model

They do it a bit different, but I assume its cause they have some more idea of what they are doing. They also set it into the main ms, not just the split ms. 

```python
fluxscale(vis='calibrators.ms', caltable='fluxgaincal.g', 
	fluxtable='fluxgaincalFcal_0.g', reference=['2'], 
	transfer=['0'], fitorder=2)
setjy(vis='calibrators.ms', field='J0321+1221', spw='', selectdata=False, 
	scalebychan=True, standard='manual', listmodels=False, fluxdensity=[1.0658000842368038, 0, 0, 0], 
	spix=[-0.655760831551428, -0.4283942378006038], reffreq='9930974495.644924Hz', 
	usescratch=True)
setjy(vis=msname, field='J0321+1221', spw='', selectdata=False, 
	scalebychan=True, standard='manual', listmodels=False, 
	fluxdensity=[1.0658000842368038, 0, 0, 0], spix=[-0.655760831551428, -0.4283942378006038], 
	reffreq='9930974495.644924Hz', usescratch=True)
```

# hifv_finalcals()

- Makes the final calibration tables

## Make the final gain for the delay calibration

```python
gaincal(vis=msname, caltable='finaldelayinitialgain', field='2', spw='*:21~43', 
	solint='int', combine='scan', refant='goodones', minsnr=3.0, solnorm=False, 
	gaintype='G', calmode='p', gaintable=['gc', 'opac', 'rq', 'ants'], parang=True)
```

## Make the final delay calibration

```python
gaincal(vis=msname, caltable='finaldelay', field='2', spw='', solint='inf', 
	combine='scan', refant='', minsnr=3.0, gaintype='K', calmode='p',
	gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelayinitialgain'], parang=True)
```

## Make final gain for bandpass calibration

```python
gaincal(vis=msname, caltable='finalBPinitialgain', field='2', spw='*:21~43', 
	solint='int', combine='scan', refant='goodones', minsnr=3.0, solnorm=False, 
	gaintype='G', calmode='p', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelay'], parang=True)
```

## Make final bandpass calibration

```python
bandpass(vis=msname, caltable='finalBPcal', field='2', spw='', solint='inf', 
	combine='scan', refant='', bandtype='B', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelay', 'finalBPinitialgain'], 
	parang=True)
```

## Make average phase gain calibration

Calculates average phase across the entire timescale

```python
gaincal(vis=msname, caltable='averagephasegain', field='2', spw='', solint='inf',
	combine='scan', refant='goodones', refantmode='flex', minsnr=1.0, gaintype='G', 
	calmode='p', gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelay', 'finalBPcal'], 
	parang=True)
```

Then unflags all the solutions and applies the calibration flags to the data set from the just made calibrations. It then splits off the final calibrators into a new ms. 

```python
flagdata(vis='averagephasegain', mode='unflag', action='apply', flagbackup=False)
```

```python
applycal(vis=msname, scan='4,5,6,8,10,12,14,16,18,20,22,23,24', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelay', 
		'finalBPcal', 'averagephasegain'], 
	parang=True, applymode='calflagstrict', flagbackup=True)
split(vis=msname, outputvis='finalcalibrators.ms', keepmms=True, 
	scan='4,5,6,8,10,12,14,16,18,20,22,23,24', datacolumn='corrected', 
	keepflags=False)
```

Set the calibrator models in the new ms

```python
setjy(vis='finalcalibrators.ms', field='2',	spw='', selectdata=False, 
	scalebychan=True, standard='Perley-Butler 2017', model='3C48_X.im', 
	usescratch=True)
setjy(vis='finalcalibrators.ms', field='J0321+1221', spw='', selectdata=False, 
	scalebychan=True, standard='manual', listmodels=False, 
	fluxdensity=[1.0658000842368038, 0, 0, 0], spix=[-0.655760831551428, -0.4283942378006038], 
	reffreq='9930974495.644924Hz', usescratch=True)
```

## Make short phase gain calibration

```python
gaincal(vis='finalcalibrators.ms', caltable='phaseshortgaincal', field='0', spw='',
 solint='int', combine='scan', refant='goodones', refantmode='flex', minsnr=3.0, 
 solnorm=False, gaiantype='G', calmode='p', parang=True)
gaincal(vis='finalcalibrators.ms', caltable='phaseshortgaincal', field='2', spw='',
 solint='int', combine='scan', refant='goodones', refantmode='flex', minsnr=3.0, 
 solnorm=False, gaintype='G', calmode='p', parang=True, append=True)
```

## Make final gain calibrations

Using short phase gain cal, make the final amp + phase calibration for the calibrators.

```python
gaincal(vis='finalcalibrators.ms', caltable='finalampgaincal', field='0', spw='', 
	solint='222.0s', combine='scan', refant='', refantmode='flex', 
	minsnr=5.0, solnorm=False, gaintype='G', calmode='ap',
	gaintable=['phaseshortgaincal'], parang=True)
gaincal(vis='finalcalibrators.ms', caltable='finalampgaincal', field='2', spw='', 
	solint='222.0s', combine='scan', refant='', refantmode='flex', 
	minsnr=5.0, solnorm=False, gaintype='G', calmode='ap',
	gaintable=['phaseshortgaincal'], parang=True, append=True)
```

Using final amp + phase calibration make the final phase calibration for the calibrators.

```python
gaincal(vis='finalcalibrators.ms', caltable='finalphasegaincal', field='0', spw='', 
	solint='222.0s', combine='scan', refant='', refantmode='flex', 
	minsnr=3.0, solnorm=False, gaintype='G',calmode='p', 
	gaintable=['finalampgaincal'], parang=True)
gaincal(vis='finalcalibrators.ms', caltable='finalphasegaincal', field='2', spw='', 
	solint='222.0s', combine='scan', refant='', refantmode='flex', 
	minsnr=3.0, solnorm=False, gaintype='G',calmode='p', 
	gaintable=['finalampgaincal'], parang=True, append=True)
```

# hifv_applycals

- This task applies all calibrations registered with the pipeline to their target measurement sets.

Does flagging summary stuff

```python
applycal(vis=msname, antenna='*&*', 
	gaintable=['gc', 'opac', 'rq', 'ants', 'finaldelay', 'finalBPcal', 'averagephasegain', 'finalampgaincal', 'finalphasegaincal'], 
	gainfield=['', '', '', '', '', '', '', '', ''], 
	interp=['', '', '', '', '', 'linear,linearflag', '', '', ''], 
	parang=True, applymode='calflagstrict', flagbackup=True)
```

Does more flagging summary to see how much application flagged the data

# hifv_checkflag() # Part 3

- This time it hits the science field we care about

# hifv_statwt()

- Calculate data weights based on st. dev. within each spw.

Does some flagging statistics before calculating the weights. It has bumped the min samples up a decent amount. It then splits it off

```python
statwt(vis=msname, minsamp=8, datacolumn='corrected')
split(vis=msname, outputvis='after.wts', spw='*:0', datacolumn='CORRECTED', 
	keepflags=False)
```

Then calculates some more flagging statistics

# My pipeline

- `hifv_importdata`
- `hifv_flagdata` get the apriori flags
- `hifv_vlasetjy`
- `hifv_priorcals` get the apriori calibrations
- Run aoflagger on the primary for pre calibration
- `hifv_testBPdcals` get the initial primary calibration
- Run aoflagger on the primary for final primary calibration
    - Replaces `hifv_checkflag` that ran on the primary calibrator
- Run aoflagger on the secondary for the precalibration
- `hifv_semiFinalBPdcals` gets next primary calibration and applies to the secondary calibration
- `hifv_solint` Get gain calibrations for the primary and secondary
- `hifv_fluxboot` get the models for the primary and secondary calibrations
- `hifv_finalcals` get the final delay, bandpass, gain calibrations for the calibrators
- `hifv_applycals` apply the calibrations to everything
- Run aoflagger on the science target(s)
- `hifv_statwt` apply statistical weightsd