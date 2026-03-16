# Second calibration

# Pre-calibration analysis

Doing some initial plots to figure out what level of aoflagger we need for the secondary + primaries

## Base flagging plotting

```python
check_flagging(msname, output_dir='plots/initial_plots')
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/initial_plots/primary_amp.png')
plotms(vis=msname, field="J0321+1221", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/initial_plots/secondary1_amp.png')
plotms(vis=msname, field="J0424+0204", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/initial_plots/secondary2_amp.png')
plotms(vis=msname, field="2A0335+096", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/initial_plots/science1_amp.png')
plotms(vis=msname, field="A478", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/initial_plots/science2_amp.png')
```

## Pre-calibration aoflagger checks

```python
check_flagging(msname, output_dir='plots/pre-flagging')
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/pre-flagging/primary_amp.png')
plotms(vis=msname, field="J0321+1221", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/pre-flagging/secondary1_amp.png')
plotms(vis=msname, field="J0424+0204", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/pre-flagging/secondary2_amp.png')
plotms(vis=msname, field="2A0335+096", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/pre-flagging/science1_amp.png')
plotms(vis=msname, field="A478", xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/pre-flagging/science2_amp.png')
```

# Calibration with apriori tables

## Splitting off C-band stuff

Temp hack to get around the flagging things

```python
split(vis=msname, outputvis=f'{msname[:-3]}-trim.ms', spw='16~47', datacolumn='data')
msname = f'{msname[:-3]}-trim.ms'
spw_string='0:19~21,1:16~18,2:22~24,3:26~28,4:7~9,5:27~29,6:49~51,7:28~30,8:5~7,9:34~36,10:24~26,11:11~13,12:5~7,13:33~35,14:42~44,15:33~35,16:13~15,17:38~40,18:12~14,19:42~44,20:50~52,21:47~49,22:8~10,23:24~26,24:35~37,25:20~22,26:12~14,27:35~37,28:51~53,29:45~47,30:15~17,31:39~41'
```

Adding in apriori tables learnt from the pipeline. 

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
```

## Initial calibration

Then we need the initial calibration. Applying this to the **primary_2** flag version, since extra flagging occasionally kills a spw in the bandpass which I can’t be bothered fixing. 

**NOTE I MANUALLY FLAGGED A DELAY CALIBRATION POINT AT -200ns HALFWAY THROUGH**

```python
# Set the flux model for the primary calibrator
setjy(vis=msname, field=p_calibrator, standard='Perley-Butler 2017', model='3C48_X.im',
	usescratch=True, scalebychan=True)
# Get inital phase calibration
remove_calibration(name, 'G0')
gaincal(vis=msname, caltable=f'{name}.G0', field=p_calibrator, refant=refant, 
	spw=spw_string, gaintype='G', calmode='p', solint='int', minsnr=5, 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq'])
# Get the delay calibration
remove_calibration(name, 'K0')
gaincal(vis=msname, caltable=f'{name}.K0', field=p_calibrator, refant=refant, 
	spw='*:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5, 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.G0'])
# Get the bandpass solution
remove_calibration(name, 'B0')
bandpass(vis=msname, caltable=f'{name}.B0', field=p_calibrator, refant=refant, 
	combine='scan', solint='inf', bandtype='B', 
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.G0', f'{name}.K0'])
# Get a better amp + phase solution
remove_calibration(name, 'G1')
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58', 
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
```

### Applying

```python
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'linear'],
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

We will skip here because we have all the flagging done. Doing this on the latest set of flags.

```python
split(vis=msname, outputvis=f'{msname[:-4]}-trim.ms', spw='16~47', datacolumn='data')
msname = f'{msname[:-4]}-trim.ms'
```

```python
# DO PRIMARY
# Run the phase only calibration
remove_calibration(name, "G1")
gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='p', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the phase + amp calibration
remove_calibration(name, "G2")
gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the final gain calibration
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'])
# DO SECONDARY
# Clear any calibration in s_calibrator for cleanup
clearcal(vis=msname, field=s_calibrator)
# Extend the phase calibration, use interp as the default linear
gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
	spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='p',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0'],
	append=True)
# Get the phase + amp calibration to create the flux model
gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
	spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='ap',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'],
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
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	gainfield=['', '', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'linear', 'nearest'],
	append=True)
```

### Applying calibrations

```python
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'linear', 'linear'],
	calwt=False, flagbackup=False)
applycal(vis=msname, field=s_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
applycal(vis=msname, field='2A0335+096',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
```

### Plotting

```python
mkdir plots/final_primary_cal
# Gain phase
plotms(vis=f'{name}.G1', xaxis='time', yaxis='phase', coloraxis='corr', 
	iteraxis='antenna', plotfile='plots/final_primary_cal/phase.png', exprange='all')
# Gain amp
plotms(vis=f'{name}.G3', xaxis='freq', yaxis='amp', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/final_primary_cal/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/final_primary_cal/spw_amp_calibrated.png')
```

```python
mkdir plots/final_secondary_cal
# Gain phase
plotms(vis=f'{name}.G1', field='1', xaxis='time', yaxis='phase', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/final_secondary_cal/phase.png', exprange='all')
# Gain amp
plotms(vis=f'{name}.G3', field='1', xaxis='freq', yaxis='amp', coloraxis='corr', 
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