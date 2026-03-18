# A2204
This data is self-calibrated but not properly source-subtracted. The resulting image has some negative sidelobe residuals which attenuate the minihalo flux pretty badly. My debugging / investigation found it was pretty much due to the cconfig data. 

There's some difficulty in separately modelling the C- and D-configuration data, since the companion galaxy is merged with the BCG in the D-configuration observations due to the beam size. It makes it a bit more tricky to do separate modelling and glue models together, which is why I ended up doing scaling (I think). Either way, a better subtraction should be able to grab a flux estimate. It might need better self-calibration, or just source modelling for this.

Folders are standard.