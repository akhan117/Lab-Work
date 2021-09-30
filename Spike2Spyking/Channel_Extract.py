import numpy as np
import h5py

# Written by Ayaan Khan
# This program extracts the channels you specify from the data Spike2Numpy. This program will not run correctly
# without running Spike2Numpy and obtaining the data that it creates!

if __name__ == "__main__":

    # Obtain the indexes for the channels we need
    with open("Channels.txt", 'r') as f:
        data = f.read()

    data = data.split('\n')
    data = data[::2]

    # Find out where the Spike2Numpy array is stored at and load it. Also save the extracted file to that location.
    with open("Config.txt", 'r') as f:
        file_name1 = f.readline()[:-1]
        file_name2 = f.readline()[:-1]
        location = f.readline()
        channel_name = f.readline()

        if channel_name[-1:] == '\n':
            channel_name = channel_name[:-1]

        # Save the Channels we need as a list for iteration
        channel_list = channel_name.split(",")
        for i in range(0, len(channel_list)):
            channel_list[i] = channel_list[i].strip()

    index_array = []
    # Save the index of the channels that are there and remove them from channel_list.
    for i in range(0, len(data)):

        for e in channel_list:
            if data[i] == e:
                channel_list.remove(e)
                index_array.append(i)

    # If the channels are still in channel_list, then that means there were not in the original spike2 file.
    if len(channel_list) >= 0:
        for i in channel_list:
            print('Channel ' + i + ' was not found')

    # Silly string manipulation to make sure that we can obtain the folder containing the file name and also
    # the name of the file itself.

    # Remove newline
    location = location[:-1]

    if location[:-1] != '\\':
        location = location + '\\'

    last_slash = location.rindex('\\')
    location = location[:last_slash]
    location = location + '\\'

    # Obtain JUST the file name of the the spike2 files to know what to name our new file.
    if '\\' in file_name1:
        last_slash = file_name1.rindex('\\')
        file_name1 = file_name1[last_slash + 1:]

    if '\\' in file_name2:
        last_slash = file_name2.rindex('\\')
        file_name2 = file_name2[last_slash + 1:]

    # Remove the extension if the user included it in the config file
    if file_name1[-4:] == '.smr':
        file_name1 = file_name1[:-4]

    if file_name2[-4:] == '.smr':
        file_name2 = file_name2[:-4]

    # Recreate the combined file name, so we can load it and prepare the save_to location as well
    read_from = "combined - " + file_name1 + " and " + file_name2
    read_from2 = location + read_from + ".hdf5"
    location = location + channel_name + " " + read_from + ".hdf5"

    # Read the combined file so we can extract the channels
    f = h5py.File(read_from2, 'r+')
    combined_data = f["test"]

    print(np.shape(combined_data))

    # Extract the channels we need and save the array
    check = 0
    u_data = np.array([])
    for i in index_array:
        if check == 0:
            u_data = combined_data[i]
            check += 1
        else:
            u_data = np.vstack([u_data, combined_data[i]])

    f.close()

    # Save the file with the extracted channels
    with h5py.File(location, 'w') as f:
        f.create_dataset("test", np.shape(u_data), data=u_data, compression="gzip")
