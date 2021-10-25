import numpy as np
import h5py
from quantities import uV, Hz, ms, s

if __name__ == "__main__":
    val = r'S:\Ayaan\Data\Numpy Arrays\Spyking\U1, U2, U3 combined - ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.result-merged.hdf5'
    sal = r'S:\Ayaan\Data\Numpy Arrays\Spyking\U1, U2, U3 combined - ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.clusters-merged.hdf5'
    clusters_file = h5py.File(sal, 'r')
    electrodes = np.array(clusters_file.get('electrodes'))
    print(electrodes)
    Sampling_rate = 18518.51851851852*Hz
    period = (1. / Sampling_rate).rescale(s)

    Spike_times = {}
    with h5py.File(val, 'r+') as f:
        me = len(f.get('spiketimes'))
        for i in range(0, me):
            string = "temp_" + str(i)
            string = 'spiketimes/' + string
            electrode = 'electrode_' + str(i)
            Spike_times[electrode] = f.get(string)[:] * period
            print(electrode)
            print(Spike_times[electrode])
            print(len(Spike_times[electrode]))
            print()



