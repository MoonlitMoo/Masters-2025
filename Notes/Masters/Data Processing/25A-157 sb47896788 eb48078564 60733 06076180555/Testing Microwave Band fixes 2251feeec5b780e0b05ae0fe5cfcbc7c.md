# Testing Microwave Band fixes

The phase calibration is really bad for the microwave bands, so running a custom one instead where I also combine via SPW for the secondary calibrator.

```python
rm -r 25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl
```

```python
# Short gain cal
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='0', spw='', selectdata=True, solint='int', combine='scan,spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='int', combine='scan,spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
# Final amp gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='0', spw='', selectdata=True,	solint='63.0s', combine='scan,spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='scan,spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
# Final phase gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='0', spw='', selectdata=True, solint='63.0s', combine='scan,spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='scan,spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
```

Replacing the stage calibrations with spw averaged ones. 

Then running the rest of the pipeline

```python
hifv_applycals()
hifv_aoflagger(flag_target='A478', aoflagger_file='A478.lua', use_corrected=True)
hifv_statwt()
hifv_plotsummary()
hifv_exportdata()
h_save()
```

## Comparing phase/gain solutions

### Gain Phase Before

![image.png](Testing%20Microwave%20Band%20fixes/image.png)

### Gain phase after

![image.png](Testing%20Microwave%20Band%20fixes/image%201.png)

Much better constrained, just less points due to the spw averaging of course. All antenna follow same results. Following is coloured by antenna.

![image.png](Testing%20Microwave%20Band%20fixes/image%202.png)

### Gain amp before

![image.png](Testing%20Microwave%20Band%20fixes/image%203.png)

All antenna similar with more or less random crap above 1. Note that this corresponds ONLY to spw 22~31, as shown in following image.

![image.png](Testing%20Microwave%20Band%20fixes/image%204.png)

### Gain amp after

![image.png](Testing%20Microwave%20Band%20fixes/image%205.png)

All data, coloured by antenna. Way more points in the 0.5 range compared to previously. Could be why it’s melty below. On the other hand, there aren’t random points > 1 by a significant margin. 

## Comparing spectra of J0424+0204

### Gain before

![image.png](Testing%20Microwave%20Band%20fixes/image%206.png)

### Gain after

![image.png](Testing%20Microwave%20Band%20fixes/image%207.png)

There’s less spikes, but it looks melted. Huge SPW dependence. 

### Phase Before

![image.png](Testing%20Microwave%20Band%20fixes/image%208.png)

### Phase after

![image.png](Testing%20Microwave%20Band%20fixes/image%209.png)

There’s a real spw dependence on the phase, not seen in the non spw combined which makes sense. The degree of the offset seems pretty concerning though. 

## Comparing A478

### Before

![image.png](Testing%20Microwave%20Band%20fixes/image%2010.png)

### After

![image.png](Testing%20Microwave%20Band%20fixes/image%2011.png)

The after fields look cleaner, better flagging seems to have been applied in general. 

# Check final flagging

![field_J0424+0204_spw_flagging.png](Testing%20Microwave%20Band%20fixes/field_J04240204_spw_flagging.png)

![field_A478_spw_flagging.png](Testing%20Microwave%20Band%20fixes/field_A478_spw_flagging.png)

# Pipeline attempt 3

Now trying combine over spw, but not scan to see if it gets better solutions for the secondary calibrator.

```python
rm -r 25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl
rm -r 25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl
rm -r 25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl
```

```python
# Short gain cal
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='0', spw='', selectdata=True, solint='int', combine='spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='int', combine='spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
# Final amp gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='0', spw='', selectdata=True,	solint='63.0s', combine='spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
# Final phase gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='0', spw='', selectdata=True, solint='63.0s', combine='spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
```

```python
hifv_applycals()
hifv_aoflagger(flag_target='A478', aoflagger_file='A478.lua', use_corrected=True)
hifv_statwt()
hifv_plotsummary()
hifv_exportdata()
h_save()
```

## Phase and Amp

Coloured by antenna. 

![image.png](Testing%20Microwave%20Band%20fixes/image%2012.png)

![image.png](Testing%20Microwave%20Band%20fixes/image%2013.png)

![image.png](Testing%20Microwave%20Band%20fixes/image%2014.png)

# Pipeline try 4

Trying out doing the amp per spw, but phase over all spw

```python
# Short gain cal
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='0', spw='', selectdata=True, solint='int', combine='scan,spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='int', combine='scan,spw', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, gaintable=[], gainfield=[''], 
	interp=[''], spwmap=[], parang=True)
# Final amp gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='0', spw='', selectdata=True,	solint='63.0s', combine='scan', 
	preavg=-1.0, refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], parang=True)
gaincal(vis='finalcalibrators.ms', caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='scan', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=5.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='ap', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_6.phaseshortgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], parang=True)
# Final phase gain
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='0', spw='', selectdata=True, solint='63.0s', combine='scan,spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=False, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
gaincal(vis='finalcalibrators.ms', 
	caltable='25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_8.finalphasegaincal.tbl', 
	field='1', spw='', selectdata=True, solint='63.0s', combine='scan,spw', preavg=-1.0, 
	refant='ea15,ea20,ea16,ea12,ea27,ea26,ea25,ea02,ea17,ea19,ea08,ea07,ea01,ea06,ea14,ea09,ea03,ea22,ea28,ea04,ea18,ea11,ea13,ea23,ea24', 
	refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G', 
	smodel=[], calmode='p', append=True, 
	gaintable=['25A-157.sb47896788.eb48078564.60733.06076180555.ms.hifv_finalcals.s12_7.finalampgaincal.tbl'], 
	gainfield=[''], interp=[''], spwmap=[], parang=True)
```

Looks practically identical to the above, so didn’t fix it.