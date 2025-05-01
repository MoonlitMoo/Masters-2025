import sys

import matplotlib.pyplot as plt
import numpy as np
from casatools import ms, msmetadata

msfile = sys.argv[1] if len(sys.argv) > 1 else ValueError("Missing msfile argument")
field_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
spw_index = int(sys.argv[3]) if len(sys.argv) > 3 else 0
plot_dir = int(sys.argv[4]) if len(sys.argv) > 3 else "."

def select_lowest_variance_channels(msfile: str, field: int | str, spw: int | str, plot_dir: str,
                                    top_percent: float=0.001, trim_channels: int=5, debug_plot: bool=False):
    """
    Extracts visibility data for a given field and spectral window,
    computes statistics, and returns the indices of the three sequential
    channels with the lowest variance.

    Parameters
    ----------
    msfile : str
        Path to the Measurement Set.
    field : int or str
        Field index or name.
    spw : int or str
        Spectral window index or range.
    plot_dir : str
        Folder to output the check plots
    top_percent : float, default=0.001
        The percentage to use to calculate the variance, given as a decimal.
    trim_channels : int, default=5
        The number of channels to ignore at the edges, while finding the sequential min-var channels
    debug_plot : bool, default=False


    Returns
    -------
    tuple
        Indices of the three sequential channels with the lowest variance (indices are lowest to highest).

    """

    # Open the Measurement Set Metadata
    msmd_tool = msmetadata()
    msmd_tool.open(msfile)

    # Get the actual field ID if a name is provided
    if isinstance(field, str):
        field_id = msmd_tool.fieldsforname(field)[0]
    else:
        field_id = field

    # Get the number of channels for the given spectral window
    num_channels = msmd_tool.nchan(spw)

    msmd_tool.close()

    # Open the MS tool and select the data
    ms_tool = ms()
    ms_tool.open(msfile)
    ms_tool.selectinit(datadescid=int(spw))
    ms_tool.select({'field_id': field_id})
    ms_tool.selectpolarization(["LL", "RR"])

    # Get the data (complex values, take amplitude)
    raw = ms_tool.getdata(['data', 'flag'])  # Shape: (polarization, channels, time)
    data = raw['data']
    flags = raw['flag']
    ms_tool.close()

    # Remove flagged data by setting to nan
    data[flags] = np.nan + 1j*np.nan

    # if data.shape[0] < 4:
    #     raise ValueError("Not enough polarizations in data; expected at least 4.")

    # Convert complex values to amplitude
    data_amp = np.abs(data)

    # Reshape to only channels
    data_amp = np.moveaxis(data_amp, 1, 0)  # Move channel axis to first dimension
    data_reshaped = data_amp.reshape(num_channels, -1)

    # Compute the average of the top .1% of values per channel
    num_top_values = [max(1, int(top_percent * len(d[~np.isnan(d)]))) for d in data_reshaped]  # Ensure at least 1 value
    # Compute the variance per channel, filtering nan as we go
    channel_variances = [np.nanvar(np.partition(d[~np.isnan(d)], -n)[-n:]) for d, n in zip(data_reshaped, num_top_values)]
    channel_variances = np.nan_to_num(channel_variances, nan=np.inf)

    # Plot debug graphs
    if debug_plot:
        plot_selected_points(data_reshaped, num_top_values)
        plot_channel_distribution(data_reshaped)
        plot_variances(channel_variances)

    # Find the three sequential channels with the lowest combined variance, ignoring trim channels
    n_channels_select = 3
    min_var_idx = np.argmin([
        np.sum(channel_variances[i:i+n_channels_select]) for i in range(trim_channels, len(channel_variances) - n_channels_select - trim_channels + 1)
    ])
    min_var_idx += trim_channels  # Correct for the trim channels

    plot_selected_points(data_reshaped, num_top_values, min_var_idx, f"{field}_{spw}", plot_dir)
    plt.close()
    return min_var_idx, min_var_idx + 1, min_var_idx + 2

def plot_selected_points(data, len_top_vals, first_selected_col, title, output_dir):
    plt.figure(figsize=(10, 6))
    for i, d in enumerate(data):
        # Remove NaNs first
        clean_d = d[~np.isnan(d)]
        num_top_values = len_top_vals[i]
        if len(clean_d) <= num_top_values:
            continue  # Skip if not enough values to partition

        # Use np.partition once and directly slice
        partitioned = np.partition(clean_d, [-num_top_values, len(clean_d) - num_top_values])

        bottom, top = partitioned[:-num_top_values], partitioned[-num_top_values:]

        # Use NumPy for efficient indexing and avoid redundant list comprehensions
        x_vals_bottom = np.full(len(bottom), i)
        x_vals_top = np.full(len(top), i)

        plt.scatter(x_vals_bottom, bottom, c='b', s=5)  # Smaller marker size
        # Colour selected column for double-checking
        c = 'g' if i in [j for j in range(first_selected_col, first_selected_col + 3)] else 'r'
        plt.scatter(x_vals_top, top, c=c, s=5)
    plt.grid()
    plt.xlabel("Channel")
    plt.ylabel("Amplitude")
    plt.title(f"Field_SPW: {title}")
    plt.savefig(f"{output_dir}/lowest_variance_{title}.png", dpi=300)


def plot_channel_distribution(data_arrays):
    """
    Plots a violin plot for multiple data arrays.

    Parameters:
    data_arrays (list of np.ndarray): List of 1D NumPy arrays.
    """
    # Create x-axis labels based on array index
    x_labels = np.arange(len(data_arrays))

    # Create the violin plot
    plt.figure(figsize=(10, 6))
    plt.violinplot([d[~np.isnan(d)] for d in data_arrays], positions=x_labels, showmeans=True, showmedians=True)

    # Label the axes
    plt.xlabel("Channel")
    plt.ylabel("Amplitude")
    plt.title("Violin Plot of Multiple Data Arrays")

    # Show the plot
    plt.grid(True)
    plt.savefig("../channeldist.png", dpi=300)


def plot_variances(variance):
    plt.figure()
    plt.plot([i for i, _ in enumerate(variance)], variance)
    plt.xlabel("Channel")
    plt.ylabel("Variance")
    plt.grid()
    plt.savefig("../variance.png", dpi=300)

def get_initial_cal_spw_string(msname: str, field: int, spw: list, plot_dir, trim_channels):
    select_strings = []
    for i in spw:
        result = select_lowest_variance_channels(msname, field, i, plot_dir, trim_channels=trim_channels)
        select_strings.append(f"{i}:{result[0]}~{result[-1]}")
    return ",".join(select_strings)


if __name__ == "__main__":
    msname = "24A-411.sb45152540.eb45209965.60336.070794328705.ms"
    print(get_initial_cal_spw_string(msname, 0, [i for i in range(16, 48)], "plots"))
