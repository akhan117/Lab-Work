import numpy as np
import h5py
from quantities import uV, Hz, ms, s
import os
import platform
from os.path import exists
import ntpath
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import pickle

print("###############################################################################################################")
print("Select the result-merged.hdf5 file from Spyking-Circus")
print("###############################################################################################################")
print()
val = askopenfilename()

if exists("Default Values/Default Save to Location.pk"):
    print()
    print("Using the Default save to location from the file Default Save to Location.pk! Delete this file if you do"
          + " not want to use the default save to location anymore!")

    with open("Default Values/Default Save to Location.pk", 'rb') as fi:
        sal = pickle.load(fi)

    print("Saving to " + sal)

else:
    print("#######################################################################################################")
    print("Where do you want to save the files to")
    print("#######################################################################################################")
    sal = askdirectory()

    print("Do you want save this as the default location to save to (y/n)")
    default = input()

    if default == 'y':
        with open("Default Values/Default Save to Location.pk", 'wb') as fi:
            pickle.dump(sal, fi)

    elif default == 'n':
        print()

    else:
        print("Defaulting to n.")

print()

if exists("Default Values/Default Sampling Rate.pk"):
    print()
    print("Using the Default Sampling from the file Default Sampling Rate.pk! Delete this file if you do not want to "
          + "use the default value anymore!")

    with open("Default Values/Default Sampling Rate.pk", 'rb') as fi:
        Sampling_rate = pickle.load(fi)

    print("The default sampling rate is " + str(Sampling_rate))
else:

    print("#######################################################################################################")
    print("Enter the Sampling Rate.")
    print("#######################################################################################################")
    sampling_rate = input()
    Sampling_rate = float(sampling_rate)

    print("Do you want save this as the default sampling rate? (y/n)")
    default = input()

    if default == 'y':
        with open("Default Values/Default Sampling Rate.pk", 'wb') as fi:
            pickle.dump(Sampling_rate, fi)

    elif default == 'n':
        print()

    else:
        print("Defaulting to n.")

if exists("Default Values/Default Offset.pk"):
    print()
    print(
            "Using the Default Offset from the file Default offset.pk! Delete this file if you do not want to "
            + "use the default value anymore!")

    with open("Default Values/Default Offset.pk", 'rb') as fi:
        offset = pickle.load(fi)

        print("The offset is " + str(offset))
else:

    print("#######################################################################################################")
    print("Enter the amount of time the rat was exposed to the odor to for in seconds.")
    print("#######################################################################################################")
    offset = input()
    offset = float(offset)

    print("Do you want save this as the default offset? (y/n)")
    default = input()

    if default == 'y':
        with open("Default Values/Default Offset.pk", 'wb') as fi:
            pickle.dump(offset, fi)

    elif default == 'n':
        print()

    else:
        print("Defaulting to n.")

if platform.system() == "Windows":
    save_to = sal + "\\" + ntpath.basename(val)
    print(sal)
else:
    save_to = sal + "/" + ntpath.basename(val)

if __name__ == "__main__":

    period = (1 / Sampling_rate)
    Electrode_List = []
    Spike_times = {}

    with h5py.File(val, 'r+') as f:
        me = len(f.get('spiketimes'))
        for i in range(0, me):
            string = "temp_" + str(i)
            string = 'spiketimes/' + string
            neuron = 'neuron_' + str(i)
            spiketimes = f.get(string)[:] * period
            reading_list = []
            for j in spiketimes:
                reading_list.append(float(j))

            Spike_times[neuron] = reading_list

    os.chdir("..")
    events = os.path.abspath(os.curdir)

    if platform.system() == "Windows":
        events = events + "\\Spike2Spyking\\Events.txt"

    else:
        events = events + "/Spike2Spyking/Events.txt"

    with open(events, 'r') as f:
        events_and_time = f.readlines()

    events_and_time = [x[:-1] for x in events_and_time]
    events_and_time = [x.split(',') for x in events_and_time]

    event_list = []
    time_list = []

    for i in events_and_time:
        [x, y] = i
        event_list.append(x)
        time_list.append(float(y))

    time_list_temp = [x + offset for x in time_list]
    with h5py.File(save_to, 'w') as f:
        f.create_dataset("Odor_Names", len(event_list), data=event_list, compression="gzip")
        f.create_dataset("Odor_Onsets", len(time_list), data=time_list, compression="gzip")
        f.create_dataset("Odor_Offsets", len(time_list_temp), data=time_list_temp, compression="gzip")
        for i in Spike_times:
            f.create_dataset(i, len(Spike_times[i]), data=Spike_times[i], compression="gzip")
