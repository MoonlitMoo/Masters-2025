# Flagging
flagdata('dconfig1-p3.ms', spw='21,22', flagbackup=False)
flagdata('dconfig2-p3.ms', spw='11,15,16', flagbackup=False)

datasets = ["cconfig", "dconfig1", "dconfig2"]
nterms = 2
# Set model, self cal
for ms in [f'{d}-p3.ms' for d in datasets]:
	clearcal(ms)
	models = [f'../image-p3.model.tt{i}' for i in range(nterms)]
	ft(vis=ms, nterms=nterms, model=models, usescratch=True)
self_calibrate(4, 'ea12')

# Image using cal 4
tclean(vis=["cconfig-p4.ms", "dconfig1-p4.ms", "dconfig2-p4.ms"],
	imagename='image-p4',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=20000, gain=0.1, threshold='0.02mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	scales=[0, 4, 8, 16],
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
# Set model from cal 4
for ms in [f'{d}-p4.ms' for d in datasets]:
	clearcal(ms)
	models = [f'image-p4.model.tt{i}' for i in range(nterms)]
	ft(vis=ms, nterms=nterms, model=models, usescratch=True)
# Make cal 5
self_calibrate(5, 'ea12')

# Image using cal 5
tclean(vis=["cconfig-p5.ms", "dconfig1-p5.ms", "dconfig2-p5.ms"],
	imagename='image-p5',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=20000, gain=0.1, threshold='0.02mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	scales=[0, 4, 8, 16],
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
# Set model from cal 5
for ms in [f'{d}-p5.ms' for d in datasets]:
	clearcal(ms)
	models = [f'image-p5.model.tt{i}' for i in range(nterms)]
	ft(vis=ms, nterms=nterms, model=models, usescratch=True)
# Make cal 6
self_calibrate(6, 'ea12')

# Make final image
tclean(vis=["cconfig-p6.ms", "dconfig1-p6.ms", "dconfig2-p6.ms"],
	imagename='image-p6',
	imsize=[2304, 2304], cell=['0.5arcsec','0.5arcsec'],
	specmode='mfs', niter=20000, gain=0.1, threshold='0.008mJy',
	deconvolver='mtmfs', pblimit=-1.e-6,
	stokes='I', weighting='briggs', robust=0.5, pbcor=False,
	scales=[0, 4, 8, 16],
	usemask='auto-multithresh', noisethreshold=5, sidelobethreshold=1.25,
	lownoisethreshold=2, minbeamfrac=0.1, negativethreshold=0.0, fastnoise=False)
