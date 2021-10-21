import numpy as np
import h5py

if __name__ == "__main__":
    val = r'S:\Ayaan\Data\Numpy Arrays\Spyking\U1, U2, U3 combined - ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.result-merged.hdf5'
    with h5py.File(val, 'r+') as f:
        print(f.keys())
        me = len(f.get('spiketimes'))
        print(me)
        for i in range(0, me):
            string = "temp_" + str(i)
            string = 'spiketimes/' + string
            print(f.get(string)[:] / 18518.51851851852)
            print(string)
