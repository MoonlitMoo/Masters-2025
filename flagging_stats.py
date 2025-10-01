import os
import json
import matplotlib.pyplot as plt
import numpy as np
from casatasks import flagmanager, flagdata


def get_flagging_summary(msname):
    """
    Generate flagging summary statistics using flagdata for each field,
    including per-SPW, per-antenna, and total flags. Results are saved to a JSON file.
    """
    result = {}

    # Get the list of fields from listobs
    obs_info = listobs(vis=msname, listfile='', verbose=False)
    fields = [i for i in obs_info.keys() if 'field_' in i]
    field_names = [obs_info[i]['name'] for i in fields]

    for field in field_names:
        field_id = str(field).split()[0]

        summary = flagdata(vis=msname, mode='summary', field=field_id)

        # Store SPW, antenna, and total stats for this field
        field_summary = {
            'total': summary['field'][field_id],
            'spw': summary['spw'],
            'antenna': summary['antenna']
        }

        result[f'field_{field_id}'] = field_summary

    return result

def save_reference_flags(msname, base_flag_file='base_flag_file'):
    # Save current flags to file
    base_stats = get_flagging_summary(msname)
    with open(base_flag_file, 'w') as f:
        json.dump(base_stats, f, indent=2)


def check_flagging(msname, base_flag_file='base_flag.json', output_dir='plots'):
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Check if reference exists, create if not, else load
    if not os.path.exists(base_flag_file):
        print(f"Reference flag file '{base_flag_file}' not found. Creating it...")

        # Save current flag state
        flagmanager(vis=msname, mode='save', versionname='tmp')
        # 1.2 Restore base flagging (assumes it exists)
        flagmanager(vis=msname, mode='restore', versionname='base_flagging')

        # 1.3 Save current flags to file
        save_reference_flags(msname, base_flag_file)

        # 1.4 Restore temporary flags
        flagmanager(vis=msname, mode='restore', versionname='tmp')
        # 1.5 Delete temporary backup
        flagmanager(vis=msname, mode='delete', versionname='tmp')

    with open(base_flag_file, 'r') as f:
        base_stats = json.load(f)

    # Step 2: Get current stats
    current_stats = get_flagging_summary(msname)

    def plot_comparison(base, current, title, xlabel, ylabel, filename):
        ids = sorted(set(base.keys()) | set(current.keys()))
        try:
            ids = sorted(ids, key=lambda x: int(x))
        except:
            pass
        base_vals = [base[i]['flagged'] / base[i]['total'] * 100 for i in ids]
        curr_vals = [current[i]['flagged'] / current[i]['total'] * 100 for i in ids]
        w, x = .4, np.arange(len(ids))

        plt.figure(figsize=(10, 5))
        plt.bar(x - w/2, base_vals, w, label='Base')
        plt.bar(x + w/2, curr_vals, w, label='Current')
        plt.xticks(x, ids)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    # Step 3: Per-field comparisons
    base_fields = [k.split("_")[1] for k in base_stats.keys()]
    for field_id in sorted(base_fields):
        if f"field_{field_id}" not in current_stats:
            print(f"WARNING: ''{field_id}' not found in current dataset")
            continue
        plot_comparison(base_stats[f"field_{field_id}"]['spw'],
                        current_stats[f"field_{field_id}"]['spw'],
                        f'Field {field_id} - Flagging by SPW',
                        'SPW', '% Flagged',
                        f'field_{field_id}_spw_flagging.png')

        plot_comparison(base_stats[f"field_{field_id}"]['antenna'],
                        current_stats[f"field_{field_id}"]['antenna'],
                        f'Field {field_id} - Flagging by antenna',
                        'SPW', '% Flagged',
                        f'field_{field_id}_antenna_flagging.png')


    # Step 4: All-field comparison
    base_field_flags = {field_id: base_stats[f'field_{field_id}']['total'] for field_id in base_fields if f"field_{field_id}" in current_stats}
    cur_field_flags = {field_id: current_stats[f'field_{field_id}']['total'] for field_id in base_fields if f"field_{field_id}" in current_stats}

    plot_comparison(base_field_flags,
                    cur_field_flags,
                    'Flagging by Field', 'Field', '% Flagged',
                    'all_fields_flagging.png')

    print(f"Flagging comparisons saved to {output_dir}/")


def assess_spws(msname, *, edge_spws=(0, -1), statwt_mode="if_missing", statwt_kwargs=None,
                abs_floor=0.35, rel_drop_mult=0.55, rel_review_mult=0.70, low_weight_guard=0.50, print_output=True):
    """
    Prints per-SPW: f(unflag), wrel, feff, decision, reason(s).
    Returns dict with arrays.
    """
    # Get unflagged fraction per SPW
    fs = flagdata(vis=msname, mode="summary")
    sorted_fs = sorted([(int(i), s) for i, s in fs["spw"].items()], key=lambda x: x[0])
    unflagged = [s["total"] - s["flagged"] for _, s in sorted_fs]
    totals    = [s["total"] for _, s in sorted_fs]
    u = np.asarray(unflagged, float)
    t = np.asarray(totals, float)
    f = np.divide(u, t, out=np.zeros_like(u, dtype=float), where=t > 0)
    nspw = len(f)

    # --- Stand in for the failure to get the weights per spw.
    wrel = np.ones_like(f)

    # --- Effective fraction & thresholds
    feff = f * wrel
    med_feff = np.median(feff[feff > 0]) if np.any(feff > 0) else 0.0
    rel_drop   = rel_drop_mult   * med_feff
    rel_review = rel_review_mult * med_feff

    rel_drop_adj = np.full_like(feff, rel_drop, dtype=float)
    for j in [j if j >= 0 else nspw + j for j in edge_spws]:
        if 0 <= j < nspw:
            rel_drop_adj[j] = (rel_drop_mult - 0.05) * med_feff  # e.g., 0.50× if base is 0.55×

    # --- Decisions + appended reasons
    decision = np.array(["keep"] * nspw, dtype=object)
    reason   = [""] * nspw
    for i in range(nspw):
        reasons = []
        # Priority: weight guard → abs floor → relative drop → review band
        if wrel[i] <= low_weight_guard:
            decision[i] = "drop"
            reasons.append(f"low relative weight (wrel={wrel[i]:.2f} ≤ {low_weight_guard:.2f})")

        if f[i] < abs_floor:
            decision[i] = "drop"
            reasons.append(f"below absolute floor (f={f[i]:.2f} < {abs_floor:.2f})")

        if feff[i] < max(abs_floor, rel_drop_adj[i]):
            decision[i] = "drop"
            reasons.append(
                f"below relative drop (feff={feff[i]:.2f} < "
                f"{max(abs_floor, rel_drop_adj[i]):.2f}; median feff={med_feff:.2f})"
            )

        if (decision[i] != "drop") and (feff[i] < rel_review):
            decision[i] = "review"
            reasons.append(
                f"in review band ({rel_drop_mult:.2f}–{rel_review_mult:.2f}×median feff: "
                f"{rel_drop:.2f}–{rel_review:.2f})"
            )

        if not reasons:
            decision[i] = "keep"
            reasons.append("healthy fraction and weights")

        reason[i] = "; ".join(reasons)

    # --- Calculate how much unflagged data is being removed
    keep_mask = decision != "drop"
    lost_fraction  = 1 - (u[keep_mask].sum() / u.sum())

    # --- Print
    if print_output:
        header = (
            f"# assess_spws on {msname}\n"
            f"# abs_floor={abs_floor:.2f} | drop<{rel_drop_mult:.2f}×med | "
            f"review<{rel_review_mult:.2f}×med | low_weight_guard≤{low_weight_guard:.2f}\n"
            f"# median feff={med_feff:.3f}\n"
            f"# dropping {np.count_nonzero(~keep_mask)} SPWs loses {lost_fraction:.1%} of unflagged data\n"
            f"SPW  f(unflag)  wrel   feff   decision   reason(s)"
        )
        print(header)
        for i in range(nspw):
            print(f"{i:>3}  {f[i]:7.3f}  {wrel[i]:5.2f}  {feff[i]:6.3f}  "
                  f"{decision[i]:>6}   {reason[i]}")
    return {
        "frac": f,
        "wrel": wrel,
        "feff": feff,
        "lost_frac": lost_fraction,
        "decision": decision,
        "reason": reason,
    }
