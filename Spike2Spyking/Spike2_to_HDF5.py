import numpy as np
from neo import Spike2IO  # neo v.0.6.1
import h5py
import ntpath
import platform
import pickle
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from os.path import exists


# Written by Ayaan Khan
# This program takes data from two smr (Spike2) data files and combines them into an numpy array, which is saved to an
# hdf5 file.
# This is so that we can combine post and pre infusion readings into a single file.
# Upon running, this program will create a config file and exit. Fill in the config file with the parameters it needs
# and run the program again

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
        name_rate = np.append(name_rate, (sig.annotations['channel_names'][0], str(sig.sampling_rate)))

    return channels_data, segment.events[0], name_rate


if __name__ == "__main__":

    if exists("Default Values/Default Number of Files.pk"):
        print()
        print("Using the default number of files from the file Default Number of Files.pk! Delete this file if you do"
              + " not want to use the default number of files anymore!")

        with open("Default Values/Default Number of Files.pk", 'rb') as fi:
            x = pickle.load(fi)

        print("Default number of files is " + x)

    else:
        print("#######################################################################################################")
        print("How many files do you want to work with?")
        print("#######################################################################################################")
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
        print("Using the Default save to location from the file Default Save to Location.pk! Delete this file if you do"
              + " not want to use the default save to location anymore!")

        with open("Default Values/Default Save to Location.pk", 'rb') as fi:
            save_to = pickle.load(fi)

        print("Saving to " + save_to)

    else:
        print("#######################################################################################################")
        print("Where do you want to save the files to")
        print("#######################################################################################################")
        save_to = askdirectory()

        print("Do you want save this as the default location to save to (y/n)")
        default = input()

        if default == 'y':
            with open("Default Values/Default Save to Location.pk", 'wb') as fi:
                pickle.dump(save_to, fi)

        elif default == 'n':
            print()

        else:
            print("Defaulting to n.")

    print()

    u_data = {}
    events = []

    # Create Dictionary of combined data from all our files
    for file in file_list:
        u_data1, events1, name_and_rate = spyke_to_numpy(file)
        events.append(events1)

        for i in list(u_data1):
            if i not in u_data:
                u_data[i] = np.array([])
            u_data[i] = np.concatenate((u_data[i], u_data1[i]))

    events_f = []
    # Organize the events by time and save them
    with open("Events.txt", 'w') as f:
        z = 0
        to_add = 0
        for event in events:
            z += 1

            for event1 in range(0, len(event.times)):

                timing = float(event.times[event1]) + to_add
                events_f.append(np.string_(str(event.labels[event1])[2:-1]))
                events_f.append(np.string_(str(timing)))
                f.write(str(event.labels[event1])[2:-1] + ", " + str(timing) + '\n')
                if event1 is len(events1.times) - 1:
                    to_add += float(events1.times[event1])

    print(events_f)
    # Save the channel names and sampling rates
    with open("Channels.txt", 'w') as f:
        for ele in name_and_rate:
            f.write(str(ele) + '\n')
    print(name_and_rate)
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

    print("Working on saving and compressing the data.....")
    # Save to our file
    with h5py.File(save_to, 'w') as f:
        for i in list(u_data):
            f.create_dataset(i, len(u_data[i]), data=u_data[i], compression="gzip")
        f.create_dataset("Events", len(events_f), data=events_f, compression="gzip")
