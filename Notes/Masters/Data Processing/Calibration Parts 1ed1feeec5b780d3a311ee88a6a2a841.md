# Calibration Parts

Notes from https://casadocs.readthedocs.io/en/latest/notebooks/synthesis_calibration.html#Preparing-for-Calibration

# Gain curve calibration ‘gc’

Large antennas have a forward gain and efficiency that changes with elevation. This is because the elevation will change the how gravity deforms the dish, since they are not perfectly rigid. 
Most important at higher frequencies as deformations will represent a larger fraction of the wavelength (wavelength smaller so deformity errors will be larger at the scale). This effect is minimised between 45 and 60 degrees. 

Should only be used on VLA data, and can be specified as ‘gceff’ or ‘gc’ and ‘eff’ separately.  

# Atmospheric optical depth calibration ‘opac’

At large radio frequencies >15GHz water + oxygen molecules cause effects on observations. These absorb radio waves, attenuating them before the antenna. This calibration solves for this. It is worse at low elevations since it passes through more atmosphere.

These molecules also add noise-like power to the system upon re-emission and a time-dependent phase error. These effects are solved via gain solutions. 

We can get opacity corrections from weather statistics and seasonal models. `plotweather` function will mix the weather statistics and the model to produce an estimate for each spectral window. Default mixing is half and half. 

# Re-quantisation calibration

Still not sure about this. It comes up as part of the switched power calibrations, but is also noted as mainly a test? This only returns the requantiser voltage gains. 

The switched-power calibration is basically an additional source of injected noise we know the power of. This means we can see how the measured level of noise changes as it is toggled on and off in order to derive a gain calibration. The tag `swpow` should do this, but `rq` seems to be used in the pipeline? 

# Antenna corrections

The antennas may positions may have been corrected post-observation. Since this affects the UV distance, we can get any updated positions from online in order to correct the data.

# Flux model

# Delay calibration

# Bandpass calibration

# Gain calibration

## Phase calibraiton

## Amplitude calibration