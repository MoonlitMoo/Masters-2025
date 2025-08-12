# This CASA pipescript is meant for use with CASA 6.6.1 and pipeline 2024.1.0.8
context = h_init()
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array')
context.set_state('ProjectSummary', 'telescope', 'EVLA')
try:
    hifv_importdata(vis=['25A-157.sb47894310.eb48187719.60748.13153532408.ms'])
    hifv_flagdata(hm_tbuff='1.5int', fracspw=0.01, intents='*POINTING*,*FOCUS*,*ATMOSPHERE*,*SIDEBAND_RATIO*, *UNKNOWN*, *SYSTEM_CONFIGURATION*, *UNSPECIFIED#UNSPECIFIED*')
    # Use cmd from fluxboot of completed run
    setjy(vis='25A-157.sb47894310.eb48187719.60748.13153532408.ms', field='J1041+0610', selectdata=False, scalebychan=True, standard='manual', listmodels=False,
          fluxdensity=[1.4146190509987009, 0, 0, 0], spix=[-0.027926005929645285, 0.00695211606663196], reffreq='9812223841.172163Hz', usescratch=True)
    # Continue now that jy scale is correct
    hifv_aoflagger(flag_target='J1041+0610', aoflagger_file='J1041+0610.lua')
    hifv_priorcals(show_tec_maps=False)
    hifv_testBPdcals()
    hifv_semiFinalBPdcals()
    # Set up all the calib tables
    calibs = ['25A-157.sb47894310.eb48187719.60748.13153532408.ms.hifv_priorcals.s4_2.gc.tbl',
              '25A-157.sb47894310.eb48187719.60748.13153532408.ms.hifv_priorcals.s4_3.opac.tbl',
              '25A-157.sb47894310.eb48187719.60748.13153532408.ms.hifv_priorcals.s4_4.rq.tbl',
              '25A-157.sb47894310.eb48187719.60748.13153532408.ms.hifv_semiFinalBPdcals.s6_2.delay_X.tbl',
              '25A-157.sb47894310.eb48187719.60748.13153532408.ms.hifv_semiFinalBPdcals.s6_4.BPcal_X.tbl']
    interps = ['', '', '', '', 'linear,linearflag']
    # Then everything is maybe correct, finalcal doesn't work since no secondary (as far as I can tell), do it manually
    gaincal(vis='25A-157.sb47894310.eb48187719.60748.13153532408.ms', caltable='phaseshortgaincal.tbl', field='0', spw='',
        solint='int', combine='scan', refant='', refantmode='flex', minsnr=3.0,
        solnorm=False, gaintype='G', calmode='p', parang=True,
        gaintable=calibs, interp=interps)
    gaincal(vis='25A-157.sb47894310.eb48187719.60748.13153532408.ms', caltable='finalampgaincal.tbl', field='0', spw='',
        solint='222.0s', combine='scan', refant='', refantmode='flex',
        minsnr=5.0, solnorm=False, gaintype='G', calmode='ap',
        gaintable=calibs + ['phaseshortgaincal.tbl'], interp=interps + [''], parang=True)
    gaincal(vis='25A-157.sb47894310.eb48187719.60748.13153532408.ms', caltable='finalphasegaincal.tbl', field='0', spw='',
        solint='222.0s', combine='scan', refant='', refantmode='flex',
        minsnr=3.0, solnorm=False, gaintype='G',calmode='p',
        gaintable=calibs + ['phaseshortgaincal.tbl'], interp=interps + [''], parang=True)
    # Apply cals
    applycal(vis='25A-157.sb47894310.eb48187719.60748.13153532408.ms', field='0,1',
             gaintable=calibs + ['finalampgaincal.tbl', 'finalphasegaincal.tbl'],
             interp= interps + ['', ''],
             parang=True, applymode='calflagstrict', flagbackup=True)
    hifv_aoflagger(flag_target='Z3146', aoflagger_file='Z3146.lua', use_corrected=True)
    hifv_statwt()
    hifv_exportdata()
finally:
    h_save()

