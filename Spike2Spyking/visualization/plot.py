from time import time
from tkinter.filedialog import askopenfilename
import pickle
import h5py
import spectrogram
import os
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import filters

# Spring 2022
# Written by Ian Lee

if __name__ == "__main__":
    print("\nPlot Spectrogram\n")
    print("Select file to plot:")
    selected_file = askopenfilename()

    if os.path.exists("Default Values/Default Plotting Channels.pk"):
        print("\n")
        print("Using the default channels")

        with open("Default Values/Default Plotting Channels.pk", 'rb') as f:
            channel_list = pickle.load(f)

        print("\n")
        print(f"Default channel(s): {', '.join(channel_list)}")

    else:
        print("\n")
        print("Select channels to plot, separated by a comma. (e.g. - U1, U2, U3)")
        channel_names = input()
        channel_list = [s.strip() for s in channel_names.split(",")]

        print(
            "Do you want to save these channels as the default channels to extract? (y/n)")
        default = input()

        if default == 'y':
            with open("Default Values/Default Plotting Channels.pk", 'wb') as f:
                pickle.dump(channel_list, f)

        elif default == 'n':
            print()

        else:
            print("Defaulting to n.")

    remaining_channels = channel_list.copy()

    print("\n")
    print("Select time range (s) to plot, separated by a comma. (e.g: 0, 100)")
    try:
        times = input()
        time_min, time_max = [int(s.strip()) for s in times.split(",")]
        time_min = max(0, time_min)
        assert time_max > time_min
    except (AssertionError, ValueError):
        print("Defaulting to full range")
        time_min, time_max = -1, -1

    print("\n")
    print("Select frequency range (hz) to plot, separated by a comma. (e.g: 1, 10)")
    try:
        frequencies = input()
        freq_min, freq_max = [int(s.strip()) for s in frequencies.split(",")]
        freq_min = max(0, freq_min)
        assert freq_max > freq_min
    except (AssertionError, ValueError):
        print("Defaulting to 1 to 120 hz")
        freq_min, freq_max = 1, 120
    print("\n")

    # extract channel data
    with h5py.File(selected_file, "r") as f:

        rates = f.get("Rates")
        rates = list(map(bytes.decode, rates))

        rates_map = dict()

        for i in range(0, len(rates), 2):
            rates_map[rates[i]] = float(rates[i+1])

        for channel in channel_list:

            if channel in f:

                remaining_channels.remove(channel)

                local_data = f.get(channel)[:]
                local_sampling_rate = rates_map[channel]
                # local_data = filters.iir_notch(local_data, local_sampling_rate)

                nfft = 2 ** int(np.log2(local_sampling_rate))
                noverlap = nfft/2

                print(f"Plotting {channel}")

                spectrogram.plot_spectrogram(
                    local_data, local_sampling_rate, time_min, time_max, freq_min, freq_max, channel, nfft=nfft, noverlap=noverlap)

    if len(remaining_channels) > 0:
        print("The following channels were not found: " +
              ", ".join(remaining_channels))
    print("Finished")
