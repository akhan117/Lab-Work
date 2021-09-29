import numpy as np
from neo import Spike2IO  # neo v.0.6.1
import paramSetUp
import pickle


# Written by Ayaan Khan
# This program takes data from two smr (Spike2) data files and combines them into an numpy array.
# This is so that we can combine post and pre infusion readings into a single file.
# Upon running, this program will create a config file and exit. Fill in the config file with the parameters it needs
# and run the program again

def spykeToNumpy(file_name):
    # Typical Set up for Neo to access the file, and we only have one block and one segment
    spike2_reader = Spike2IO(file_name)
    blocks = spike2_reader.read()
    block = blocks[0]
    segments = block.segments
    segment = segments[0]

    channels_data = np.array([])
    time_check = False
    name_rate = np.array([])
    data_len = 0

    # Go through all the channels, and add the data from each to the array
    for sig in segment.analogsignals:
        channel_data = np.squeeze(sig)

        # Saving the channel names and sampling rate
        name_rate = np.append(name_rate, (sig.annotations['channel_names'][0], str(sig.sampling_rate)))
        data_len = max(data_len, len(channel_data))

        if not time_check:
            channels_data = [channel_data]
            time_check = True

        else:
            if len(channels_data[0]) < data_len:
                c, rows = np.shape(channels_data)

                # Pad if necessary - not all channels have the same amount of samples
                none_array = np.full([c, data_len - rows], np.Inf)
                channels_data = np.concatenate((channels_data, none_array), axis=1)

            channels_data = np.vstack([channels_data, channel_data])

    return channels_data, segment.events[0], name_rate

    # Iterate through the channel names
    # for sig in segment.analogsignals:
    #
    #     for chan in channels:
    #
    #         # Pick out the Channel names we're interested in
    #         if sig.annotations['channel_names'][0] == chan:
    #
    #             # Check to see if we've already picked up the sampling data - we only want it once
    #             if not time_check:
    #
    #                 # We print the sampling rate as it's required for SpyKingCircus
    #                 sampling_rate = sig.sampling_rate
    #                 print("The Sampling Rate is", end=" ")
    #                 print(sampling_rate)
    #
    #                 # Extract sampling data and unit/lfp data
    #                 u_times = sig.times
    #                 u_data = np.squeeze(sig)
    #                 print(sig.annotations['channel_names'][0])
    #                 print(len(u_data))
    #                 unit_boy = [u_data]
    #                 time_check = True
    #
    #             else:
    #                 # Only Extract unit/lfp data, and we add it as an additional row to our existing Array
    #                 print(sig.annotations['channel_names'][0] + ' ' + str(sig.sampling_rate))
    #                 print(len(sig.times))
    #                 print(len(sig))
    #                 u1_data = np.squeeze(sig)
    #
    #                 print(len(u1_data))
    #                 unit_boy = np.vstack([unit_boy, u1_data])
    #
    # return unit_boy, u_times, segment.events[0]


if __name__ == "__main__":

    file_name1 = ""
    file_name2 = ""

    # Read the data we want from the config file
    with open("Config.txt", 'r') as f:
        # We want the Post and Pre infusion readings, so we take in two spike files
        # Shave off the newline at the end
        file_name1 = f.readline()[:-1]
        file_name2 = f.readline()[:-1]
        save_to = f.readline()[:-1]

    u_data1, events1, name_and_rate = spykeToNumpy(file_name1)
    u_data2, events2, name_and_rate2 = spykeToNumpy(file_name2)

    print(np.shape(u_data1))
    print(np.shape(u_data2))
    # Combine the data from the two files
    u_data_final = np.concatenate((u_data1, u_data2), axis=1)

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

    if '\\' in file_name1:
        last_slash = file_name1.rindex('\\')
        file_name1 = file_name1[last_slash + 1:]

    if '\\' in file_name2:
        last_slash = file_name2.rindex('\\')
        file_name2 = file_name2[last_slash + 1:]

    file_name1 = file_name1[:-4]
    file_name2 = file_name2[:-4]
    print(file_name1)
    print(file_name2)
    if save_to[:-1] == '\\':
        save_to = save_to + "combined - " + file_name1 + " and " + file_name2
    else:
        save_to = save_to + '\\' + ''"combined - " + file_name1 + " and " + file_name2

    np.save(save_to, u_data_final)
