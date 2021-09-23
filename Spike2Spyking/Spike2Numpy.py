import numpy as np
from neo import Spike2IO  # neo v.0.6.1
#import raky


def spykeToNumpy(file_name):
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

    for sig in segment.analogsignals:
        analog_signal = segment.analogsignals[2]

        if sig.annotations['channel_names'][0] == 'U1':
            sampling_rate = sig.sampling_rate
            print(sampling_rate)
            u_times = sig.times
            u1_data = np.squeeze(sig)
            unit_boy = [u1_data]

        elif sig.annotations['channel_names'][0] == 'U2':

            u2_data = np.squeeze(sig)
            unit_boy = np.vstack([unit_boy, u2_data])

        elif sig.annotations['channel_names'][0] == 'U3':
            u3_data = np.squeeze(sig)
            unit_boy = np.vstack([unit_boy, u3_data])

    return unit_boy, u_times


if __name__ == "__main__":
    file_name1 = r"C:\Ayaan Data\ParameterTest_OE8_091119_Preinfusion.smr"
    file_name2 = r"C:\Ayaan Data\ParameterTest_OE8_091119_Postinfusion.smr"

    u_data1, u_times1 = spykeToNumpy(file_name1)
    u_data2, u_times2 = spykeToNumpy(file_name2)
    cut_off = min(len(u_times1), len(u_times2))
    u_times1 = u_times1[:cut_off]
    u_times2 = u_times2[:cut_off]

    if len(u_data1[0]) < len(u_data2[0]):
        u_data2 = np.delete(u_data2, range(len(u_data1[0]), len(u_data2[0])), axis=1)

    elif len(u_data2[0]) < len(u_data1[0]):
        u_data1 = np.delete(u_data1, range(len(u_data2[0]), len(u_data1[0])), axis=1)

    u_final = np.vstack([u_times1, u_data1])
    u_final = np.vstack([u_final, u_data2])

    np.save(r"C:\Ayaan Data\Numpy Arrays\combined_unit_recordings", u_final)

    # spike2_reader = Spike2IO(file_name)
    #
    # blocks = spike2_reader.read()
    # block = blocks[0]
    # # Block contains all the data in a recording session
    # segments = block.segments
    # # Segments are containers for data sharing the same clock
    # segment = segments[0]
    # # We take the first segment of the first block, since the data contains a single block and single segment
    # unit_boy = np.array([])
    # unit_recordings = np.array([])
    #
    # for sig in segment.analogsignals:
    #
    #     if sig.annotations['channel_names'][0] == 'U1':
    #         u_times = sig.times
    #         u1_data = np.squeeze(sig)
    #         unit_boy = [u_times, u1_data]
    #
    #     elif sig.annotations['channel_names'][0] == 'U2':
    #         u2_data = np.squeeze(sig)
    #         unit_boy = np.vstack([unit_boy, u2_data])
    #
    #     elif sig.annotations['channel_names'][0] == 'U3':
    #         u3_data = np.squeeze(sig)
    #         unit_boy = np.vstack([unit_boy, u3_data])
    #
    # print(unit_boy)
    #
    # np.save(r"C:\Ayaan Data\Numpy Arrays\all_unit_recordings", unit_boy)
