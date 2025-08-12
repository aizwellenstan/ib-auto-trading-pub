import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
import pandas_ta as ta
import pandas as pd
from modules.trade.utils import floor_round, ceil_round
from modules.atr import ATR
from modules.vwap import Vwap
from modules.movingAverage import SmaArr, EmaArr
from modules.lorentizianClassification import Signal
from modules.kernelema import kernelema
from modules.permutationEntropy import permutation_entropy

def VwapStrategy(df):
    # Calculate VWAP, RSI, and Bollinger Bands
    df = df.assign(VWAP= ta.vwap(df.High, df.Low, df.Close, df.Volume))
    df = df.assign(RSI= ta.rsi(df.Close, length=16))
    bbands = ta.bbands(df.Close, length=14, std=2.0)
    df = df.join(bbands)
    df = df[df['Volume'] >= 1]

    # Generate VWAP Signal
    backcandles = 15
    VWAPsignal = np.zeros(len(df))

    for row in range(backcandles, len(df)):
        upt = 1
        dnt = 1
        for i in range(row - backcandles, row + 1):
            if max(df.Open[i], df.Close[i]) >= df.VWAP[i]:
                dnt = 0
            if min(df.Open[i], df.Close[i]) <= df.VWAP[i]:
                upt = 0
        if upt == 1 and dnt == 1:
            VWAPsignal[row] = 3
        elif upt == 1:
            VWAPsignal[row] = 2
        elif dnt == 1:
            VWAPsignal[row] = 1

    df['VWAPSignal'] = VWAPsignal

    # Define TotalSignal function and apply it
    def TotalSignal(l):
        if (df.VWAPSignal[l] == 2
                and df.Close[l] <= df['BBL_14_2.0'][l]
                and df.RSI[l] < 45):
            return 2
        if (df.VWAPSignal[l] == 1
                and df.Close[l] >= df['BBU_14_2.0'][l]
                and df.RSI[l] > 55):
            return 1
        return 0

    TotSignal = np.zeros(len(df))

    for row in range(backcandles, len(df)):
        TotSignal[row] = TotalSignal(row)

    df['TotalSignal'] = TotSignal
    return df

TP_VAL = 1.5
def GetVwapStrategy(npArr, tf, tick_val=0.25):
    if len(npArr) < 192: return 0, 0, 0, 0
    df = pd.DataFrame(npArr, columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date'])
    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Date']]
    df['Date'] = pd.to_datetime(df.Date)
    df.set_index(df.Date, inplace=True)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df = VwapStrategy(df)
    if len(df['TotalSignal']) < 1: return 0, 0, 0, 0
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

def GetOPSLTP(npArr, signal, tf, tick_val):
    # TP_VAL = 1.333333333
    TP_VAL = 2
    if signal > 0:
        op = npArr[-1][0]
        # sl = max(np.min(npArr[-2:][:,2]), (cus_sl + op)/2)
        sl = np.min(npArr[-2:][:,2])
        sl = floor_round(sl, tick_val)
        tp = op + (op-sl) * TP_VAL
        # sl = np.min(npArr[-4:][:,2]) - tick_val * 140
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        # sl = min(np.max(npArr[-2:][:,1]), (cus_sl + op)/2)
        sl = np.max(npArr[-2:][:,1])
        sl = ceil_round(sl, tick_val)
        tp = op - (sl-op) * TP_VAL
        # sl = np.max(npArr[-4:][:,1]) + tick_val * 140
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def Atr(data, period):
    close_p, high_p, low_p = data[:, 3], data[:, 1], data[:, 2]
    tr = np.maximum(high_p - low_p, np.maximum(np.abs(high_p - np.roll(close_p, 1)), np.abs(low_p - np.roll(close_p, 1))))
    atr = np.convolve(tr, np.ones(period)/period, 'valid')
    return atr
    # recent_atr = np.convolve(atr, np.ones(1)/1, 'valid')
    # historical_atr = np.convolve(atr, np.ones(10)/10, 'valid')
    # historical_atr = np.concatenate((np.full(9, np.nan), historical_atr))
    
    # volatility_filter = recent_atr > historical_atr
    # if not np.all(high_p - low_p): return False
    # regime_filter = np.abs(np.diff(close_p, prepend=close_p[0])) / (high_p - low_p) >= 0.1
    # if len(regime_filter) < 1: return False
    # return regime_filter[-1]

def calculate_rsi(close_prices, window=14):
    delta = np.diff(close_prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.convolve(gain, np.ones((window,))/window, mode='valid')
    avg_loss = np.convolve(loss, np.ones((window,))/window, mode='valid')
    avg_loss = np.convolve(loss, np.ones((window,))/window, mode='valid')
    if not np.all(avg_loss): return []

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the RSI array to match the length of the input
    rsi = np.concatenate([np.full(window-1, np.nan), rsi])
    return rsi

def FourBarReversal(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # # atrPeriod = 100
    # atrPeriod = 200
    # period = 50
    # # IS_FILTER_PASSED = filter(npArr[:-1][-40:], 20)
    # # if not IS_FILTER_PASSED: return 0, npArr[-1][0], 0, 0
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    #     sma50 = SmaArr(npArr[:-1][:,3][-51:], 50)
    #     vwapPeriod = 50
    #     npArrC = npArr[:-1]
    #     npArrC = npArrC[npArrC[:, 4] != 0]
    #     vwap = Vwap(npArrC[:,4][-vwapPeriod:],npArrC[:,1][-vwapPeriod:],npArrC[:,2][-vwapPeriod:])
    #     ema = EmaArr(npArr[:-1][:,3][-9:], 8)
    if (
        # npArr[-1][1] < npArr[-5][2] and
        # npArr[-1][1] > npArr[-4][2] and
        # npArr[-3][2] < npArr[-4][2] and
        # npArr[-2][2] < npArr[-3][2]
        npArr[-2][1] < npArr[-6][2] and
        npArr[-2][1] > npArr[-5][2] and
        npArr[-4][2] < npArr[-5][2] and
        npArr[-3][2] < npArr[-4][2] and
        npArr[-2][1] > npArr[-3][1]

        
        # npArr[-2][3] > sma50[-1] and
        # ema[-4] < vwap[-4] and
        # ema[-3] < vwap[-3] and
        # ema[-2] < vwap[-2] and
        # ema[-1] > vwap[-1] and
        # npArr[-2][3] > vwap[-1] and
        # npArr[-2][3] > ema[-1] and
        # npArr[-2][3] > npArr[-2][0]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] > sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        # sl = floor_round(vwap[-1], tick_val)
        return signal, op, sl, tp
    elif (
        npArr[-2][2] > npArr[-6][1] and
        npArr[-2][2] < npArr[-5][1] and
        npArr[-4][1] > npArr[-5][1] and
        npArr[-3][1] > npArr[-4][1] and
        npArr[-2][2] < npArr[-3][2]
        
        # npArr[-1][2] > npArr[-5][1] and
        # npArr[-1][2] < npArr[-4][1] and
        # npArr[-3][1] > npArr[-4][1] and
        # npArr[-2][1] > npArr[-3][1]
        # npArr[-2][3] < sma50[-1] and
        # ema[-4] > vwap[-4] and
        # ema[-3] > vwap[-3] and
        # ema[-2] > vwap[-2] and
        # ema[-1] < vwap[-1] and
        # npArr[-2][3] < vwap[-1] and
        # npArr[-2][3] < ema[-1] and
        # npArr[-2][3] < npArr[-2][0]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] > sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        # sl = ceil_round(vwap[-1], tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0