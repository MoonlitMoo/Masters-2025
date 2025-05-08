import os
import shutil

from casatasks import flagmanager, gencal, plotweather, clearcal, applycal, gaincal, fluxscale, setjy, bandpass

FLAGGING_STEPS = [
    'base_flagging',
    'primary',
    'primary_2',
    'secondary',
    'secondary_2'
]

def flag_versions(msname):
    """ Retrieves all flag version names. """
    versions = {v['name'] for k, v in flagmanager(vis=msname, mode='list').items() if k != "MS"}
    return versions

def clean_flag_versions(msname, skip=None, dry_run=False):
    """ Removes all flag versions not part of the flagging steps + skip. Use with caution. """
    if skip is None:
        skip = []
    versions = flag_versions(msname)
    extra_versions = set(versions) - set(FLAGGING_STEPS) - set(skip)
    if dry_run:
        print(f"Found extra versions: {extra_versions if extra_versions else 'None'}")
    for v in extra_versions:
        flagmanager(vis=msname, mode='delete', versionname=v)

def remove_calibration(name, target: str, dry_run=False):
    """
    Removes directories in the current working directory whose names match the calibration suffix.

    Parameters
    ----------
    target : str
        The calibration suffix to remove
    """
    cwd = os.getcwd()
    for entry in os.listdir(cwd):
        full_path = os.path.join(cwd, entry)
        if os.path.isdir(full_path) and entry == f'{name}.{target}':
            print(f"Removing calibration: {entry}")
            if not dry_run:
                shutil.rmtree(full_path)

def apriori_tables(name):
    """ Returns the apriori gaintables as a list. """
    cals = [f'{name}.gc', f'{name}.opac', f'{name}.rq']
    if f'{name}.antpos' in os.listdir(os.getcwd()):
        cals.append(f'{name}.antpos')
    return cals

def interp_modes(tables, nearest=None):
    """ Returns the interp modes for the corresponding gain tables.
    By default, it uses nearest for bandpass and delay, else linear
    """
    if nearest is None:
        nearest = ["B0", "K0"]
    return ["linear" for t in tables if t.split(".")[-1] not in nearest]

def secondary_gainfields(tables, name, p_calibrator, s_calibrator):
    """ Returns the gain fields for the secondary calibration to use. """
    res = []
    for t in tables:
        if t in apriori_tables(name):
            # If aprior, no field
            res.append('')
        else:
            # Otherwise gain calibrations are secondary
            ext = t.split('.')[-1]
            if ext in ['K0', 'B0']:
                res.append(p_calibrator)
            else:
                res.append(s_calibrator)
    return res


def apriori_calibration(msname, name):
    """ Get the basic calibrations that aren't data-dependent.
    Removes existing ones before rerunning calibration steps.
    """
    # Get the gain curve calibration
    remove_calibration(name, 'gc')
    gencal(vis=msname, caltable=f'{name}.gc', caltype='gc')
    # Get the opacity calibration. We specify the spw string because the documentation said it was non-trivial :)
    remove_calibration(name, 'opac')
    tau = plotweather(vis=msname, doPlot=True, plotName='plots/weather.png')
    spw_list = ','.join([str(i) for i in range(32)])
    gencal(vis=msname, caltable=f'{name}.opac', caltype='opac', spw=spw_list, parameter=tau)
    # Get the requantisation calibration
    remove_calibration(name, 'rq')
    gencal(vis=msname, caltable=f'{name}.rq', caltype='rq')
    # Get the antenna position calibrations
    remove_calibration(name, 'antpos')
    gencal(vis=msname, caltable=f'{name}.antpos', caltype='antpos')
    print("Finished apriori calibration")

def primary_pre_calibration(msname, name, p_calibrator, refant, spw_string, flag_version=FLAGGING_STEPS[1]):
    """ Runs all initial calibration steps on the first pass calibrated primary data.
    Resets to flag version before running.
    """
    # Reset flags to 'primary'
    if flag_version in flag_versions(msname):
        flagmanager(vis=msname, mode='restore', versionname=flag_version)
    else:
        raise ValueError(f"Flagging version '{flag_version}' not found in flagmanager.")
    # Set the flux model for the primary calibrator
    setjy(vis=msname, field=p_calibrator, standard='Perley-Butler 2017', model='3C48_X.im',
          usescratch=True, scalebychan=True)
    # Get inital phase calibration
    remove_calibration(name, 'G0')
    gaincal(vis=msname, caltable=f'{name}.G0', field=p_calibrator, refant=refant, spw=spw_string,
            gaintype='G', calmode='p', solint='int', minsnr=5, gaintable=apriori_tables(name))
    # Get the delay calibration
    remove_calibration(name, 'K0')
    gaintables = apriori_tables(name) + [f'{name}.G0']
    gaincal(vis=msname, caltable=f'{name}.K0', field=p_calibrator, refant=refant,
            spw='*:5~58', gaintype='K', solint='inf', combine='scan', minsnr=5,
            gaintable=gaintables)
    # Get the bandpass solution
    remove_calibration(name, 'B0')
    gaintables += [f'{name}.K0']
    bandpass(vis=msname, caltable=f'{name}.B0', field=p_calibrator,
        refant=refant, combine='scan', solint='inf', bandtype='B',
        gaintable=gaintables)
    # Get a better amp + phase solution
    remove_calibration(name, 'G1')
    gaintables = apriori_tables(name) + [f'{name}.B0', f'{name}.K0']
    gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
            solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
            gaintable=gaintables,
            interp=interp_modes(gaintables))


def primary_post_calibration(msname, name, p_calibrator, refant, flag_version=FLAGGING_STEPS[2]):
    """ Runs the gain calibration on the final primary calibration. Resets to the given flag version before running. """
    # Reset flags to 'primary'
    if flag_version in flag_versions(msname):
        flagmanager(vis=msname, mode='restore', versionname=flag_version)
    else:
        raise ValueError(f"Flagging version '{flag_version}' not found in flagmanager.")
    # Run the phase only calibration
    remove_calibration(name, "G1")
    gaintables = apriori_tables(name) + [f'{name}.B0', f'{name}.K0']
    gaincal(vis=msname, caltable=f'{name}.G1', field=p_calibrator, spw='*:5~58',
            solint='inf', refant=refant, gaintype='G', calmode='p', solnorm=False,
            gaintable=gaintables,
            interp=interp_modes(gaintables))
    # Run the phase + amp calibration
    remove_calibration(name, "G2")
    gaintables += [f'{name}.G1']
    gaincal(vis=msname, caltable=f'{name}.G2', field=p_calibrator, spw='*:5~58',
            solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
            gaintable=gaintables,
            interp=interp_modes(gaintables))
    # Run the final gain calibration
    gaincal(vis=msname, caltable=f'{name}.G3', field=p_calibrator, spw='*:5~58',
            solint='inf', refant=refant, gaintype='G', calmode='ap', solnorm=False,
            gaintable=gaintables,
            interp=interp_modes(gaintables))

def secondary_pre_calibration(msname, name, p_calibrator, s_calibrator, refant,
                              flag_version=FLAGGING_STEPS[3], primary_flag_version=FLAGGING_STEPS[2]):
    primary_post_calibration(msname, name, p_calibrator, refant, primary_flag_version)
    if flag_version in flag_versions(msname):
        flagmanager(vis=msname, mode='restore', versionname=flag_version)
    else:
        raise ValueError(f"Flagging version '{flag_version}' not found in flagmanager.")
    # Clear any calibration in s_calibrator for cleanup
    clearcal(vis=msname, field=s_calibrator)
    # Extend the phase calibration, use interp as the default linear
    gaintables = apriori_tables(name) + [f'{name}.B0', f'{name}.K0']
    gaincal(vis=msname, caltable=f'{name}.G1', field=s_calibrator,
            spw='*:5~58', solint='int', refant=refant, gaintype='G', calmode='p',
            gaintables=gaintables, append=True)
    # Get the phase + amp calibration to create the flux model
    gaintables += [f'{name}.G1']
    gaincal(vis=msname, caltable=f'{name}.G2', field=s_calibrator,
            spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='ap',
            gaintable=gaintables,
            gainfield=secondary_gainfields(gaintables, name, p_calibrator, s_calibrator),
            interp=interp_modes(gaintables),
            append=True)
    # Add the fluxmodel to secondary calibrator
    remove_calibration(name, "fluxscale1")
    myscale = fluxscale(vis=msname, caltable=f'{name}.G2', fluxtable=f'{name}.fluxscale1',
                        reference=p_calibrator, transfer=[s_calibrator],
                        incremental=False)
    setjy(vis=msname, field=s_calibrator, standard='fluxscale', fluxdict=myscale)
    # Create the final gain calibration
    gaincal(vis=msname, caltable=f'{name}.G3', field=s_calibrator,
            spw='*:5~58', solint='inf', refant=refant, gaintype='G', calmode='ap',
            gaintable=gaintables,
            gainfield=secondary_gainfields(gaintables, name, p_calibrator, s_calibrator),
            interp=interp_modes(gaintables),
            append=True)


def secondary_post_calibration(msname, name, p_calibrator, s_calibrator, refant, flag_version=FLAGGING_STEPS[4], primary_flag_version=FLAGGING_STEPS[2]):
    """ Re-runs the secondary calibration using the post flagged secondary version. """
    secondary_pre_calibration(msname, name, p_calibrator, s_calibrator, refant, flag_version, primary_flag_version)

def apply_initial_calibration(msname, name, p_calibrator):
    """ Applies initial calibration to the primary calibrator. """
    gaintables = apriori_tables(name) + [f'{name}.K0', f'{name}.B0', f'{name}.G1']
    applycal(vis=msname, field=p_calibrator,
             gaintable=gaintables,
             interp=interp_modes(gaintables),
             calwt=False, flagbackup=False)

def apply_calibration(msname, name, field, p_calibrator, s_calibrator=None):
    """ Applies full calibration to given field. """
    gaintables = apriori_tables(name) + [f'{name}.G3', f'{name}.G1', f'{name}.K0', f'{name}.B0']
    if s_calibrator is not None:
        gainfield = secondary_gainfields(gaintables, name, p_calibrator, s_calibrator)
    else:
        gainfield = ['' for _ in gaintables]
    interp = interp_modes(gaintables)
    applycal(vis=msname, field=field,
             gaintable=gaintables,
             gainfield=gainfield,
             interp=interp,
             calwt=False, flagbackup=False)
