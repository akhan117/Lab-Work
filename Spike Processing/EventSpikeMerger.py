import numpy as np
import h5py
from quantities import uV, Hz, ms, s
import os
import platform
from os.path import exists
import ntpath
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

print("###############################################################################################################")
print("Select the result-merged.hdf5 file from Spyking-Circus")
print("###############################################################################################################")
print()
val = askopenfilename()

print("###############################################################################################################")
print("Select the folder you want to print from")
print("###############################################################################################################")
print()
sal = askdirectory()

if platform.system() == "Windows":
    save_to = sal + "\\" + ntpath.basename(val)
    print(sal)
else:
    save_to = sal + "/" + ntpath.basename(val)

if __name__ == "__main__":

    Sampling_rate = 18518.51851851852 * Hz
    period = (1. / Sampling_rate).rescale(s)
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

    print(event_list)
    print(time_list)
    print("Enter the the amount of time the rat is exposed to the odor for, in seconds:")
    offset = input()
    offset = float(offset)
    time_list_temp = [x + offset for x in time_list]
    print(time_list_temp)
    with h5py.File(save_to, 'w') as f:
        f.create_dataset("Odor_Names", len(event_list), data=event_list, compression="gzip")
        f.create_dataset("Odor_Onsets", len(time_list), data=time_list, compression="gzip")
        f.create_dataset("Odor_Offsets", len(time_list_temp), data=time_list_temp, compression="gzip")
        for i in Spike_times:
            f.create_dataset(i, len(Spike_times[i]), data=Spike_times[i], compression="gzip")

    with h5py.File(save_to, 'r') as f:
        print(f.get("Odor_Names")[:])
