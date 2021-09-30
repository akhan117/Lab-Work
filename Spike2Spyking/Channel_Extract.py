import numpy as np

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
    for i in range(0, len(data)):

        for e in channel_list:
            if data[i] == e:
                channel_list.remove(e)
                index_array.append(i)

    if len(channel_list) >= 0:
        for i in channel_list:
            print('Channel ' + i + ' was not found')

    location2 = location[:-1]
    if location2[:-1] != '\\':
        location2 = location2 + '\\'

    if '\\' in location2:

        last_slash = location2.rindex('\\')
        location2 = location2[:last_slash]
        location3 = location2[:last_slash]
        location2 = location2 + '\\'

    else:
        location2 = ''

    location = location[:-1] + ".npy"

    if '\\' in file_name1:
        last_slash = file_name1.rindex('\\')
        file_name1 = file_name1[last_slash + 1:]

    if '\\' in file_name2:
        last_slash = file_name2.rindex('\\')
        file_name2 = file_name2[last_slash + 1:]

    if file_name1[-4:] == '.smr':
        file_name1 = file_name1[:-4]

    if file_name2[-4:] == '.smr':
        file_name2 = file_name2[:-4]

    porpoise = "combined - " + file_name1 + " and " + file_name2 + ".npy"
    porpoise2 = location3 + '\\' + porpoise
    location2 = location2 + channel_name + " " + porpoise
    combined_data = np.load(porpoise2)

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
