from casatasks import tclean

OUTPUT_DIR = "grid_search"
smallscalebias = [-0.5, 0, 0.5]
robust = [0.5, 1, 1.5, 2]

for ssb in smallscalebias:
    for r in robust:
        image_name = f"{OUTPUT_DIR}/minihalo_robust{r}_ssb{ssb}"
        tclean(vis=["cconfig_uvsub.ms", "dconfig1_uvsub.ms", "dconfig2_uvsub.ms"],
            imagename=image_name,
            imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
            specmode='mfs', niter=10000, gain=0.1, threshold='0.008mJy',
            deconvolver='mtmfs', pblimit=-1.e-6, scales=[0, 4, 8, 16], smallscalebias=ssb,
            stokes='I', weighting='briggs', robust=r, pbcor=False,
            usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
            lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
