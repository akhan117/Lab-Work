from time import time
from tkinter.filedialog import askopenfilename
import pickle
import h5py
import plotter
import os
import matplotlib.pyplot as plt
from scipy import signal, ndimage
import numpy as np
import filters

# Spring 2022
# Written by Ian Lee


def default_save(path, to_save, to_save_label):
    print(f"Do you want to save as the default {to_save_label}? (y/n)")
    default = input()

    if default == 'y':
        with open(path, 'wb') as f:
            pickle.dump(to_save, f)
        print("saved")


def get_plot_type():
    plot_types = ["LFP", "Spectrogram", "Both"]
    path = "Default Values/Plot Type.pk"
    if os.path.exists(path):
        with open(path, 'rb') as f:
            plot_type = pickle.load(f)
        print(f"Default: Plotting {plot_types[int(plot_type)-1]}")
    else:
        print("\nChoose Plot (enter number):")
        print("1) LFP")
        print("2) Spectrogram")
        print("3) Both\n")
        revise = True
        while revise:

            plot_type = input()

            try:
                plot_type = int(plot_type)
                assert 1 <= plot_type <= 3
                revise = False
            except (AssertionError, ValueError):
                print("Invalid. Try again.")

        to_save = plot_type
        to_save_label = "plot type"
        default_save(path, to_save, to_save_label)
    return plot_type


def get_channels():
    path = "Default Values/Default Plotting Channels.pk"
    if os.path.exists(path):

        with open(path, 'rb') as f:
            channel_list = pickle.load(f)

        print(f"\nDefault channel(s): {', '.join(channel_list)}")

    else:
        print("\nSelect channels to plot, separated by a comma. (e.g. - U1, U2, U3)")
        channel_names = input()
        channel_list = [s.strip() for s in channel_names.split(",")]

        to_save = channel_list
        to_save_label = "channels"
        default_save(path, to_save, to_save_label)
    return channel_list


def get_freqs():
    path = "Default Values/Default Frequency.pk"
    if os.path.exists(path):

        with open(path, 'rb') as f:
            freq_min, freq_max = pickle.load(f)

        print(f"\nDefault frequencies: {freq_min}, {freq_max}")
    else:
        print("Select frequency range (hz) to plot, separated by a comma. (e.g: 1, 10)")
        try:
            frequencies = input()
            freq_min, freq_max = [int(s.strip())
                                  for s in frequencies.split(",")]
            freq_min = max(0, freq_min)
            assert freq_max > freq_min

            to_save = (freq_min, freq_max)
            to_save_label = "frequencies"
            default_save(path, to_save, to_save_label)
        except (AssertionError, ValueError):
            print("Defaulting to 1 to 120 hz")
            freq_min, freq_max = 1, 120
    return freq_min, freq_max


def get_time_range():
    path = "Default Values/Default Time Range.pk"
    if os.path.exists(path):

        with open(path, 'rb') as f:
            time_min, time_max = pickle.load(f)

        print(f"\nDefault time range: {time_min}, {time_max}")
    else:
        print("\nSelect time range (sec) to plot, separated by a comma. (e.g: 0, 100)")
        try:
            times = input()
            time_min, time_max = [int(s.strip()) for s in times.split(",")]
            time_min = max(0, time_min)
            assert time_max > time_min

            to_save = (time_min, time_max)
            to_save_label = "time range"
            default_save(path, to_save, to_save_label)
        except (AssertionError, ValueError):
            print("Defaulting to full range")
            time_min, time_max = -1, -1
    return time_min, time_max


def select_file():
    print("Select HDF5 file to plot:")
    selected_file = askopenfilename()
    return selected_file


def get_sampling_rates(selected_file):
    with h5py.File(selected_file, "r") as f:

        rates = f.get("Rates")
        rates = list(map(bytes.decode, rates))

        rates_map = dict()

        for i in range(0, len(rates), 2):
            rates_map[rates[i]] = float(rates[i+1])
    return rates_map


def get_events(selected_file):
    with h5py.File(selected_file, "r") as f:

        events = f.get("Events")
        events = list(map(bytes.decode, events))

        events_tuple = []

        for i in range(0, len(events), 3):
            events_tuple.append(
                (events[i], float(events[i+1]), float(events[i+2])))
    return events_tuple


def plot_LFP(selected_file, channel_list, time_min, time_max, rates_map, events_tuple, smoothing=5):
    print("Plotting LFP")

    remaining_channels = channel_list.copy()

    # extract channel data
    with h5py.File(selected_file, "r") as f:

        for channel in channel_list:
            if channel in f:

                remaining_channels.remove(channel)

                local_data = f.get(channel)[:]
                local_sampling_rate = rates_map[channel]
                local_data = ndimage.gaussian_filter(
                    local_data, sigma=local_sampling_rate/smoothing, mode="nearest", truncate=4)  # blur to remove high frequency noise

                plotter.plot_LFP(
                    local_data, local_sampling_rate, events_tuple, time_min, time_max, channel)

    if len(remaining_channels) > 0:
        print(
            f"The following channels were not found: {', '.join(remaining_channels)}")


def spectrogram(selected_file, channel_list, freq_min, freq_max, time_min, time_max, rates_map, events_tuple):
    print("Plotting Spectrogram")

    remaining_channels = channel_list.copy()

    # extract channel data
    with h5py.File(selected_file, "r") as f:

        for channel in channel_list:
            if channel in f:

                remaining_channels.remove(channel)

                local_data = f.get(channel)[:]
                local_sampling_rate = rates_map[channel]
                # local_data = filters.iir_notch(local_data, local_sampling_rate)

                nfft = 2 ** int(np.log2(local_sampling_rate)+2)
                noverlap = nfft/2

                plotter.plot_spectrogram(
                    local_data, local_sampling_rate, events_tuple, channel, time_min, time_max, freq_min, freq_max, nfft=nfft, noverlap=noverlap, log_scale=False)

    if len(remaining_channels) > 0:
        print(
            f"The following channels were not found: {', '.join(remaining_channels)}")


def make_plot():
    plot_type = get_plot_type()
    selected_file = select_file()

    channel_list = get_channels()
    time_min, time_max = get_time_range()
    if plot_type == 2 or plot_type == 3:
        freq_min, freq_max = get_freqs()
    events_tuple = get_events(selected_file)
    rates_map = get_sampling_rates(selected_file)

    if plot_type == 1:
        plot_LFP(selected_file, channel_list, time_min,
                 time_max, rates_map, events_tuple)
    elif plot_type == 2:
        spectrogram(selected_file, channel_list, freq_min,
                    freq_max, time_min, time_max, rates_map, events_tuple)
    elif plot_type == 3:
        plot_LFP(selected_file, channel_list, time_min,
                 time_max, rates_map, events_tuple)
        spectrogram(selected_file, channel_list, freq_min,
                    freq_max, time_min, time_max, rates_map, events_tuple)
    print("Finished")


if __name__ == "__main__":

    make_plot()
