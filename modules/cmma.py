import pandas as pd
import pandas_ta as ta

def Cmma(npArr, lookback=24, atr_lookback=168):
    ohlc = pd.DataFrame(npArr, columns = ['open','high','low', 'close', 'volume', 'date'])
    atr = ta.atr(ohlc['high'], ohlc['low'], ohlc['close'], atr_lookback)
    ma = ohlc['close'].rolling(lookback).mean()
    ind = (ohlc['close'] - ma) / (atr * lookback ** 0.5)
    return ind