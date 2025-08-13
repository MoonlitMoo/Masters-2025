# This CASA pipescript is meant for use with CASA 6.6.1 and pipeline 2024.1.0.8
context = h_init()
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array')
context.set_state('ProjectSummary', 'telescope', 'EVLA')
try:
    hifv_importdata(vis=['25A-157.sb47894939.eb48078696.60734.16955045139.ms'])
    hifv_flagdata(hm_tbuff='1.5int', fracspw=0.01, intents='*POINTING*,*FOCUS*,*ATMOSPHERE*,*SIDEBAND_RATIO*, *UNKNOWN*, *SYSTEM_CONFIGURATION*, *UNSPECIFIED#UNSPECIFIED*')
    hifv_vlasetjy()
    hifv_priorcals(show_tec_maps=False)
    hifv_aoflagger(flag_target='"1331+305=3C286"', aoflagger_file='light.lua')
    hifv_testBPdcals()
    hifv_semiFinalBPdcals()
    hifv_aoflagger(flag_target='J1150+2417', aoflagger_file='light.lua', use_corrected=True)
    hifv_solint()
    hifv_fluxboot()
    hifv_finalcals()
    hifv_applycals()
    hifv_aoflagger(flag_target='A1413', aoflagger_file='A1413.lua', use_corrected=True)
    hifv_statwt()
    hifv_plotsummary()
    hifv_exportdata()
finally:
    h_save()

