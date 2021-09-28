import numpy as np


# Written by Ayaan Khan
# This program extracts the channels you specify from the data Spike2Numpy. This program will not run correctly
# without running Spike2Numpy and obtaining the data that it creates!

if __name__ == "__main__":

    # Accept the channels, put them into a list.
    val = input("Enter the channels (e.g - U1, U2, U3): ")
    val = val.split(',')
    for i in range(0, len(val)):
        val[i] = val[i].strip()

    # Obtain the indexes for the channels we need
    with open("Channels.txt", 'r') as f:
        data = f.read()

    data = data.split('\n')
    data = data[::2]

    index_array = []
    for i in range(0, len(data)):

        for e in val:
            if data[i] == e:
                val.remove(e)
                index_array.append(i)

    if len(val) >= 0:
        for i in val:
            print('Channel ' + i + ' was not found')

    # Find out where the Spike2Numpy array is stored at and load it. Also save the extracted file to that location.
    with open("Config.txt", 'r') as f:
        location = f.readline()
        location = f.readline()
        location = f.readline()

    location2 = location[:-1]
    if '\\' in location2:

        last_slash = location2.rindex('\\')
        location2 = location2[:last_slash]
        location2 = location2 + '\\' + 'extracted_channels'

    else:
        location2 = 'extracted_channels'

    location = location[:-1] + ".npy"
    combined_data = np.load(location)

    # Extract the channels we need and save the array
    check = 0
    u_data = np.array([])
    for i in index_array:
        if check == 0:
            u_data = combined_data[i]
            check += 1
        else:
            u_data = np.vstack([u_data, combined_data[i]])

    np.save(location2, u_data)
