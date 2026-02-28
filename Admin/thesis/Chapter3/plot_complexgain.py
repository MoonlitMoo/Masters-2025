# Run inside CASA Python so casatools is available
from casatools import table
import numpy as np
import matplotlib.pyplot as plt

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 10 * f_scale

def _hours_since(t):
    t0 = np.nanmin(t)
    return (t - t0) / 3600.0

def plot_amp_vs_time_by_antenna(path, field_id=1, spw_id=0, use_corrected=False, pol=0, chan_avg=True):
    """
    path:   caltable or MS path
    field_id, spw_id: selection
    use_corrected: if MS, use CORRECTED_DATA instead of DATA
    pol:    polarisation index to plot (0 is usually fine)
    chan_avg: average amplitude over channels (recommended for thesis-style plots)
    """
    tb.open(path)
    cols = set(tb.colnames())
    tb.close()

    # ---------- CASE A: Calibration table (gaincal output) ----------
    tb.open(path)

    time = tb.getcol("TIME")                 # shape (nrow,)
    ant  = tb.getcol("ANTENNA1")             # shape (nrow,)
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")   # shape (nrow,)

    # Some caltables also have FIELD_ID; if missing, field selection isn't applicable
    if "FIELD_ID" in cols:
        fld = tb.getcol("FIELD_ID")
        row_sel = (spw == spw_id) & (fld == field_id)
    else:
        row_sel = (spw == spw_id)

    # CPARAM shape: (npol, nchan, nrow)
    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]

    # flags optional
    if "FLAG" in cols:
        flag = tb.getcol("FLAG")[:, :, row_sel].astype(bool)
    else:
        flag = None

    tb.close()

    # amplitude
    amp = np.abs(cparam[pol, :, :])  # (nchan, nrow_sel)
    if flag is not None:
        amp = np.where(flag[pol, :, :], np.nan, amp)
        
    print(amp.shape)
    if chan_avg:
        amp = np.nanmean(amp, axis=0)  # (nrow_sel,)
    else:
        # flatten channel dimension for scatter
        amp = amp.reshape(-1)
        t_sel = np.repeat(t_sel, cparam.shape[1])
        a_sel = np.repeat(a_sel, cparam.shape[1])

    x = _hours_since(t_sel)

    # ---------- Plot ----------
    cal_ranges = [(6, -0.0004166666666666667, 0.020416666666666666),
        (7, 0.02125, 0.035416666666666666),
        (9, 0.17958333333333334, 0.19375),
        (11, 0.3370833330684238, 0.35125),
        (13, 0.49541666640175713, 0.5095833333333334),
        (15, 0.6529166666666667, 0.6670833335982429),
        (17, 0.81125, 0.8254166669315762),
        (19, 0.96875, 0.9829166666666667),
        (21, 1.12625, 1.14125),
        (23, 1.2845833333333334, 1.29875)]

    ants = np.unique(a_sel)[1:5]
    plt.figure()
    for ai in ants:
        m = (a_sel == ai)
        plt.scatter(x[m], amp[m], s=30, zorder=1, label=f"Antenna {ai}")
        # plt.plot(x[m], amp[m], alpha=0.7, linewidth=1)
        plt.step(x[m], amp[m], where="post", lw=1.0, alpha=0.7)

    # science_ranges: list of (t0_hr, t1_hr) tuples in hours-since-start
    t_offset = -0.025  # Slight offset because I aligned wrong
    for (s, t0, t1) in cal_ranges:
        if s == 6:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red', label="Calibrator scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red')

    for i, sc in enumerate(cal_ranges[1:-1]):
        s = sc[0]
        t0 = sc[2] + 0.01
        t1 = cal_ranges[i+2][1] - 0.01
        if s == 9:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0, label="Science scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0)


    plt.axhline(1, c='k', linestyle='--', zorder=-10)
    plt.xlabel("Time (hours since start)")
    plt.ylabel("Complex Gain amplitude")
    plt.grid(alpha=0.5)
    plt.legend()
    plt.tight_layout()

f_scale = 1.0
plt.rcParams['axes.labelsize'] = 14 * f_scale
plt.rcParams['axes.titlesize'] = 16 * f_scale
plt.rcParams['xtick.labelsize'] = 12 * f_scale
plt.rcParams['ytick.labelsize'] = 12 * f_scale
plt.rcParams['legend.fontsize'] = 12 * f_scale

def _hours_since(t):
    t0 = np.nanmin(t)
    return (t - t0) / 3600.0

def plot_amp_vs_time_by_antenna(path, field_id=1, spw_id=0, pol=0, chan_avg=True):
    """
    path:   caltable or MS path
    field_id, spw_id: selection
    use_corrected: if MS, use CORRECTED_DATA instead of DATA
    pol:    polarisation index to plot (0 is usually fine)
    chan_avg: average amplitude over channels (recommended for thesis-style plots)
    """
    tb.open(path)
    cols = set(tb.colnames())
    tb.close()

    # ---------- CASE A: Calibration table (gaincal output) ----------
    tb.open(path)

    time = tb.getcol("TIME")                 # shape (nrow,)
    ant  = tb.getcol("ANTENNA1")             # shape (nrow,)
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")   # shape (nrow,)

    # Some caltables also have FIELD_ID; if missing, field selection isn't applicable
    if "FIELD_ID" in cols:
        fld = tb.getcol("FIELD_ID")
        row_sel = (spw == spw_id) & (fld == field_id)
    else:
        row_sel = (spw == spw_id)

    # CPARAM shape: (npol, nchan, nrow)
    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]

    # flags optional
    if "FLAG" in cols:
        flag = tb.getcol("FLAG")[:, :, row_sel].astype(bool)
    else:
        flag = None

    tb.close()

    # amplitude
    amp = np.abs(cparam[pol, :, :])  # (nchan, nrow_sel)
    if flag is not None:
        amp = np.where(flag[pol, :, :], np.nan, amp)
        
    if chan_avg:
        amp = np.nanmean(amp, axis=0)  # (nrow_sel,)
    else:
        # flatten channel dimension for scatter
        amp = amp.reshape(-1)
        t_sel = np.repeat(t_sel, cparam.shape[1])
        a_sel = np.repeat(a_sel, cparam.shape[1])

    # Phase
    x = _hours_since(t_sel)

    # ---------- Plot ----------
    cal_ranges = [(6, -0.0004166666666666667, 0.020416666666666666),
        (7, 0.02125, 0.035416666666666666),
        (9, 0.17958333333333334, 0.19375),
        (11, 0.3370833330684238, 0.35125),
        (13, 0.49541666640175713, 0.5095833333333334),
        (15, 0.6529166666666667, 0.6670833335982429),
        (17, 0.81125, 0.8254166669315762),
        (19, 0.96875, 0.9829166666666667),
        (21, 1.12625, 1.14125),
        (23, 1.2845833333333334, 1.29875)]

    ants = np.unique(a_sel)[:5]
    plt.figure()
    for ai in ants:
        m = (a_sel == ai)
        plt.scatter(x[m], amp[m], s=30, zorder=1, label=f"Antenna {ai}")
        # plt.plot(x[m], amp[m], alpha=0.7, linewidth=1)
        plt.step(x[m], amp[m], where="post", lw=1.0, alpha=0.7)

    # science_ranges: list of (t0_hr, t1_hr) tuples in hours-since-start
    t_offset = -0.025  # Slight offset because I aligned wrong
    for (s, t0, t1) in cal_ranges:
        if s == 6:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red', label="Calibrator scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red')

    for i, sc in enumerate(cal_ranges[1:-1]):
        s = sc[0]
        t0 = sc[2] + 0.01
        t1 = cal_ranges[i+2][1] - 0.01
        if s == 9:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0, label="Science scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0)


    plt.axhline(1, c='k', linestyle='--', zorder=-10)
    plt.xlabel("Time (hours since start)")
    plt.ylabel("Complex Gain amplitude")
    plt.grid(alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("gainamp.pdf", dpi=300, bbox_inches='tight')

def plot_phase_vs_time_by_antenna(path, field_id=1, spw_id=0, pol=0, chan_avg=True):
    """
    path:   caltable or MS path
    field_id, spw_id: selection
    use_corrected: if MS, use CORRECTED_DATA instead of DATA
    pol:    polarisation index to plot (0 is usually fine)
    chan_avg: average amplitude over channels (recommended for thesis-style plots)
    """
    tb.open(path)
    cols = set(tb.colnames())
    tb.close()

    # ---------- CASE A: Calibration table (gaincal output) ----------
    tb.open(path)

    time = tb.getcol("TIME")                 # shape (nrow,)
    ant  = tb.getcol("ANTENNA1")             # shape (nrow,)
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")   # shape (nrow,)

    # Some caltables also have FIELD_ID; if missing, field selection isn't applicable
    if "FIELD_ID" in cols:
        fld = tb.getcol("FIELD_ID")
        row_sel = (spw == spw_id) & (fld == field_id)
    else:
        row_sel = (spw == spw_id)

    # CPARAM shape: (npol, nchan, nrow)
    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]

    # flags optional
    if "FLAG" in cols:
        flag = tb.getcol("FLAG")[:, :, row_sel].astype(bool)
    else:
        flag = None

    tb.close()

    # Phase
    # Average over channels
    gains = cparam[pol, :, :]
    gains = np.mean(gains, axis=0)

    # Phase in degrees
    phase = np.angle(gains, deg=True)

    # Wrap to [-180, 180]
    phase = (phase + 180) % 360 - 180

    # Phase
    x = _hours_since(t_sel)

    # ---------- Plot ----------
    cal_ranges = [(6, -0.0004166666666666667, 0.020416666666666666),
        (7, 0.02125, 0.035416666666666666),
        (9, 0.17958333333333334, 0.19375),
        (11, 0.3370833330684238, 0.35125),
        (13, 0.49541666640175713, 0.5095833333333334),
        (15, 0.6529166666666667, 0.6670833335982429),
        (17, 0.81125, 0.8254166669315762),
        (19, 0.96875, 0.9829166666666667),
        (21, 1.12625, 1.14125),
        (23, 1.2845833333333334, 1.29875)]

    ants = np.unique(a_sel)[1:4]
    plt.figure()
    for ai in ants:
        m = (a_sel == ai)
        plt.scatter(x[m], phase[m], s=30, zorder=1, label=f"Antenna {ai}")
        # plt.plot(x[m], phase[m], alpha=0.7, linewidth=1)
        plt.step(x[m], phase[m], where="post", lw=1.0, alpha=0.7)

    # science_ranges: list of (t0_hr, t1_hr) tuples in hours-since-start
    t_offset = -0.025  # Slight offset because I aligned the x-axis wrong
    for (s, t0, t1) in cal_ranges:
        if s == 6:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red', label="Calibrator scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.08, zorder=0, facecolor='red')

    for i, sc in enumerate(cal_ranges[1:-1]):
        s = sc[0]
        t0 = sc[2] + 0.01
        t1 = cal_ranges[i+2][1] - 0.01
        if s == 9:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0, label="Science scan")
        else:
            plt.axvspan(t0+t_offset, t1+t_offset, alpha=0.05, zorder=0)


    plt.axhline(1, c='k', linestyle='--', zorder=-10)
    plt.xlabel("Time (hours since start)")
    plt.ylabel("Complex Gain phase (degrees)")
    plt.grid(alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("gainphase.pdf", dpi=300, bbox_inches='tight')

def plot_gain_amp_phase(path_amp, path_phase, field_id=1, spw_id=0, pol=0, chan_avg=True):

    fig, (ax_amp, ax_phase) = plt.subplots(
        1, 2, figsize=(8, 4), sharex=True
    )

    # ------------------ AMPLITUDE ------------------
    tb.open(path_amp)
    cols = set(tb.colnames())
    time = tb.getcol("TIME")
    ant  = tb.getcol("ANTENNA1")
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")

    if "FIELD_ID" in cols:
        fld = tb.getcol("FIELD_ID")
        row_sel = (spw == spw_id) & (fld == field_id)
    else:
        row_sel = (spw == spw_id)

    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]
    tb.close()

    amp = np.abs(cparam[pol, :, :])
    if chan_avg:
        amp = np.nanmean(amp, axis=0)

    x = _hours_since(t_sel)

    ants = np.unique(a_sel)[1:4]
    for ai in ants:
        m = (a_sel == ai)
        ax_amp.step(x[m], amp[m], where="post", lw=1.0, alpha=0.7, label=f"Antenna {ai}")
        ax_amp.scatter(x[m], amp[m], s=20)

    ax_amp.axhline(1, c='k', linestyle='--')
    ax_amp.set_ylabel("Gain amplitude")
    ax_amp.grid(alpha=0.5)

    # ------------------ PHASE ------------------
    tb.open(path_phase)
    time = tb.getcol("TIME")
    ant  = tb.getcol("ANTENNA1")
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")

    if "FIELD_ID" in cols:
        fld = tb.getcol("FIELD_ID")
        row_sel = (spw == spw_id) & (fld == field_id)
    else:
        row_sel = (spw == spw_id)

    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]
    tb.close()

    gains = np.mean(cparam[pol, :, :], axis=0)
    phase = np.angle(gains, deg=True)
    phase = (phase + 180) % 360 - 180

    x = _hours_since(t_sel)

    for ai in ants:
        m = (a_sel == ai)
        ax_phase.step(x[m], phase[m], where="post", lw=1.0, alpha=0.7, label=f"Antenna {ai}")
        ax_phase.scatter(x[m], phase[m], s=20)

    # Plot the scan times
    cal_ranges = [(6, -0.0004166666666666667, 0.020416666666666666),
        (7, 0.02125, 0.035416666666666666),
        (9, 0.17958333333333334, 0.19375),
        (11, 0.3370833330684238, 0.35125),
        (13, 0.49541666640175713, 0.5095833333333334),
        (15, 0.6529166666666667, 0.6670833335982429),
        (17, 0.81125, 0.8254166669315762),
        (19, 0.96875, 0.9829166666666667),
        (21, 1.12625, 1.14125),
        (23, 1.2845833333333334, 1.29875)]
    al = 0.08
    for ax in (ax_amp, ax_phase):
        t_offset = -0.025  # Slight offset because I aligned the x-axis wrong
        for (s, t0, t1) in cal_ranges:
            if s == 6:
                ax.axvspan(t0+t_offset, t1+t_offset, alpha=al, zorder=0, facecolor='red', label="Calibrator scan")
            else:
                ax.axvspan(t0+t_offset, t1+t_offset, alpha=al, zorder=0, facecolor='red')

        for i, sc in enumerate(cal_ranges[1:-1]):
            s = sc[0]
            t0 = sc[2] + 0.01
            t1 = cal_ranges[i+2][1] - 0.01
            if s == 9:
                ax.axvspan(t0+t_offset, t1+t_offset, alpha=al, zorder=0, label="Science scan")
            else:
                ax.axvspan(t0+t_offset, t1+t_offset, alpha=al, zorder=0)

    ax_phase.set_ylabel("Gain phase (deg)")
    fig.supxlabel("Time (hours since start)")
    ax_phase.grid(alpha=0.5)

    ax_amp.legend(loc="best", fontsize=10)

    plt.tight_layout()
    plt.savefig("gain_amp_phase.pdf", dpi=300, bbox_inches='tight')

plot_gain_amp_phase(
    "25A-157.sb47896587.eb48188930.60749.83678572917.ms.hifv_finalcals.s13_7.finalampgaincal.tbl",
    "25A-157.sb47896587.eb48188930.60749.83678572917.ms.hifv_finalcals.s13_8.finalphasegaincal.tbl", 
    field_id=1, spw_id=0)
# # Example usage:
# plot_phase_vs_time_by_antenna("25A-157.sb47896587.eb48188930.60749.83678572917.ms.hifv_finalcals.s13_8.finalphasegaincal.tbl", field_id=1, spw_id=0)
# # Example usage:
# plot_amp_vs_time_by_antenna("25A-157.sb47896587.eb48188930.60749.83678572917.ms.hifv_finalcals.s13_7.finalampgaincal.tbl", field_id=1, spw_id=0)