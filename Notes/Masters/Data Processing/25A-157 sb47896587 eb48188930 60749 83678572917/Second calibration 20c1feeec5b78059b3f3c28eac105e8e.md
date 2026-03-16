# Second calibration

# Calibration setup

- Using `ea02` as the reference antenna.
- p_calibrator is `0137+331=3C48` at field `0`
- s_calibrator is `J0321+1221` at field `1`
- science field is `2A0335+096` at field `2`

🚩 **saved apriori flag state as base_flagging**

# Apriori calibrations

Create the gain curve, opacity, requantisation calibrations. **There are no antenna corrections for this dataset.**

```bash
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

# Initial primary flagging

Notes say ea10 and ea01 had problems so flagging outright.

```bash
flagdata(vis=msname, antenna='ea10,ea01', flagbackup=False)
!aoflagger -fields 0 -strategy primary.lua 25A-157.sb47896587.eb48188930.60749.83678572917.ms
```

🚩 **saved state as primary**

### Plotting

```bash
mkdir plots/primary_flagging
# Flagging plots
check_flagging(msname, output_dir='plots/primary_flagging')
# Amplitude plots
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/primary_flagging/spw_amp.png')
plotms(vis=msname, field=p_calibrator, xaxis='time', yaxis='amp', coloraxis='spw', 
	avgchannel='8', correlation='LL,RR', plotfile='plots/primary_flagging/time_amp.png')
```

![spw_amp.png](Second%20calibration/spw_amp.png)

![time_amp.png](Second%20calibration/time_amp.png)

![field_2A0335+096_spw_flagging.png](Second%20calibration/field_2A0335096_spw_flagging.png)

![field_0137+331=3C48_antenna_flagging.png](Second%20calibration/field_01373313C48_antenna_flagging.png)

![all_fields_flagging.png](Second%20calibration/all_fields_flagging.png)

# Initial primary calibration

Then do the initial calibration using the first pass flagging

```bash
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

## Applying initial calibration

```bash
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'linear'],
	calwt=False, flagbackup=False)
```

### Plotting

```bash
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
plotms(vis=f'{name}.G1', xaxis='freq', yaxis='amp', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/initial_cal/gain/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/initial_cal/spw_amp_calibrated.png')
```

![spw_amp_calibrated.png](Second%20calibration/spw_amp_calibrated.png)

# Final primary flagging

Rerunning aoflagger with same settings on the model subtracted data. The first scan is really bad so I flagged it.

```bash
uvsub(vis=msname)
!aoflagger -fields 0 -strategy primary_2.lua -column CORRECTED_DATA 25A-157.sb47896587.eb48188930.60749.83678572917.ms
uvsub(vis=msname, reverse=True)
```

🚩**Saved as ‘primary_2’**

### Plotting

```bash
mkdir plots/primary_2_flagging
# Flagging plots
check_flagging(msname, output_dir='plots/primary_2_flagging')
# Amplitude plots
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/primary_2_flagging/spw_amp.png')
plotms(vis=msname, field=p_calibrator, xaxis='time', yaxis='amp', coloraxis='scan', 
	avgchannel='8', correlation='LL,RR', plotfile='plots/primary_2_flagging/time_amp.png')
```

# Final primary calibration

Using the model subbed flagging to make a better calibration. Overwriting G1 from prior

```bash
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
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the final gain calibration
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
```

## Applying final primary calibration

```bash
applycal(vis=msname, field=p_calibrator,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'linear', 'linear'],
	calwt=False, flagbackup=False)
```

### Plotting

```bash
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

![spw_amp_calibrated.png](Second%20calibration/spw_amp_calibrated%201.png)

# Initial secondary flagging

```bash
!aoflagger -fields 1 -strategy secondary.lua 25A-157.sb47896587.eb48188930.60749.83678572917.ms
```

🚩**Saved as ‘secondary’**

## Plotting

```bash
mkdir plots/secondary_flagging
# Flagging plots
check_flagging(msname, output_dir='plots/secondary_flagging')
# Amplitude plots
plotms(vis=msname, field=s_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/secondary_flagging/spw_amp.png')
plotms(vis=msname, field=s_calibrator, xaxis='time', yaxis='amp', coloraxis='spw', 
	avgchannel='8', correlation='LL,RR', plotfile='plots/secondary_flagging/time_amp.png')
```

![spw_amp.png](Second%20calibration/spw_amp%201.png)

![time_amp.png](Second%20calibration/time_amp%201.png)

# Initial secondary calibration

```bash
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
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'],
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
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'],
	append=True)
```

## Apply calibration

```bash
applycal(vis=msname, field='1',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
```

### Plotting

```bash
mkdir plots/initial_secondary_cal
# Gain phase
plotms(vis=f'{name}.G1', field='1', xaxis='time', yaxis='phase', coloraxis='spw', 
	iteraxis='antenna', plotfile='plots/initial_secondary_cal/phase.png', exprange='all')
# Gain amp
plotms(vis=f'{name}.G3', field='1', xaxis='freq', yaxis='amp', coloraxis='corr', 
	iteraxis='antenna', plotfile='plots/initial_secondary_cal/amp.png', exprange='all')
# Calibrated primary
plotms(vis=msname, field=s_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', ydatacolumn='corrected', plotfile='plots/initial_secondary_cal/spw_amp_calibrated.png')
```

![spw_amp_calibrated.png](Second%20calibration/spw_amp_calibrated%202.png)

# Final secondary flagging

```bash
uvsub(vis=msname)
!aoflagger -fields 1 -strategy secondary_2.lua 25A-157.sb47896587.eb48188930.60749.83678572917.ms
uvsub(vis=msname, reverse=True)
```

### Plotting

```bash
mkdir plots/secondary_2_flagging
# Flagging plots
check_flagging(msname, output_dir='plots/secondary_2_flagging')
# Amplitude plots
plotms(vis=msname, field=p_calibrator, xaxis='freq', yaxis='amp', coloraxis='spw', 
	avgtime='60', correlation='LL,RR', plotfile='plots/secondary_2_flagging/spw_amp.png')
plotms(vis=msname, field=p_calibrator, xaxis='time', yaxis='amp', coloraxis='scan', 
	avgchannel='8', correlation='LL,RR', plotfile='plots/secondary_2_flagging/time_amp.png')
```

# Final secondary calibration

```bash
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
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
# Run the final gain calibration
gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
	solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1'],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'])
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
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'],
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
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest'],
	append=True)
```

## Apply calibration

```bash
applycal(vis=msname, field='1',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
```

### Plotting

```bash
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

# Flag 2A0335+096

## Apply calibration

```bash
applycal(vis=msname, field='2',
	gaintable=[f'{name}.gc', f'{name}.opac', f'{name}.rq', f'{name}.K0', f'{name}.B0', f'{name}.G1', f'{name}.G3'],
	gainfield=['', '', '', p_calibrator, p_calibrator, s_calibrator, s_calibrator],
	interp=['linear', 'linear', 'linear', 'linear', 'nearest', 'nearest'],
	calwt=False, flagbackup=False)
```

Flagging increased to ~19% from 17% due to apply cal. 

## Flagging on calibrated data

Don’t need to subtract model, since there is no model and there’s stuff all signal.

```bash
!aoflagger -fields 2 -strategy science.lua -column CORRECTED_DATA 25A-157.sb47896587.eb48188930.60749.83678572917.ms
```

🚩**saved as ‘2A0335+096’**

### Plotting

```bash
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

# Split final imaging data