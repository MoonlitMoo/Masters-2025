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

def save_reference_flags(base_flag_file='base_flag_file'):
    # Save current flags to file
    base_stats = get_flagging_summary()
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
        save_reference_flags(base_flag_file)

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
    base_field_flags = {field_id: base_stats[f'field_{field_id}']['total'] for field_id in base_fields}
    cur_field_flags = {field_id: current_stats[f'field_{field_id}']['total'] for field_id in base_fields}

    plot_comparison(base_field_flags,
                    cur_field_flags,
                    'Flagging by Field', 'Field', '% Flagged',
                    'all_fields_flagging.png')

    print(f"Flagging comparisons saved to {output_dir}/")

