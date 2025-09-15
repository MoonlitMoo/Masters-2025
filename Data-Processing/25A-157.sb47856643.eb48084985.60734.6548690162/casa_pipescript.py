# This CASA pipescript is meant for use with CASA 6.6.1 and pipeline 2024.1.0.8
context = h_init()
context.set_state('ProjectSummary', 'observatory', 'Karl G. Jansky Very Large Array')
context.set_state('ProjectSummary', 'telescope', 'EVLA')
try:
    hifv_importdata(vis=['25A-157.sb47856643.eb48084985.60734.6548690162.ms'])
    hifv_flagdata(hm_tbuff='1.5int', fracspw=0.01, intents='*POINTING*,*FOCUS*,*ATMOSPHERE*,*SIDEBAND_RATIO*, *UNKNOWN*, *SYSTEM_CONFIGURATION*, *UNSPECIFIED#UNSPECIFIED*')
    hifv_vlasetjy()
    hifv_priorcals(show_tec_maps=False)
    hifv_aoflagger(flag_target='"0137+331=3C48"', aoflagger_file='light.lua')
    hifv_testBPdcals()
    hifv_semiFinalBPdcals()
    hifv_aoflagger(flag_target='J2136+0041', aoflagger_file='light.lua', use_corrected=True)
    hifv_aoflagger(flag_target='J2253+1608', aoflagger_file='light.lua', use_corrected=True)
    hifv_aoflagger(flag_target='J0022+0014', aoflagger_file='J0022+0014.lua', use_corrected=True)
    hifv_solint()
    hifv_fluxboot()
    hifv_finalcals()
    # Smooth over the J0022+0014 solutions.
    # Step 1, bandpass 1 sol per scan per antenna per spw. This is to get the right shape for the final bandpass
    bandpass(vis='finalcalibrators.ms', caltable='testphase_inf_b_allspw.b',
        field='J0022+0014', combine='', minsnr=5.0, bandtype='B', parang=True)
    # Step 2, phase sol using good antenna from the weblog
    gaincal(vis='finalcalibrators.ms',
        caltable='final_field5_gain_good_spw_avged/',
        field='J0022+0014', spw='0~22', solint='int', combine='spw', preavg=-1.0,
        refant='ea15,ea16,ea20,ea26,ea25,ea02,ea17,ea08,ea19,ea07,ea06,ea14,ea09,ea27,ea03,ea22,ea12,ea28,ea04,ea18,ea11,ea23,ea24,ea13,ea10',
        refantmode='flex', minblperant=4, minsnr=3.0, solnorm=False, gaintype='G',
        calmode='p', parang=True)
    # Step 3, fit the gradient sols
    execfile('fit_bpsols.py')
    # Apply the calibrations to the fields
    applycal(vis=msname, field='5,6',
        gaintable=['25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_2.gc.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_3.opac.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_4.rq.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_6.ants.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_2.finaldelay.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_4.finalBPcal.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_5.averagephasegain.tbl',
            'final_field5_gain_good_spw_avged',
            'bptable_fitted.b'],
        gainfield=['', '', '', '', '', '', '', '', ''],
        interp=['', '', '', '', '', 'linear,linearflag', '', '', ''],
        spwmap=[[], [], [], [], [], [], [], 32*[0], []],
        calwt=[False, False, False, False, False, False, False, False, False],
        parang=True, applymode='calflagstrict', flagbackup=True)
    applycal(vis=msname, field='0~4,7',
        gaintable=[
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_2.gc.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_3.opac.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_4.rq.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_priorcals.s4_6.ants.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_2.finaldelay.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_4.finalBPcal.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_5.averagephasegain.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_7.finalampgaincal.tbl',
            '25A-157.sb47856643.eb48084985.60734.6548690162.ms.hifv_finalcals.s13_8.finalphasegaincal.tbl'],
        gainfield=['', '', '', '', '', '', '', '', ''],
        interp=['', '', '', '', '', 'linear,linearflag', '', '', ''],
        calwt=[False, False, False, False, False, False, False, False, False],
        parang=True, applymode='calflagstrict', flagbackup=True)
    # Return to flagging
    hifv_aoflagger(flag_target='RXJ2129+0005', aoflagger_file='science.lua')
    hifv_aoflagger(flag_target='A2626', aoflagger_file='science.lua')
    hifv_aoflagger(flag_target='ACTJ0022-0036', aoflagger_file='science.lua')
    hifv_statwt()
    hifv_plotsummary()
    hifv_exportdata()
finally:
    h_save()

