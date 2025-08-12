import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-3:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-3:][:,1])
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def calculate_roc(close_prices, window_size=1):
    roc = np.diff(close_prices, n=window_size) / close_prices[:-window_size]
    return roc

def train_hmm(roc_data, n_components=3):
    model = hmm.GaussianHMM(n_components=n_components, n_iter=100, random_state=100)
    scaler = StandardScaler()
    
    # Prepare data for HMM
    roc_data = roc_data.reshape(-1, 1)
    scaled_data = scaler.fit_transform(roc_data)
    
    model.fit(scaled_data)
    return model, scaler

def generate_signals(model, scaler, latest_roc):
    scaled_roc = scaler.transform(latest_roc.reshape(-1, 1))
    probs = model.predict_proba(scaled_roc)
    return probs

def generate_trading_signal(probs, threshold=0.5):
    state_probs = probs[-1]
    if state_probs[2] > threshold:
        return 1
    elif state_probs[0] > threshold:
        return -1
    else:
        return 0

model = 0
scaler = 0
def roc_model(prices, IS_TRAIN=False):
    global model, scaler, c
    roc = calculate_roc(prices)
    if len(roc) < 1: return 0
    if model == 0 or IS_TRAIN:
        model, scaler = train_hmm(roc, n_components=3)
    latest_roc = roc[-1]
    probs = generate_signals(model, scaler, np.array([latest_roc]))
    signal = generate_trading_signal(probs)
    return signal

def Roc(npArr, tf, tick_val=0.25, IS_TRAIN=False):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    if npArr[-2][4] < npArr[-3][4] / 2:
        signal = roc_model(npArr[:-1][:,3], 1)
    else:
        signal = roc_model(npArr[:-1][:,3], 0)
    sma100 = SmaArr(npArr[:-1][:,3], 50)
    if (
        signal > 0 and
        npArr[-2][3] > sma100[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        signal < 0 and
        npArr[-2][3] < sma100[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

# 15 mins 20 mins
def MaCrossHTF(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0