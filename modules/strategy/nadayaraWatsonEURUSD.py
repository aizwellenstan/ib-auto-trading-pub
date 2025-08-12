import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.movingAverage import SmaArr, EmaArr
from modules.atr import ATR
from statsmodels.nonparametric.kernel_regression import KernelReg
import pandas as pd

def GetOPSLTP(npArr, signal, tf, tick_val, atr):
    # TP_VAL = 5
    # if tf in ['20 mins']: TP_VAL = 4
    # elif tf in ['30 mins']: TP_VAL = 2
    # elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = op - atr * 2.5
        tp = op + atr * 4.5
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = op + atr * 2.5
        tp = op - atr * 4.5
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def getBands(npArr):
    open_idx, high_idx, low_idx, close_idx = 0, 1, 2, 3
    
    # Extract columns from npArr
    close = npArr[:, close_idx]
    index = np.arange(len(npArr))  # Simulate DataFrame index

    # Fit the Kernel Regression model
    model = KernelReg(endog=close, exog=index, var_type='c', reg_type='lc', bw=[3])
    fitted_values, _ = model.fit()

    # Calculate residuals
    residuals = close - fitted_values

    # Calculate standard deviation of residuals
    std_dev = 2. * np.std(residuals)

    # Calculate upper and lower envelopes
    upper_envelope = fitted_values + std_dev
    lower_envelope = fitted_values - std_dev

    # Create the result array
    result = np.vstack((close, lower_envelope, upper_envelope)).T

    return result

def Bands(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    bands = getBands(npArr[:-1][-15:])
    sma = SmaArr(npArr[:,3][:-1], 50)
    emaS = EmaArr(npArr[:,3][:-1], 50)
    emaF = EmaArr(npArr[:,3][:-1], 40)
    atrPeriod = 8
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 7)
    if (
        emaF[-1] > emaS[-1] and
        npArr[-2][3] <= bands[-1][1] and
        npArr[-2][3] < sma[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val, atr)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    elif (
        emaF[-1] < emaS[-1] and
        npArr[-2][3] >= bands[-1][2] and
        npArr[-2][3] > sma[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val, atr)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, bands[-1][1]
    return 0, npArr[-1][0], 0, 0
