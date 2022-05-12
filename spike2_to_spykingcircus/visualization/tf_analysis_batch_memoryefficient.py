import numpy as np
from scipy.io import loadmat
from scipy import signal
from filters import butter_lowpass_filter
import neo
from quantities import uV, ms, Hz, s
from spectrogram import plot_spectrogram
from change_in_power import change_power
import mne
import matplotlib.pyplot as plt
import math
import h5py
import os


def lpf_epoch(arr):
    """
    Parameters:
        arr [list/array]: 
            input array to be epoched

    Output:
        Epoched array processed with specified parameters
    """
    pass


proj_dir = ""
save_dir = ""
file_dir = proj_dir + r'ephys_filtandrsamp\notch_filt\\'

try:
    os.mkdir(save_dir)
except:
    print('directory already exists')


Fs = 30000 * Hz  # Sampling frequency
ChannelCount = 32
rfs = 1000 * Hz
segment_size = [-4, 3]
segment_length = np.abs(segment_size[1] - segment_size[0])
baseline = [-3, -.5]
change_pow_seg_size = [-1, 1]
calc_psd = False
freqs = np.arange(1, 100.1, 2)  # define frequencies of interest
n_cycles = freqs / 2
# n_cycles[np.where(n_cycles > 10)] = 10
ch_types = []

for ch in range(0, ChannelCount):
    ch_types.append('eeg')

info = mne.create_info(ch_names=list(
    map(str, np.arange(1, 33, 1))), sfreq=rfs/Hz, ch_types=ch_types)
varname = 'PREXTimes_awake'
avg_elecs = True

for file in range(0, len(os.listdir(file_dir))):
    fname = os.listdir(file_dir)[file]
    fname = fname.replace('.npy', '')
    fileloc = proj_dir + 'processed\seperated\\'
    FVSwitchTimesOn = loadmat(fileloc + fname + '_' + varname)
    FVSwitchTimesOn = FVSwitchTimesOn['x']
    fileloc = file_dir
    data = np.load(fileloc+fname+'.npy')
    if avg_elecs:
        # smells, events, freqs, times
        pow_arr = np.empty((16, 45, len(freqs), int(segment_length*rfs)))
    else:
        # channels, smells, freqs, times
        pow_arr = np.empty((32, 16, 45, len(freqs), int(segment_length * rfs)))
    pow_arr[:] = np.nan
    for smell in range(0, FVSwitchTimesOn.shape[1]):
        # could also loop through smells...
        curr_switchTimesOn = FVSwitchTimesOn[0, smell][0]
        if len(curr_switchTimesOn) != 0:  # if this isn't empty (it is sometimes)
            for i in range(0, curr_switchTimesOn.shape[0]):
                start = curr_switchTimesOn[i] + segment_size[0]
                #end = curr_switchTimesOff[smell] + 3
                end = curr_switchTimesOn[i] + segment_size[1]
                epochs = np.empty(
                    (1, ChannelCount, int(segment_length * (rfs/Hz))))
                for elec in range(0, ChannelCount):
                    try:
                        epochs[0, elec, :] = data[elec, int(
                            round(start * (rfs/Hz), 4)):int(round(end * (rfs/Hz), 4))]
                        epoch_suc = True
                    except:
                        # should be because the end time was after the end of the data
                        print('epoching failed')
                        epoch_suc = False

                if epoch_suc:
                    epochs = mne.EpochsArray(epochs, info)
                    tmp_pow = mne.time_frequency.tfr_morlet(
                        epochs, freqs=freqs, n_cycles=n_cycles, return_itc=False, average=False)
                    # tmp_pow.apply_baseline(mode='zscore', baseline=(baseline[0] - segment_size[0], baseline[1] - segment_size[0]))

                    print(smell+1)
                    if not avg_elecs:
                        pow_arr[:, smell, i, :, :] = np.squeeze(tmp_pow.data)
                    else:
                        pow_arr[smell, i, :, :] = np.mean(
                            np.squeeze(tmp_pow.data), 0)
            else:
                print(smell)

        np.save(save_dir+fname+'_pow.npy', pow_arr)
        #np.save(save_dir + fname + '_all_elecs_pow.npy', pow_arr)

        tmp_pow.save(save_dir + fname + '_tmp_pow-tfr.h5', overwrite=True)
