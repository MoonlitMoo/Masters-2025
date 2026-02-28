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


def plot_bandpass_amp_phase_vs_freq(
    bp_table,
    spw_id=0,
    ant_id=None,
    field_id=None,
    pol_map=None,          # e.g. {"LL": 0, "RR": 1}
    ms_path=None,
    avg_over_time=True,    # typical for bandpass tables
    savepath="bandpass_amp_phase.pdf",
):
    """
    Plot bandpass solutions vs frequency for one SPW.

    bp_table:  bandpass caltable (e.g. from bandpass)
    spw_id:    SPW to plot
    ant_id:    antenna to plot (int). If None, uses the first antenna in selection.
    field_id:  optional FIELD_ID selection if present in table
    pol_map:   mapping of pol labels to indices in CPARAM (defaults to {"LL":0,"RR":1} if possible)
    ms_path:   MS path to read channel frequencies (recommended)
    """

    # ---- read table columns ----
    tb.open(bp_table)
    cols = set(tb.colnames())

    time = tb.getcol("TIME")
    ant  = tb.getcol("ANTENNA1")
    spw  = tb.getcol("SPECTRAL_WINDOW_ID")

    fld = tb.getcol("FIELD_ID")
    row_sel = (fld == field_id)

    if not np.any(row_sel):
        tb.close()
        raise RuntimeError("No rows match the requested selection (spw/field).")

    # CPARAM: (npol, nchan, nrow)
    cparam = tb.getcol("CPARAM")[:, :, row_sel]
    t_sel  = time[row_sel]
    a_sel  = ant[row_sel]

    flag = None
    if "FLAG" in cols:
        flag = tb.getcol("FLAG")[:, :, row_sel].astype(bool)

    tb.close()

    # ---- pick antenna ----
    ants = np.unique(a_sel)
    if ant_id is None:
        ant_id = int(ants[0])

    m_ant = (a_sel == ant_id)
    if not np.any(m_ant):
        raise RuntimeError(f"Antenna {ant_id} not present in selected rows.")

    # ---- get frequencies ----
    msmd.open(ms_path)
    nspw=len(msmd.spwsforfield(field_id))
    freq_GHz=[]
    for ispw in range(nspw):
        freq_GHz.append(msmd.chanfreqs(ispw))
    freq_GHz = np.array(freq_GHz) / 1e9  # Offset to centre channel
    msmd.close()
    
    # ---- choose pols ----
    npol = cparam.shape[0]
    if pol_map is None:
        # Common case: npol==2 for parallel hands
        pol_map = {"LL": 0, "RR": 1} if npol >= 2 else {"P0": 0}

    # ---- prep figure ----
    fig, (ax_amp, ax_phase) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    colours = ['k', 'm']
    labels = ["LL", "RR"]
    for j in range(2):
        gains = cparam[j, :, m_ant]  # (nchan, ntime_rows_for_ant)
        if flag is not None:
            gains = np.where(flag[0, :, m_ant], np.nan + 1j*np.nan, gains)
        c = colours[j]
        for i in range(32):
            g = gains[i, :]
            f = freq_GHz[i, :]

            amp = np.abs(g)
            phase = np.angle(g, deg=True)
            phase = (phase + 180) % 360 - 180
            ax_amp.scatter(f, amp, c=c, s=6)
            ax_phase.scatter(f, phase, c=c, s=6)
            l = labels[j] if i == 0 else None
            ax_amp.plot(f, amp, c=c, linewidth=1, label=l)
            ax_phase.plot(f, phase, c=c, linewidth=1, label=l)

        for i in range(32):
            offset = 0.02  # Better alignment with points?
            f0 = freq_GHz[i, :].min() + offset
            f1 = freq_GHz[i, :].max() + offset
            if i % 2 == 0:
                ax_amp.axvspan(f0, f1, alpha=0.1, color="grey")
                ax_phase.axvspan(f0, f1, alpha=0.1, color="grey")

    ax_amp.set_ylabel("Amplitude")
    ax_phase.set_ylabel("Phase (deg)")
    ax_phase.set_xlabel("Frequency (GHz)")

    ax_amp.grid(alpha=0.5)
    ax_phase.grid(alpha=0.5)

    ax_phase.legend(loc='best')

    plt.tight_layout()
    plt.savefig(savepath, dpi=300, bbox_inches="tight")

plot_bandpass_amp_phase_vs_freq(
    bp_table="25A-157.sb47896587.eb48188930.60749.83678572917.ms.hifv_finalcals.s13_4.finalBPcal.tbl",
    ms_path="../../tmp/scal.ms",
    spw_id=0,
    ant_id=9,
    field_id=0,          # optional
    pol_map={"LL": 0, "RR": 1},
    avg_over_time=True,
    savepath="bandpass_vs_freq.pdf",
)
