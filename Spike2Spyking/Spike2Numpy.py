import numpy as np
from neo import Spike2IO  # neo v.0.6.1


# Written by Ayaan Khan
# This program takes data from two smr (Spike2) data files and combines them into an numpy array.
# This is so that we can combine post and pre infusion readings into a single file.
# Upon running, this program will create a config file and exit. Fill in the config file with the parameters it needs
# and run the program again

def spykeToNumpy(file_name, channels):
    # Typical Set up for Neo to access the file, and we only have one block and one segment
    spike2_reader = Spike2IO(file_name)
    blocks = spike2_reader.read()
    block = blocks[0]
    segments = block.segments
    segment = segments[0]

    unit_boy = np.array([])
    time_check = False

    # Iterate through the channel names
    for sig in segment.analogsignals:

        for chan in channels:

            # Pick out the Channel names we're interested in
            if sig.annotations['channel_names'][0] == chan:

                # Check to see if we've already picked up the sampling data - we only want it once
                if not time_check:

                    # We print the sampling rate as it's required for SpyKingCircus
                    sampling_rate = sig.sampling_rate
                    print("The Sampling Rate is", end=" ")
                    print(sampling_rate)

                    # Extract sampling data and unit/lfp data
                    u_times = sig.times
                    u_data = np.squeeze(sig)
                    unit_boy = [u_data]
                    time_check = True

                else:
                    # Only Extract unit/lfp data, and we add it as an additional row to our existing Array
                    u1_data = np.squeeze(sig)
                    unit_boy = np.vstack([unit_boy, u1_data])

        # if sig.annotations['channel_names'][0] == 'U1':
        #     sampling_rate = sig.sampling_rate
        #     print(sampling_rate)
        #     u_times = sig.times
        #     u1_data = np.squeeze(sig)
        #     unit_boy = [u1_data]
        #
        # elif sig.annotations['channel_names'][0] == 'U2':
        #
        #     u2_data = np.squeeze(sig)
        #     unit_boy = np.vstack([unit_boy, u2_data])
        #
        # elif sig.annotations['channel_names'][0] == 'U3':
        #     u3_data = np.squeeze(sig)
        #     unit_boy = np.vstack([unit_boy, u3_data])

    # Return all the Channel data as an Array, and the Sampling data as well
    return unit_boy, u_times


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

        # Last line may or may not have a newline, so shave depending on that
        channel_name = f.readline()

        if channel_name[-1:] == '\n':
            channel_name = channel_name[:-1]

        # Save the Channels we need as a list for iteration
        channel_list = channel_name.split(",")
        for i in range(0, len(channel_list)): channel_list[i] = channel_list[i].strip()

    u_data1, u_times1 = spykeToNumpy(file_name1, channel_list)
    u_data2, u_times2 = spykeToNumpy(file_name2, channel_list)

    # The post and pre infusion files have roughly the same number as samples (time spent recording), but we need them
    # to be exactly the same. So we must determine which is the shorter one and make them both the same length.
    cut_off = min(len(u_times1), len(u_times2))
    u_times1 = u_times1[:cut_off]
    u_times2 = u_times2[:cut_off]

    # Making sure the larger unit/lfp data set falls in line with the amount of samples
    if len(u_data1[0]) < len(u_data2[0]):
        u_data2 = np.delete(u_data2, range(len(u_data1[0]), len(u_data2[0])), axis=1)

    elif len(u_data2[0]) < len(u_data1[0]):
        u_data1 = np.delete(u_data1, range(len(u_data2[0]), len(u_data1[0])), axis=1)

    # Combine unit/ lfp files from both files into the final numpy array, and save it
    # u_final = np.vstack([u_times1, u_data1])
    # u_final = np.vstack([u_final, u_data2])

    u_final = np.vstack([u_data1, u_data2])
    print(np.shape(u_final))
    np.save(save_to, u_final)
