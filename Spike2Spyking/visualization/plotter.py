import numpy as np
import matplotlib.pylab as plt
import scipy.ndimage as ndi
import filters
import seaborn as sns

# signal processing tutorial
# https://neurodsp-tools.github.io/neurodsp/auto_tutorials/index.html


def plot_LFP(data, fs, events_tuple, tmin=-1, tmax=-1, channel=""):
    sns.set()
    if tmax > tmin >= 0:
        tmax = min(tmax, len(data)/fs)
        data = data[int(tmin * fs):int(tmax * fs)+1]
        x = np.linspace(tmin, tmax, len(data))
    else:
        x = np.linspace(0, int(len(data)/fs), len(data))
        tmin, tmax = 0, len(data)/fs
    plt.figure(figsize=(15, 7))
    plt.plot(x, data, zorder=1)
    plt.ylabel('Voltage', fontsize=12)
    plt.xlabel('Time (seconds)', fontsize=12)
    ymin, ymax = plt.ylim()
    plt.ylim(ymin*0.98, ymax*1.02)
    plt.suptitle(f"LFP {channel}", fontsize=15, y=0.97)

    ymax, ymin = np.max(data), np.min(data)
    ymin_sub, ymax_sub = ymin+(ymax-ymin)*0.1, ymax-(ymax-ymin)*0.2
    valve_onsets = [t1 for _, t1, _ in events_tuple if tmax >= t1 >= tmin]
    odor_onsets = [t2 for _, _, t2 in events_tuple if tmax >= t2 >= tmin]
    # navajowhite
    # darkorange
    plt.vlines(valve_onsets, ymin=ymin_sub, ymax=ymax_sub, color='darkorange',
               linestyle='-', linewidth=1.5, label="Valve Onset", alpha=0.3, zorder=2)
    # firebrick
    # lightcoral
    plt.vlines(odor_onsets, ymin=ymin_sub, ymax=ymax_sub, color='maroon',
               linestyle='--', linewidth=2, label="Odor Onset", alpha=0.3, zorder=2)
    # dimgray
    # darkslategray
    for label, t1, t2 in events_tuple:
        if t1 > tmin and t2 < tmax:
            plt.text(t1, ymin, f"{round(t1, 1)}+{round(t2-t1,1)}", color='dimgray', rotation=80, fontsize=8,
                     ha='left', va='center')
            plt.text(t1, ymax_sub*1.01, label, color='dimgray',
                     rotation=80, fontsize=9, ha='left', va='baseline')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()


def plot_spectrogram(data, fs, events_tuple, channel="", tmin=-1, tmax=-1, fmin=-1, fmax=-1, levels=100, sigma=1, perc_low=1, perc_high=99, nfft=1024, noverlap=512, log_scale=True):
    """
    Butterworth band pass filter between [fmin] and [fmax].

    Data
    ------------
    data: Quantity array or Numpy ndarray
        Your time series of voltage values
    fs: Quantity
        Sampling rate in Hz
    tmin: float/int
        Minimum of time range to plot
    tmax: float/int
        Maximum of time range to plot
    channel: String
        Identity of channel

    Spectrogram parameters
    ------------
    levels: int
        The number of color levels displayed in the contour plot (spectrogram)
    sigma: int
        The standard deviation argument for the gaussian blur
    perc_low, perc_high: int
        Out of the powers displayed in your spectrogram, these are the low and high percentiles
        which mark the low and high ends of your colorbar.

        E.g., there might be a period in the start of the experiment where the voltage time series shifts
        abruptly, which wouldappear as a vertical 'bar' of high power in the spectrogram; setting perc_high
        to a value lower than 100 will make the color bar ignore these higher values (>perc_high), and
        display the 'hottest' colors as the highest power values other than these (<perc_high), allowing
        for better visualization of actual data. Similar effects can be accomplished with vmin/vmax args
        to countourf.
    nfft: int
        The number of data points used in each window of the FFT.
        Argument is directly passed on to matplotlib.specgram(). See the documentation
        `matplotlib.specgram()` for options.
    noverlap: int
        The number of data points that overlap between FFT windows.
        Argument is directly passed on to matplotlib.specgram(). See the documentation
        `matplotlib.specgram()` for options.
    """
    # sns.set()
    plt.rcParams['image.cmap'] = 'jet'

    if tmax > tmin >= 0:
        tmax = min(tmax, len(data)/fs)
        tmin_i = int(tmin * fs)
        tmax_i = int(tmax * fs)
        data = data[tmin_i:tmax_i+1]

    if fmax > fmin >= 0:
        # band pass filter
        filtered_data = filters.cheby2_bp_filter(data, fs, fmin, fmax)
        # new_data = filters.butter_bp_filter(data, fs, fmin, fmax)
        if np.isnan(filtered_data).any():
            print("Frequency band pass width is too narrow. Quit Filter")
        else:
            data = filtered_data

    spec, freqs, bins, __ = plt.specgram(data, NFFT=nfft, Fs=int(
        fs), noverlap=noverlap)  # gives us time and frequency bins with their power

    if fmax > fmin >= 0:
        # extract rows in spec corresponding to desired freqs
        coef = fs/nfft
        fmin_i = int(fmin/coef)
        fmax_i = int(fmax/coef)
        spec = spec[fmin_i:fmax_i+1, :]
        freqs = freqs[fmin_i:fmax_i+1]

    Z = np.flipud(np.log10(spec)*10) if log_scale else np.flipud(spec)
    Z = ndi.gaussian_filter(Z, sigma)  # reduce high frequency noise
    extent = 0, np.amax(bins), freqs[0], freqs[-1]
    levels = np.linspace(np.percentile(Z, perc_low),
                         np.percentile(Z, perc_high), levels)
    x1, y1 = np.meshgrid(bins, freqs)
    x1 += tmin

    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.suptitle(f"Spectrogram {channel}", fontsize=15, y=.94)
    plt.contourf(x1, list(reversed(y1)), Z, vmin=None,
                 vmax=None, extent=extent, levels=levels)
    plt.colorbar()
    plt.axis('auto')

    if tmax > tmin >= 0:
        plt.xlim(tmin, tmax)
    if fmax > fmin >= 0:
        plt.ylim(fmin, fmax)
    tmin, tmax = plt.xlim()

    # add events
    valve_onsets = [t1 for _, t1, _ in events_tuple if tmax >= t1 >= tmin]

    for t1 in valve_onsets:
        plt.axvline(t1, ymin=0, ymax=0.1, color="gray",
                    linestyle="-", linewidth=2, alpha=0.9)
    plt.show()
