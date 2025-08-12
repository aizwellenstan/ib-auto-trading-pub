import numpy as np

def Msd(closeArr, short_window=23, long_window=50):
    # Calculate moving averages
    short_ma = np.convolve(closeArr, np.ones(short_window)/short_window, mode='valid')
    long_ma = np.convolve(closeArr, np.ones(long_window)/long_window, mode='valid')

    # Make sure short_ma and long_ma have the same length
    min_len = min(len(short_ma), len(long_ma))
    short_ma = short_ma[-min_len:]
    long_ma = long_ma[-min_len:]

    # Calculate signals
    signal = np.where(short_ma > long_ma, 1, -1)

    # Calculate Market Sentiment Difference (MSD)
    msd = np.convolve(signal, np.ones(short_window)/short_window, mode='valid')

    # Generate trading signals based on MSD
    msd_mean = np.mean(msd)
    msd_signal = np.where(msd > msd_mean, 1, -1)

    length_diff = len(closeArr) - len(msd_signal)
    if length_diff > 0:
        msd_signal = np.pad(msd_signal, (length_diff, 0), 'constant', constant_values=0)

    return msd_signal