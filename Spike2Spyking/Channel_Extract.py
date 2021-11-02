import numpy as np
import h5py
import ntpath
import platform

# Written by Ayaan Khan
# This program extracts the channels you specify from the data Spike2Numpy. This program will not run correctly
# without running Spike2Numpy and obtaining the data that it creates!

if __name__ == "__main__":

    # Find out where the Spike2Numpy array is stored at and load it. Also save the extracted file to that location.
    with open("Config.txt", 'r') as f:
        file_name = f.readline()[:-1]
        file_list = file_name.split(",")
        for i in range(0, len(file_list)):
            file_list[i] = file_list[i].strip()

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

    # Obtain JUST the file name of the the spike2 files to know where our file is
    file_list = [ntpath.basename(file) for file in file_list]
    for i in range(0, len(file_list)):
        if '.smr' in file_list[i]:
            file_list[i] = file_list[i][:-4]

    # Remove newline
    location = location[:-1]

    # For Windows -> If the folder to save_to ends with \, then simply add .hdf5 to the end of the name and save it,
    # otherwise the backslash has to be added to have a legitimate directory
    if platform.system() == "Windows":
        if location[:-1] != '\\':
            location = location + '\\'

    else:
        if location[:-1] != '/':
            location = location + '/'

    # Recreate the name of the final file in order to access it
    read_from = "combined - " + file_list[0]
    for i in range(1, len(file_list)):
        read_from = read_from + " and " + file_list[i]

    # Recreate the combined file name, so we can load it and prepare the save_to location as well
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

                print(str(i) + " was extracted, length: " + str(len(temp)))

                if check == 0:
                    combined_data = [temp]
                    check += 1
                else:
                    combined_data = np.vstack((combined_data, temp))

    # Check which channels which were given as input were not found
    for j in removed:
        channel_list.remove(j)

    if len(channel_list) > 0:
        print("The following channels were not found - " + str(channel_list))


    # Use the channels that were found to determine the name of our new file
    channels_present = str(removed[0])
    for i in removed[1:]:
        channels_present = channels_present + ", " + str(i)

    location = location + channels_present + " " + read_from + ".hdf5"
    print(np.shape(combined_data))

    # Save the file with the extracted channels
    with h5py.File(location, 'w') as f:
        # We save all the data in one data set because spyking-circus seems to use only 1 data-set from a hdf5 file
        f.create_dataset("unit", np.shape(combined_data), data=combined_data, compression="gzip")
