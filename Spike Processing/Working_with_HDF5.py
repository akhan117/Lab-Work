import h5py


if __name__ == "__main__":
    spike_list = []
    with h5py.File(r"S:\Ayaan\Data\HDF5 Files\Spike Processing\U1, U2, U3 ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.result-merged.hdf5", 'r') as f:
        for i in f:
            print(i)

        Odor_names = f["Odor_Names"][:]
        Odor_Onsets = f["Odor_Onsets"][:]
        Odor_Offsets = f["Odor_Offsets"][:]

        print()
        print("Now in Neurons")
        neurons = f['Neurons']

        for i in neurons:
            print(i)
            spike_list.append(neurons[i][:])


    # print(Odor_names)
    # print(Odor_Onsets)
    # print(Odor_Offsets)
    print(spike_list)