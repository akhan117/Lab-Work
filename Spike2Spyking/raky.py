import numpy as np
from neo import Spike2IO  #v0.6.1
import matplotlib.pyplot as plt
from quantities import s


def clip(times, signal, start, duration):
    t1 = times - start
    t1[t1 < 0] = np.max(t1)
    i1 = np.argmin(t1)

    t2 = times - (start + duration)
    t2 = -t2
    t2[t2 < 0] = np.max(t2)
    i2 = np.argmin(t2)

    return times[i1:i2], signal[i1:i2]


def vlines_range(event_times, event_labels, start, duration, baseline=[b'mineral oil', b'BLANK']):
    for i in range(len(event_times)):
        time = event_times[i]
        label = event_labels[i]
        if start < time < start + duration:
            plt.axvline(time, color=('black' if label in baseline else 'red'))


# ======================================================================================================================
# file_name = r'E:\sniffer_data_fall_2019\MergedSpikes\extraction_KM\ParameterTest_OE9_092419_Prepostinfusion.smr'\

# file_name = "/Users/kyrusmama/Desktop/Research/CP Lab animal /" \
#             "Example data ex/ParameterTest_OE8_091819_Prepostinfusion.smr"

file_name = "C:\Ayaan Data\ParameterTest_OE8_091119_Postinfusion.smr"

print("extracting data from: ", file_name, '\n')
# Access the file
spike2_reader = Spike2IO(file_name)

# Break the file up into "blocks"
blocks = spike2_reader.read()
print("number of blocks: ", len(blocks))
# take the first block
block, = blocks

# Break each block up into segments
segments = block.segments
print("number of segments: ", len(segments))
# take the first segment
segment = segments[0]

# ======================================================================================================================
# Signal getting
# things like LFPs, units, etc
print("SIGNALS")
# print(segment.analogsignals)

start = 492 * s
duration = 60 * s
channel = 2

# for each signal, print the channel names
for sig in segment.analogsignals:
    # print(sig, sig.annotations, sig.channel_index)
    print(sig.annotations['channel_names'][0])

# for the first signal
if len(segment.analogsignals) >= 1:
    analog_signal = segment.analogsignals[channel]

    # plotting some data from the signal (uncomment plotting)
    print('sampling rate of ', analog_signal.annotations['channel_names'][0], ' = ', analog_signal.sampling_rate)

    unitless_data = np.squeeze(analog_signal.as_array())
    # plt.plot(analog_signal.times[:10000], unitless_data[:10000])

    cliptime, clipsignal = clip(analog_signal.times, unitless_data, start, duration)
    plt.plot(cliptime, clipsignal)

    plt.title(analog_signal.annotations['channel_names'][0])

    # print some information from the first signal
    print(analog_signal.sampling_rate, analog_signal.t_start, analog_signal.t_stop,
            analog_signal.annotations, analog_signal.annotations['channel_names'][0])
    # plt.show()
    # for signal in segment.analogsignals:
    #     print(signal.annotations)

# ======================================================================================================================
# Event getting
# things like odor presentations
print("EVENTS")

events = segment.events
assert len(events) >= 1
event = events[0]

print(event.annotations)

print(event.times)
print(event.labels)
vlines_range(event.times, event.labels, start, duration)

plt.show()

# ======================================================================================================================