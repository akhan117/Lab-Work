from time import time
from click import group
import numpy as np
from neo import Spike2IO  # neo v.0.6.1
import h5py
import ntpath
import platform
import pickle
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from os.path import exists
import os
import scipy
from visualization import filters
import matplotlib.pyplot as plt


# def frequency_odor_significance(arr, i_start, i_range, i_step, sample_size, sample_distance, fmin=1, fmax=12):
#     """
#     t-tests on two intervals of sample frequency from [fmin] to [fmax]. Perform test every [t_step] within [t_range]
#     """
#     #     # sampling freq
#     #     # respiratory signal (u_data)
#     #     # label of odors and timestamps (event)
#     #     # time array
#     #     # Respirat

#     #     # Welch T test
#     #     # 1 - 10 hz frequency
#     #     print("Extracting Respiratory Odor Onset")
#     #     scipy.stats.ttest_ind(equal_var=False)

#     freq_p = []
#     return freq_p


def magnitude_odor_significance(abs_d_arr, i_start, i_range, i_step, sample_size, sample_distance):
    """
    t-tests on two intervals of sample magnitude from [fmin] to [fmax]. Perform test every [t_step] within [t_range]

    Test for volatility using first order discrete derivative
    """
    mag_p = []
    for t in range(i_start, i_start+i_range+1, i_step):
        try:
            group1 = abs_d_arr[t:t+sample_size]
            group2 = abs_d_arr[t-sample_distance-sample_size:t-sample_distance]
            _, p = scipy.stats.ttest_ind(
                group1, group2, equal_var=False, alternative="greater")
            mag_p.append(p)
        except IndexError:
            continue
    return mag_p


def onset_timestamp(ps, time_step, t):
    plt.plot(ps)
    plt.show()
    return np.argmin(ps, axis=0) * time_step + t


def odor_onset(respirat_arr, events, fs, fmin=1, fmax=10):
    """
    return ordor onset timestamps
    """
    time_step = 0.1  # sample every 100 ms
    time_step_i = int(time_step * fs)
    time_frame = 10  # sample first 10000 ms of odor presentation
    time_frame_i = int(time_frame * fs)
    sample_interval = 1.5  # sample in groups of 1500 ms data
    sample_interval_i = int(sample_interval * fs)
    group_distances = 1  # t test groups time distance
    group_distances_i = int(group_distances * fs)

    respirat_arr = filters.cheby2_bp_filter(
        respirat_arr, fs, fmin, fmax)  # filter band pass
    respirat_arr = scipy.ndimage.gaussian_filter(
        respirat_arr, sigma=fs/5, mode="nearest", truncate=4)  # blur to remove high frequency noise
    derivative_arr = (np.roll(respirat_arr, -1) - respirat_arr) * fs
    abs_derivative_arr = np.abs(derivative_arr)

    events_f = []
    for i in range(0, len(events), 2):
        label, t = events[i], events[i+1]  # string, float
        time_i = int(float(t) * fs)

        if label.upper() == "BLANK":
            continue

        # freq_p = frequency_odor_significance(
        #     respirat_arr, time_i, time_frame_i, time_step_1, sample_interval_i, group_distances_i)
        mag_p = magnitude_odor_significance(
            abs_derivative_arr, time_i, time_frame_i, time_step_i, sample_interval_i, group_distances_i)
        mag_p = scipy.ndimage.gaussian_filter(
            mag_p, sigma=2, mode="constant", cval=1)
        cross_p = mag_p

        local_onset_t = onset_timestamp(cross_p, time_step, t)

        events_f.append(label)
        events_f.append(str(t))
        events_f.append(str(local_onset_t))

    return events_f

#   save plot compatible epoch hdf files


def spyke_to_numpy(file_name):
    print("Working on " + file_name + "......")
    # Typical Set up for Neo to access the file, and we only have one block and one segment
    spike2_reader = Spike2IO(file_name)
    blocks = spike2_reader.read()
    block = blocks[0]
    segments = block.segments
    segment = segments[0]
    channels_data = {}
    name_rate = np.array([])

    # Go through all the channels, and add the data from each to the dictionary
    for sig in segment.analogsignals:
        channel_data = np.squeeze(sig)
        channel_name = sig.annotations['channel_names'][0]
        channels_data[channel_name] = channel_data

        # Saving the channel names and sampling rate
        name_rate = np.append(
            name_rate,
            (sig.annotations['channel_names'][0], str(sig.sampling_rate)))

    return channels_data, segment.events[0], name_rate


if __name__ == "__main__":

    if exists("Default Values/Default Number of Files.pk"):
        print()
        print(
            "Using the default number of files from the file Default Number of Files.pk! Delete this file if you do"
            + " not want to use the default number of files anymore!")

        with open("Default Values/Default Number of Files.pk", 'rb') as fi:
            x = pickle.load(fi)

        print("Default number of files is " + x)

    else:
        print(
            "#######################################################################################################"
        )
        print("How many files do you want to work with?")
        print(
            "#######################################################################################################"
        )
        x = input()
        print()

        print("Do you want save this as the default number of files (y/n)")
        default = input()

        if default == 'y':
            with open("Default Values/Default Number of Files.pk", 'wb') as fi:
                pickle.dump(x, fi)

        elif default == 'n':
            print()

        else:
            print("Defaulting to n.")
    print()
    file_list = []

    for i in range(0, int(x)):
        print("There are still " + str(int(x) - i) + " file(s) to choose")
        val = askopenfilename()
        file_list.append(val)

    if exists("Default Values/Default Save to Location.pk"):
        print()
        print(
            "Using the Default save to location from the file Default Save to Location.pk! Delete this file if you do"
            + " not want to use the default save to location anymore!")

        with open("Default Values/Default Save to Location.pk", 'rb') as fi:
            save_to = pickle.load(fi)

        print("Saving to " + save_to)

    else:
        print(
            "#######################################################################################################"
        )
        print("Where do you want to save the files to")
        print(
            "#######################################################################################################"
        )
        save_to = askdirectory()

        print("Do you want save this as the default location to save to (y/n)")
        default = input()

        if default == 'y':
            with open("Default Values/Default Save to Location.pk",
                      'wb') as fi:
                pickle.dump(save_to, fi)

        elif default == 'n':
            print()

        else:
            print("Defaulting to n.")

    print()

    u_data = {}
    events = []
    split = []
    # Create Dictionary of combined data from all our files
    for file in file_list:
        split_s = 0
        file_index = file_list.index(file)
        u_data1, events1, name_and_rate = spyke_to_numpy(file)
        events.append(events1)
        for i in list(u_data1):
            if len(file_list[file_index:]) != 1:
                if len(u_data1[i]) > split_s:
                    split_s = len(u_data1[i])

            if i not in u_data:
                u_data[i] = np.array([])
            u_data[i] = np.concatenate((u_data[i], u_data1[i]))

        split.append(split_s)

    # Save the channel names and sampling rates
    with open("Channels.txt", 'w') as f:
        for ele in name_and_rate:
            f.write(str(ele) + '\n')

    # clean events (label, timing) to string and float
    events_str = []
    to_add = 0
    for event in events:

        for event1 in range(0, len(event.times)):

            timing = float(event.times[event1]) + to_add
            events_str.append(str(event.labels[event1])[2:-1])
            events_str.append(timing)
            if event1 is len(events1.times) - 1:
                to_add += float(events1.times[event1])

    # Odor onset events
    print("Extracting Respiratory Odor Onset")
    k = "Respirat"
    res_i = np.where(name_and_rate == k)[0][0]
    fs = float(name_and_rate[res_i+1][:-3])
    respirat_arr = u_data[k]
    events_f = odor_onset(respirat_arr, events_str, fs)

    events_f_b = []
    # Organize the events by time and save them
    with open("Events.txt", 'w') as f:

        for event_i in range(0, len(events_f), 3):

            events_f_b.append(np.string_(events_f[event_i]))
            events_f_b.append(np.string_(events_f[event_i+1]))
            events_f_b.append(np.string_(events_f[event_i+2]))
            f.write(
                events_f[event_i] + ", " + events_f[event_i+1] +
                ", " + events_f[event_i+2] +
                '\n')

    # Organize name and rates of channels
    name_and_rates_dict = dict()
    for i in range(0, len(name_and_rate), 2):
        name_and_rates_dict[name_and_rate[i]] = float(name_and_rate[i+1][:-3])
    name_and_rates = []

    for n in name_and_rates_dict:
        name_and_rates.append(np.string_(str(n)))
        name_and_rates.append(np.string_(str(name_and_rates_dict[n])))

    # Obtain just the file names and remove the .smr extension from them
    file_list = [ntpath.basename(file) for file in file_list]
    for i in range(0, len(file_list)):
        if '.smr' in file_list[i]:
            file_list[i] = file_list[i][:-4]

    # Create the name of the final file
    full_name = file_list[0]
    for i in range(1, len(file_list)):
        full_name = full_name + " and " + file_list[i]

    # For Windows -> If the folder to save_to ends with \, then simply add .hdf5 to the end of the name and save it,
    # otherwise the backslash has to be added to have a legitimate directory
    if platform.system() == "Windows":
        if save_to[:-1] == '\\':
            save_to = save_to + full_name + ".hdf5"
        else:
            save_to = save_to + '\\' + full_name + ".hdf5"

    # For OSX and Linux -> The directory would likely include a forward slash instead
    else:
        if save_to[:-1] == '/':
            save_to = save_to + full_name + ".hdf5"
        else:
            save_to = save_to + '/' + full_name + ".hdf5"

    with open("Save to.pk", 'wb') as fi:
        pickle.dump(save_to, fi)

    with open("Events.txt", 'r') as f:
        events_and_time = f.readlines()

    events_and_time = [x[:-1] for x in events_and_time]
    events_and_time = [x.split(',') for x in events_and_time]

    event_list = []
    time_list = []
    odor_onset_list = []

    for i in events_and_time:
        [x, y, z] = i
        event_list.append(x)
        time_list.append(float(y))
        odor_onset_list.append(float(z))

    os.chdir("..")
    events = os.path.abspath(os.curdir)

    if platform.system() == "Windows":
        times = events + "\\Spike Processing\\Event and Sampling Rates Data\\" + \
            full_name + " times.pk"
        rates = events + "\\Spike Processing\\Event and Sampling Rates Data\\" + \
            full_name + " rates.pk"
        splits = events + "\\Spike Processing\\Event and Sampling Rates Data\\" + \
            full_name + " splits.pk"
        odor_onsets = events + "\\Spike Processing\\Event and Sampling Rates Data\\" + \
            full_name + " odor_onsets.pk"
        events = events + "\\Spike Processing\\Event and Sampling Rates Data\\" + \
            full_name + " events.pk"

    else:
        times = events + "/Spike Processing/Event and Sampling Rates Data/" + \
            full_name + " times.pk"
        rates = events + "/Spike Processing/Event and Sampling Rates Data/" + \
            full_name + " rates.pk"
        splits = events + "/Spike Processing/Event and Sampling Rates Data/" + \
            full_name + " splits.pk"
        odor_onsets = events + "/Spike Processing/Event and Sampling Rates Data/" + \
            full_name + " odor_onsets.pk"
        events = events + "/Spike Processing/Event and Sampling Rates Data/" + \
            full_name + " events.pk"

    with open(events, "wb") as fi:
        pickle.dump(event_list, fi)

    with open(times, "wb") as fi:
        pickle.dump(time_list, fi)

    with open(rates, "wb") as fi:
        pickle.dump(name_and_rate, fi)

    with open(splits, "wb") as fi:
        pickle.dump(split, fi)

    with open(odor_onsets, "wb") as fi:
        pickle.dump(odor_onset_list, fi)

    print()
    print(
        "Would you like to enter miscellaneous data such as the rat ID, dates etc? (y/n)"
    )

    inp = input()
    if inp == "y":
        print("Press Enter for irrelevant/unknown fields.")

        print("Enter the rats ID-")
        rat_name = input()

        print("Enter the name of the Experiment-")
        Experiment_name = input()

        print("Enter the Experimental Group-")
        Experimental_group = input()

        print("Enter the date of the experiment-")
        date = input()

        print("Enter the name of the person who did the experiment-")
        name = input()

    print("Working on compressing and saving the data.....")
    # Save to our file
    with h5py.File(save_to, 'w') as f:
        for i in list(u_data):
            f.create_dataset(i,
                             len(u_data[i]),
                             data=u_data[i],
                             compression="gzip")
            print(i + " was saved to the HDF5 File.")

        f.create_dataset("Events",
                         len(events_f_b),
                         data=events_f_b,
                         compression="gzip")
        print("Event (label, start time, odor onset) saved to the HDF5 File.")

        f.create_dataset("Rates",
                         len(name_and_rates),
                         data=name_and_rates,
                         compression="gzip"
                         )
        print("Channel Rates saved to the HDF5 File.")

        try:
            rat_name
        except NameError:
            pass
        else:
            f.create_dataset("RatID", 1, data=rat_name, compression="gzip")

        try:
            Experiment_name
        except NameError:
            pass
        else:
            f.create_dataset("ExperimentName",
                             1,
                             data=Experiment_name,
                             compression="gzip")

        try:
            Experimental_group
        except NameError:
            pass
        else:
            f.create_dataset("ExperimentalGroup",
                             1,
                             data=Experimental_group,
                             compression="gzip")

        try:
            name
        except NameError:
            pass
        else:
            f.create_dataset("Name", 1, data=name, compression="gzip")

        try:
            date
        except NameError:
            pass
        else:
            f.create_dataset("Date", 1, data=date, compression="gzip")

    print("Finished")
