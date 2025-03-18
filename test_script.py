import sys

import matplotlib.pyplot as plt
import numpy as np
from casatools import ms, msmetadata

msfile = sys.argv[1] if len(sys.argv) > 1 else ValueError("Missing msfile argument")
field_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
spw_index = int(sys.argv[3]) if len(sys.argv) > 3 else 0

def select_lowest_variance_channels(msfile: str, field: int | str, spw: int):
    """
    Extracts visibility data for a given field and spectral window,
    computes statistics, and returns the indices of the three sequential
    channels with the lowest variance.

    Parameters:
    msfile (str): Path to the Measurement Set.
    field (int or str): Field index or name.
    spw (int or str): Spectral window index or range.

    Returns:
    tuple: Indices of the three sequential channels with the lowest variance.
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

    # Get the data (complex values, take amplitude)
    raw = ms_tool.getdata(['data', 'flag'])  # Shape: (polarization, channels, time)
    data = raw['data']
    flags = raw['flag']
    ms_tool.close()

    # Remove flagged data by setting to nan
    data[flags] = np.nan + 1j*np.nan

    if data.shape[0] < 4:
        raise ValueError("Not enough polarizations in data; expected at least 4.")

    # Convert complex values to amplitude
    data_amp = np.abs(data)

    # Reshape to only channels
    data_amp = np.moveaxis(data_amp, 1, 0)
    data_reshaped = data_amp.reshape(num_channels, -1)

    # Compute the average of the top .1% of values per channel
    num_top_values = max(1, int(0.001 * data_reshaped.shape[1]))  # Ensure at least 1 value
    # Compute the variance per channel, filtering nan as we go
    channel_variances = [np.nanvar(np.partition(d[~np.isnan(d)], -num_top_values)[-num_top_values:]) for d in data_reshaped]
    channel_variances = np.nan_to_num(channel_variances, nan=np.inf)

    # Plot debug graphs
    # plot_selected_points(data_reshaped, num_top_values)
    # plot_channel_distribution(data_reshaped)
    # plot_variances(channel_variances)

    # Find the three sequential channels with the lowest combined variance, ignoring trim channels
    trim_channels = 5
    min_var_idx = np.argmin([
        np.sum(channel_variances[i:i+3]) for i in range(trim_channels, len(channel_variances) - 2 - trim_channels)
    ])
    min_var_idx += trim_channels  # Correct for the trim channels
    return min_var_idx, min_var_idx + 1, min_var_idx + 2

def plot_selected_points(data, num_top_values):
    plt.figure(figsize=(10, 6))
    for i, d in enumerate(data):
        # Remove NaNs first
        clean_d = d[~np.isnan(d)]

        if len(clean_d) <= num_top_values:
            continue  # Skip if not enough values to partition

        # Use np.partition once and directly slice
        partitioned = np.partition(clean_d, [-num_top_values, len(clean_d) - num_top_values])

        bottom, top = partitioned[:-num_top_values], partitioned[-num_top_values:]

        # Use NumPy for efficient indexing and avoid redundant list comprehensions
        x_vals_bottom = np.full(len(bottom), i)
        x_vals_top = np.full(len(top), i)

        plt.scatter(x_vals_bottom, bottom, c='b', s=5)  # Smaller marker size
        plt.scatter(x_vals_top, top, c='r', s=5)

    plt.savefig('../selected_points.png', dpi=300)


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

if __name__ == "__main__":
    msname = "24A-411.sb45152540.eb45209965.60336.070794328705.ms"
    # result = select_lowest_variance_channels(msname, 1, 20)
    # print(result)
    select_strings = []
    for i in range(16, 48):
        result = select_lowest_variance_channels(msname, 1, i)
        select_strings.append(f"{i}:{result[0]}~{result[-1]}")
    final_string = ",".join(select_strings)
    print(final_string)