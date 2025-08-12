rootPath = "..";import sys;sys.path.append(rootPath)
import numpy as np
import pylab as pl
from numpy import fft
from datetime import datetime
from pandas_datareader import data as pdr
from modules.data import GetDataWithVolumeDate

def fourierExtrapolation(x, n_predict):
    n = x.size
    n_harm = 50
    t = np.arange(0, n)
    p = np.polyfit(t, x, 1)
    x_notrend = x - p[0] * t
    x_freqdom = fft.fft(x_notrend)
    f = fft.fftfreq(n)
    indexes = list(range(n))
    indexes.sort(key=lambda i: np.absolute(f[i]))

    #indexes.sort(key=lambda i: np.absolute(x_freqdom[i]))
    #indexes.reverse()
 
    t = np.arange(0, n + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[:1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n
        phase = np.angle(x_freqdom[i])
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    return restored_sig + p[0] * t
    

npArr = GetDataWithVolumeDate("9101")
hist = npArr[:,3]
train = hist[:225]

n_predict = len(hist) - len(train)
extrapolation = fourierExtrapolation(train, n_predict)
pl.plot(np.arange(0, hist.size), hist, 'b', label = 'Data', linewidth = 3)
pl.plot(np.arange(0, train.size), train, 'c', label = 'Train', linewidth = 2)
pl.plot(np.arange(0, extrapolation.size), extrapolation, 'r', label = 'Predict', linewidth = 1)

pl.legend()
pl.show()