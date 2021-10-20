import numpy as np
import h5py

if __name__ == "__main__":
    val = r'S:\Ayaan\Data\Numpy Arrays\Spyking\U1, U2, U3 combined - ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.clusters-merged.hdf5'
    with h5py.File(val, 'r+') as f:
        for i in range(0, 3):
            print(i)
            time = 'times_' + str(i)
            print(f.get(time)[:])
            something = f.get(time)[:]
        print(f.keys())
        print('times_i' in f)
        print(f.get('time_i'))
        print(something/18518.51851851852)