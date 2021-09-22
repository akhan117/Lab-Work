import numpy as np
import csv
from neo import Spike2IO
# import raky
import xlsxwriter
from quantities import s

if __name__ == "__main__":
    file_name = "C:\Ayaan Data\ParameterTest_OE8_091119_Postinfusion.smr"
    spike2_reader = Spike2IO(file_name)

    blocks = spike2_reader.read()
    block = blocks[0]
    # Block contains all the data in a recording session
    segments = block.segments
    # Segments are containers for data sharing the same clock
    segment = segments[0]
    # We take the first segment of the first block, since the data contains a single block and single segment
    unit_boy = np.array([])
    unit_recordings = np.array([])
    u_times = np.array([])
    u1_data = np.array([])
    u2_data = np.array([])
    u3_data = np.array([])

    for sig in segment.analogsignals:

        if sig.annotations['channel_names'][0] == 'U1':
            u_times = sig.times
            u1_data = np.squeeze(sig)
            unit_boy = [u_times, u1_data]

        elif sig.annotations['channel_names'][0] == 'U2':
            u2_data = np.squeeze(sig)
            unit_boy = np.vstack([unit_boy, u2_data])

        elif sig.annotations['channel_names'][0] == 'U3':
            u3_data = np.squeeze(sig)
            unit_boy = np.vstack([unit_boy, u3_data])


    all_unit_recordings = np.array(
        [u_times, u1_data, u2_data, u3_data],
        dtype=object,
    )

    print(all_unit_recordings)
    print(unit_boy)




