import numpy as np
import pandas as pd

def GetAtrTs(npArr, windows=3, ATRMultiplier=2.5):
    high = npArr[:,1]
    low = npArr[:,2]
    close = npArr[:,3]
    
    high_low_diff = high - low
    high_close_diff = np.abs(high - np.roll(close, 1))
    high_close_diff[0] = np.nan
    
    low_close_diff = np.abs(low - np.roll(close, 1))
    low_close_diff[0] = np.nan
    
    tr = np.maximum(high_low_diff, np.maximum(high_close_diff, low_close_diff))
    
    # ATR
    atrs = np.convolve(tr, np.ones(windows)/windows, mode='valid')
    atr = np.concatenate((np.full(windows-1, np.nan), atrs))
    
    # Calculate Stop and initialize ATRTrailingStop
    stop = ATRMultiplier * atr
    atr_ts = np.full(close.shape[0], np.nan)
    atr_ts[0] = 0
    count = 0
    for i in range(1, len(close)):
        prev_atr_ts = atr_ts[i-1]
        if close[i] > prev_atr_ts and close[i-1] > prev_atr_ts:
            atr_ts[i] = max(prev_atr_ts, close[i] - stop[i])
        elif close[i] < prev_atr_ts and close[i-1] < prev_atr_ts:
            atr_ts[i] = min(prev_atr_ts, close[i] + stop[i])
        elif close[i] > prev_atr_ts:
            atr_ts[i] = close[i] - stop[i]
        elif close[i] < prev_atr_ts:
            atr_ts[i] = close[i] + stop[i]
            
        if close[i] == prev_atr_ts:
            atr_ts[i] = close[i] - stop[i]
            count+=1 
    
    position = np.where(close > atr_ts, 1, 0)
    npArr = np.c_[npArr, position, atr_ts]
    return npArr

def GetAtrTsSqueeze(npArr, windows=3, ATRMultiplier=2.5):
    high = npArr[:,1]
    low = npArr[:,2]
    close = npArr[:,3]
    
    high_low_diff = high - low
    high_close_diff = np.abs(high - np.roll(close, 1))
    high_close_diff[0] = np.nan
    
    low_close_diff = np.abs(low - np.roll(close, 1))
    low_close_diff[0] = np.nan
    
    tr = np.maximum(high_low_diff, np.maximum(high_close_diff, low_close_diff))
    
    # ATR
    atrs = np.convolve(tr, np.ones(windows)/windows, mode='valid')
    atr = np.concatenate((np.full(windows-1, np.nan), atrs))
    
    # Calculate Stop and initialize ATRTrailingStop
    stop = ATRMultiplier * atr
    atr_ts = np.full(close.shape[0], np.nan)
    atr_ts[0] = 0
    count = 0
    for i in range(1, len(close)):
        prev_atr_ts = atr_ts[i-1]
        if close[i] > prev_atr_ts and close[i-1] > prev_atr_ts:
            atr_ts[i] = max(prev_atr_ts, close[i] - stop[i])
        elif close[i] < prev_atr_ts and close[i-1] < prev_atr_ts:
            atr_ts[i] = min(prev_atr_ts, close[i] + stop[i])
        elif close[i] > prev_atr_ts:
            atr_ts[i] = close[i] - stop[i]
        elif close[i] < prev_atr_ts:
            atr_ts[i] = close[i] + stop[i]
            
        if close[i] == prev_atr_ts:
            atr_ts[i] = close[i] - stop[i]
            count+=1 
    
    position = np.where(close > atr_ts, 1, 0)
    

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
    npArr = np.c_[npArr, position, atr_ts, squeeze]
    return npArr