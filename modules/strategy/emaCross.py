import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
import pandas_ta as ta
import pandas as pd
from modules.trade.utils import floor_round, ceil_round

def EmaCrossStrategy(df,fast_ema_period=9,slow_ema_period=12):
    df['EMA_Fast'] = df['Close'].ewm(span=fast_ema_period, min_periods=fast_ema_period, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=slow_ema_period, min_periods=slow_ema_period, adjust=False).mean()
    
    # Generate signals
    df['Signal'] = 0  # 0 means no signal
    
    # Buy signal: EMA_Fast crosses above EMA_Slow
    df.loc[(df['EMA_Fast'] > df['EMA_Slow']) & (df['Close'] > df['EMA_Fast']) & (df['Close'].shift() <= df['EMA_Fast'].shift()), 'Signal'] = 1
    
    # Sell signal: EMA_Fast crosses below EMA_Slow
    df.loc[(df['EMA_Fast'] < df['EMA_Slow']) & (df['Close'] < df['EMA_Fast']) & (df['Close'].shift() >= df['EMA_Fast'].shift()), 'Signal'] = 2
    
    df['Time'] = df.index.time
    # df.loc[(df['Time'] >= pd.to_datetime('22:30').time()) & (df['Time'] <= pd.to_datetime('23:59').time()), 'TotalSignal'] = df['Signal']
    start_time = pd.to_datetime('22:30').time()
    end_time = pd.to_datetime('00:30').time()
    df.loc[(df['Time'] >= start_time) | (df['Time'] <= end_time), 'TotalSignal'] = df['Signal']
    # # Combine buy and sell signals into TotSignal column
    # df['TotalSignal'] = df['Signal']
    
    # Remove temporary columns
    # df.drop(['EMA_Fast', 'EMA_Slow', 'Signal'], axis=1, inplace=True)
    
    return df

TP_VAL = 1.6
def GetEmaCrossStrategy(npArr, tick_val=0.25):
    # npArr = npArr[-16:]
    df = pd.DataFrame(npArr, columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date'])
    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
    df['Date'] = pd.to_datetime(df.Date)
    df.set_index(df.Date, inplace=True)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df = EmaCrossStrategy(df)
    signal = df['TotalSignal'].iloc[-1]
    if signal == 2: signal = 1
    elif signal == 1: signal = -1
    
    op = 0
    sl = 0
    tp = 0
    if signal != 0:
        atr = ta.atr(df.High, df.Low, df.Close, length=7)[-1]
        slAtr =  atr * 1.2
        op = npArr[-2][3]
        if signal == 1:
            sl = ceil_round(op - slAtr, tick_val)
            tp = ceil_round(op + slAtr * TP_VAL, tick_val)
        elif signal == -1:
            sl = floor_round(op + slAtr, tick_val)
            tp = floor_round(op - slAtr * TP_VAL, tick_val)
    return signal, op, sl, tp