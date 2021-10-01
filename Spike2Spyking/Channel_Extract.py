import numpy as np
import h5py

# Written by Ayaan Khan
# This program extracts the channels you specify from the data Spike2Numpy. This program will not run correctly
# without running Spike2Numpy and obtaining the data that it creates!

if __name__ == "__main__":

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

    # Read the combined file so we can extract the channels
    combined_data = np.array([])
    removed = []
    check = 0

    # Go through the files, save the data we want and save it to a numpy array
    with h5py.File(read_from2, 'r+') as f:
        for i in channel_list:
            if i in f:
                removed.append(i)
                temp = f.get(i)[:]
                if check == 0:
                    combined_data = [temp]
                    check += 1
                else:
                    combined_data = np.vstack((combined_data, temp))

    # Check which channels which were given as input were not found
    for j in removed:
        channel_list.remove(j)

    if len(channel_list) >= 0:
        print("The following channels were not found - " + str(channel_list))

    # Use the channels that were found to determine the name of our new file
    present = str(removed[0])
    for i in removed[1:]:
        present = present + ", " + str(i)

    location = location + present + " " + read_from + ".hdf5"

    # Save the file with the extracted channels
    with h5py.File(location, 'w') as f:
        # We save all the data in one data set because spyking-circus seems to use only 1 data-set from a hdf5 file
        f.create_dataset("unit", np.shape(combined_data), data=combined_data, compression="gzip")
