import numpy as np
# import neo
# import scipy.io
# from scipy import signal
import matplotlib.pylab as plt
# from quantities import Hz, uV, ms, s
from numpy import meshgrid
import scipy.ndimage as ndi
import filters
# from lfp_processing.filters import butter_lowpass_filter, iir_notch
# from ephys_analysis.mcd_conv import get_electrode_data

# signal processing tutorial
# https://neurodsp-tools.github.io/neurodsp/auto_tutorials/index.html


def plot_spectrogram(data, fs, tmin=-1, tmax=-1, fmin=-1, fmax=-1, channel="", levels=100, sigma=1, perc_low=1, perc_high=99, nfft=1024, noverlap=512):
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

    plt.rcParams['image.cmap'] = 'jet'
    # print(f"freq: {fs}")
    if tmax > tmin >= 0:
        tmax = min(tmax, len(data)/fs) + 1
        tmin_i = int(tmin * fs)
        tmax_i = int(tmax * fs)
        data = data[tmin_i:tmax_i]

    # data = ndi.gaussian_filter(data, sigma)
    if fmax > fmin >= 0:
        # band pass filter
        # new_data = filters.cheby2_bp_filter(data, fs, fmin, fmax)
        new_data = filters.butter_bp_filter(data, fs, fmin, fmax)
        if np.isnan(new_data).any():
            print("Frequency band pass width is too narrow. Quit Filter")
        else:
            data = new_data

    spec, freqs, bins, __ = plt.specgram(data, NFFT=nfft, Fs=int(
        fs), noverlap=noverlap)  # gives us time and frequency bins with their power

    if fmax > fmin >= 0:
        # extract rows in spec corresponding to desired freqs
        coef = fs/nfft
        fmin_i = int(fmin/coef)
        fmax_i = int(fmax/coef)
        spec = spec[fmin_i:fmax_i+1, :]
        freqs = freqs[fmin_i:fmax_i+1]

    Z = np.flipud(np.log10(spec)*10)
    Z = ndi.gaussian_filter(Z, sigma)  # reduce high frequency noise
    extent = 0, np.amax(bins), freqs[0], freqs[-1]
    levels = np.linspace(np.percentile(Z, perc_low),
                         np.percentile(Z, perc_high), levels)
    x1, y1 = np.meshgrid(bins, freqs)
    x1 += tmin

    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.suptitle(f"Spectrogram of {channel}", fontsize=15, y=.94)
    plt.contourf(x1, list(reversed(y1)), Z, vmin=None,
                 vmax=None, extent=extent, levels=levels)
    plt.colorbar()
    plt.axis('auto')
    if tmax > tmin >= 0:
        plt.xlim(tmin, tmax)
    if fmax > fmin >= 0:
        plt.ylim(fmin, fmax)
    plt.show()
