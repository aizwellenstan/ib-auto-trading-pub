import pandas as pd
import numpy as np

def GetSqueeze(npArr):
    period = 25
    df = pd.DataFrame(npArr, columns = ['op', 'high', 'low', 'close', 'vol', 'da'])
    df['sma'] = df['close'].rolling(window=period).mean()
    df['TR'] = abs(df['high'] - df['low'])
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

    df['stddev'] = df['close'].rolling(window=period).std()
    df['lower_band'] = df['sma'] - (2 * df['stddev'])
    df['upper_band'] = df['sma'] + (2 * df['stddev'])

    def in_squeeze(df):
        if df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']:
            return 1
        return 0
    squeeze = df.apply(in_squeeze, axis=1)
    npArr = np.c_[npArr, squeeze]
    return npArr
