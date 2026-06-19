# High-Frequency Study of Radio Minihalos

This repository stores the analysis methods and notes taken during my Master's project 3/25 to 3/26 at VUW. The actual data, raw, processed, and imaging, is stored on the VUW research storage [SOLAR](http://libguides.victoria.ac.nz/research-data-management/store). Contact details to get access are below.

I have split this into three primary parts, Data-Processing, Image-Processing, and my notes. A bunch of scripts are also littered everywhere, but are almost organised if you squint. The Notes are pretty much a one-to-one recreation of the repo structure and have been exported in markdown format.

## Data-Processing
This folder contains the pipeline calibration and analysis metadata for each raw observation. For the data and pipeline product data, go to SOLAR. Detailed notes are in the notes folder. 

## Image-Processing
This contains the averaged down and organised datasets from Data-Processing, sorted per cluster. Each cluster has 'cconfig' and 'dconfig_X' folders where I did some per dataset exploration (some clusters are missing that due to time constraints). Then the 'full_image' folder contains the joint image self-calibration process. The 'minihalo' folder contains the self-calibrated images and analysis performed to do subtraction, point flux estimates, etc. A common folder of note are 'check_flux' inside 'minihalo',  which contains the images used for point source flux estimates. 

## Notes
This is an export from Notion, which has pages and subpages represented as markdown files and folders. Note that the bunch of letters at the end of each filename is just a hash from the export, noting the version of the notion pae. There are also some extra pages for my writing and research notes, which are only partly done as a lot ended up being written in-situ in the thesis.

## Random scripts
In the top-level there are three scripts `cal_tools.py`, `flagging_tools.py`, and `minihalo_tools.py`. These implement the majority of the logic I used for the analysis and debug plotting throughout the thesis. A lot of the exact commands are also listed in the notes, and required importing in CASA prior to running. 

More custom scripts are present where required, particularly `calculate_flux.py` and `minihalo_flux.py` in the 'minihalo' folders. These calculate the minihalo flux and uncertainty (using functions in the tools file) for the given cluster, and plot the flux values and fit the spectral index, respectively. More precise READMEs are given for the clusters, especially where there is a lot going on. Important note is that some of the `minihalo_flux.py` files have the wrong minihalo flux or BCG values, since I was using them to only get the spectral index of one or the other (usually the BCG). 

Probably the best way to figure out what a randomly named folder is about is to open the scripts and hit Ctrl+F to see whatever I used it for, since most scripts should be somewhat commented.

## Admin
Has the raw masters thesis and PASA paper for submission.

# Contact
Any questions can be emailed to me at benjamincahoonz@gmail.com.