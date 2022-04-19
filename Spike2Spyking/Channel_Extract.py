import numpy as np
import h5py
import ntpath
import platform
import pickle
from os.path import exists
from tkinter.filedialog import askopenfilename

# Written by Ayaan Khan
# This program extracts the channels you specify from the data Spike2Numpy. This program will not run correctly
# without running Spike2Numpy and obtaining the data that it creates!

if __name__ == "__main__":
    print("Pick the file you want to extract channels from")
    read_from = askopenfilename()

    if exists("Default Values/Default Channels.pk"):
        print()
        print("Using the Default Values from the file Default Channels.pk! Delete this file if you do not want to use "
              + "these default values anymore!")

        with open("Default Values/Default Channels.pk", 'rb') as fi:
            channel_list = pickle.load(fi)

        print("The default channels are " + str(channel_list))
    else:

        print("#######################################################################################################")
        print("Enter the channels you want to input, separated by a comma. (e.g. - U1, U2, U3)")
        print("#######################################################################################################")
        channel_name = input()
        channel_list = channel_name.split(",")
        for i in range(0, len(channel_list)):
            channel_list[i] = channel_list[i].strip()

        print(
            "Do you want to save these channels as the default channels to extract? (y/n)")
        default = input()

        if default == 'y':
            with open("Default Values/Default Channels.pk", 'wb') as fi:
                pickle.dump(channel_list, fi)

        elif default == 'n':
            print()

        else:
            print("Defaulting to n.")

    print()

    # Read the combined file so we can extract the channels
    combined_data = np.array([])
    removed = []
    check = 0

    # Go through the files, save the data we want and save it to a numpy array
    with h5py.File(read_from, 'r+') as f:
        for i in channel_list:

            if i in f:

                removed.append(i)
                temp = f.get(i)[:]

                print(str(i) + " was extracted.")

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

    read_from1, read_from2 = ntpath.split(read_from)

    location = read_from1 + '/' + channels_present + ' ' + read_from2
    print(np.shape(combined_data))
    print("Combining the channels....")
    # Save the file with the extracted channels
    with h5py.File(location, 'w') as f:
        # We save all the data in one data set because spyking-circus seems to use only 1 data-set from a hdf5 file
        f.create_dataset("unit", np.shape(combined_data),
                         data=combined_data, compression="gzip")
