# RXJ1720+2638
It's self-calibrated and has a minihalo flux value. There's a lot in here since it's the main experiment case study. A brief list:

- In the 'minihalo' folder the check_flux folder is named 'agn_images' instead. 
- There are several tests I did to see how uvrange impacted the configs (joint and not) stored in 'config_tests' in 'minihalo'
- All the minihalo imaging is under 'model_minihalo' in 'minihalo', though the plotting is in the 'minihalo' folder.
- A few grid searches are in 'model_minihalo', checking how robust the flux measurements are against choice of robust + smallscalebias. 
- The scripts are also extremely messy since I was hot gluing bits together to test different things (like masking). So if re-running thins be casreful about what mask is being used to calculate fluxes etc.
- There's an extra L-band folder (depending where you look) which is being analysed for the PASA paper.
- There's also some RFI testing I did for a reason I don't remember, stored in it's own special 'full_image_rfi_tests' folder for a reason I also don't remember.