# This CASA pipescript is meant for use with CASA 6.6.1 and pipeline 2024.1.0.8
context = h_init()
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array')
context.set_state('ProjectSummary', 'telescope', 'EVLA')
try:
    hifv_importdata(vis=['25A-157.sb47895952.eb48256632.60761.33700966435.ms'])
    hifv_flagdata(hm_tbuff='1.5int', fracspw=0.01, intents='*POINTING*,*FOCUS*,*ATMOSPHERE*,*SIDEBAND_RATIO*, *UNKNOWN*, *SYSTEM_CONFIGURATION*, *UNSPECIFIED#UNSPECIFIED*')
    hifv_vlasetjy()
    hifv_priorcals(show_tec_maps=False)
    hifv_testBPdcals()
    hifv_semiFinalBPdcals()
    hifv_aoflagger(flag_target='0', aoflagger_file='J1616+0459.lua')
    hifv_aoflagger(flag_target='2', aoflagger_file='J1719+1745.lua')
    hifv_solint()
    hifv_fluxboot()
    # hifv_finalcals()
    # hifv_applycals()
    # hifv_aoflagger(flag_target='2A0335+096', aoflagger_file='2A0335+096.lua', use_corrected=True)
    # hifv_statwt()
    # hifv_plotsummary()
    # hifv_exportdata()
finally:
    h_save()

