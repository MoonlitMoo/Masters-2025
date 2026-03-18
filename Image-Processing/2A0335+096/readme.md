# 2A0335+096
This cluster has a couple different folders as it was the first one I experimented with. It's got one self-calibration that isn't perfect, but used for the thesis imaging. No minihalo flux estimate.

There is a 'non-pipeline' calibration that was my first attempt, no real reason to look at that other than to see my learning / manual process. 

There is the 'full_image' (self-calibration.tar.gz) which I used for the thesis, this isn't perfect as the cconfig dataset has some weird negative modelling around the BCG which is throwing things off a little in the joint model/image. In this there are also two extra calibrations (p7 & p8 from memory), where I was trying to make this better, but didn't use since wasn't happy with the process. 

Lastly there is try2 or 'second_attempt.tar.gz', where I went back to the beginning and tried from scratch. This is in-progress and not completed, left for picking up / experimenting with.

Overall, the image is ok, not perfect. There is some sidelobe contaimination from the subtraction due to the cconfig modelling from memory. The minihalo is hard to separate from the fossil lobes at their relative brightnesses, but might not be impossible with some smoothing / careful uvrange selections.