import numpy as np
from neo import Spike2IO  # neo v.0.6.1
import h5py
import paramSetUp
import pickle


# Written by Ayaan Khan
# This program takes data from two smr (Spike2) data files and combines them into an numpy array, which is saved to an
# hdf5 file.
# This is so that we can combine post and pre infusion readings into a single file.
# Upon running, this program will create a config file and exit. Fill in the config file with the parameters it needs
# and run the program again

def spyke_to_numpy(file_name):
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

    # Read the data we want from the config file
    with open("Config.txt", 'r') as f:
        # We want the Post and Pre infusion readings, so we take in two spike files
        # Shave off the newline at the end
        file_name1 = f.readline()[:-1]
        file_name2 = f.readline()[:-1]

        # To make sure the file names includes the extension, add .smr to the end if it's not already there
        if file_name1[-4:] != '.smr':
            file_name1 = file_name1 + '.smr'

        if file_name2[-4:] != '.smr':
            file_name2 = file_name2 + '.smr'

        save_to = f.readline()[:-1]

    u_data1, events1, name_and_rate = spyke_to_numpy(file_name1)
    u_data2, events2, name_and_rate2 = spyke_to_numpy(file_name2)

    # Combine the data from the two files
    u_data_final = {}
    for i in list(u_data1):
        u_data_final[i] = np.concatenate((u_data1[i], u_data2[i]))

    # Organize the events by time and save them
    with open("Events.txt", 'w') as f:
        f.write("FILE:" + file_name1.split('\\')[-1:][0] + '\n' + '\n')
        for event in range(0, len(events1.times)):
            f.write("at " + str(events1.times[event]) + ", " + str(events1.labels[event])[2:-1] + '\n')

        f.write(" " + '\n' + '\n' + '\n')

        f.write("FILE:" + file_name2.split('\\')[-1:][0] + '\n' + '\n')
        for event in range(0, len(events2.times)):
            f.write("at " + str(events2.times[event]) + ", " + str(events2.labels[event])[2:-1] + '\n')

    # Save the channel names and sampling rates
    with open("Channels.txt", 'w') as f:
        for ele in name_and_rate:
            f.write(str(ele) + '\n')

    # Obtain JUST the file name of the the spike2 files to know what to name our new file.
    if '\\' in file_name1:
        last_slash = file_name1.rindex('\\')
        file_name1 = file_name1[last_slash + 1:]

    if '\\' in file_name2:
        last_slash = file_name2.rindex('\\')
        file_name2 = file_name2[last_slash + 1:]

    # Remove the extension if the user included it in the config file
    file_name1 = file_name1[:-4]
    file_name2 = file_name2[:-4]

    # If the folder to save_to ends with \, then simply add .hdf5 to the end of the name and save it,
    # otherwise the backslash has to be added to have a legitimate directory
    if save_to[:-1] == '\\':
        save_to = save_to + "combined - " + file_name1 + " and " + file_name2 + ".hdf5"
    else:
        save_to = save_to + '\\' + ''"combined - " + file_name1 + " and " + file_name2 + ".hdf5"

    # Saved as an hdf5 file, for compressions sake
    with h5py.File(save_to, 'w') as f:
        for i in list(u_data_final):
            f.create_dataset(i, len(u_data_final[i]), data=u_data_final[i], compression="gzip")

