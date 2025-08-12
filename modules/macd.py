import talib
import numpy as np

def Macd(closeArr):
    closeArr = closeArr.astype(np.float)
    macdBase, macdSignal, macdHist = talib.MACD(closeArr)
    return [macdBase, macdSignal]

def MacdHistorical(closeArr):
    # closeArr = closeArr.astype(np.float)
    macd, macdSignal, macdHist = talib.MACD(closeArr)
    return macdHist

# def macd(c, n1, n2, ns):
#     ema_short = c.ewm(span=n1,adjust=False).mean()
#     ema_long = c.ewm(span=n2,adjust=False).mean()
#     macd = ema_short - ema_long
#     signal = macd.ewm(span=ns,adjust=False).mean()
#     histogram = macd - signal
#     histogramplus = histogram.where(histogram > 0, 0)
#     histogramminus = histogram.where(histogram < 0, 0)
#     return macd,signal,histogram,histogramplus,histogramminus