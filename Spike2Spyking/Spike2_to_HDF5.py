import numpy as np
import config_setup
from neo import Spike2IO  # neo v.0.6.1
import h5py
import ntpath
import platform


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
    print("In " + ntpath.basename(file) + ", the sampling rate and number of readings are:")
    # Go through all the channels, and add the data from each to the dictionary
    for sig in segment.analogsignals:
        channel_data = np.squeeze(sig)
        channel_name = sig.annotations['channel_names'][0]
        channels_data[channel_name] = channel_data

        # Saving the channel names and sampling rate
        name_rate = np.append(name_rate, (sig.annotations['channel_names'][0], str(sig.sampling_rate)))

        print(str(channel_name) + ": " + str(sig.sampling_rate) +
              ", " + str(len(channels_data.get(channel_name))))

    print()
    print()
    a = segment.events[0]
    print(a.times)
    print(a.labels)
    b = segment.events[1]
    print(b.times)
    print(b.labels)
    c = segment.events[2]
    print(c.times)
    print(c.labels)
    print()
    return channels_data, segment.events[0], name_rate


if __name__ == "__main__":

    # Read the data we want from the config file
    with open("Config.txt", 'r') as f:
        # We want the Post and Pre infusion readings, so we take in two spike files
        # Shave off the newline at the end
        file_name = f.readline()[:-1]
        file_list = file_name.split(",")
        for i in range(0, len(file_list)):
            file_list[i] = file_list[i].strip()

        # To make sure the file names includes the extension, add .smr to the end if it's not already there
        file_list = [file + '.smr' for file in file_list if file[-4:] != '.smr']

        save_to = f.readline()[:-1]

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

    print("In the combined file, the number of readings are:")
    for key in u_data.keys():
        print(str(key) + ": " + str(len(u_data.get(key))))

    # Organize the events by time and save them
    with open("Events.txt", 'w') as f:
        z = 0
        to_add = 0
        for event in events:
            z += 1

            for event1 in range(0, len(event.times)):

                timing = float(event.times[event1]) + to_add
                f.write(str(event.labels[event1])[2:-1] + ", " + str(timing) + '\n' )
                if event1 is len(events1.times) - 1:
                    to_add += float(events1.times[event1])




    # Save the channel names and sampling rates
    with open("Channels.txt", 'w') as f:
        for ele in name_and_rate:
            f.write(str(ele) + '\n')

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
            save_to = save_to + "combined - " + full_name + ".hdf5"
        else:
            save_to = save_to + '\\' + ''"combined - " + full_name + ".hdf5"

    # For OSX and Linux -> The directory would likely include a forward slash instead
    else:
        if save_to[:-1] == '/':
            save_to = save_to + "combined - " + full_name + ".hdf5"
        else:
            save_to = save_to + '/' + "combined - " + full_name + ".hdf5"

    # Save to our file
    # with h5py.File(save_to, 'w') as f:
    #     for i in list(u_data):
    #         f.create_dataset(i, len(u_data[i]), data=u_data[i], compression="gzip")
