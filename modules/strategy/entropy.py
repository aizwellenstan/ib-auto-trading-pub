import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 20
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

import numpy as np
from scipy.stats import entropy
from collections import deque

def generate_signal(prices):
    """
    Generates trading signals based on historical prices.
    
    Parameters:
    prices (np.array): Array of historical prices.
    
    Returns:
    signal (int): 1 for buy, -1 for sell, 0 for no action.
    """
    
    class SimpleMovingAverage:
        def __init__(self, period):
            self.period = period
            self.queue = deque(maxlen=period)
            self.current_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.current_value = np.mean(self.queue)
        
        @property
        def is_ready(self):
            return len(self.queue) == self.period
    
    class EntropyIndicator:
        def __init__(self, period, ma_period):
            self.period = period
            self.ma_period = ma_period
            self.queue = deque(maxlen=period)
            self.ma_queue = deque(maxlen=ma_period)
            self.value = 0
            self.ma_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.calculate_entropy()
                self.ma_queue.append(self.value)

            if len(self.ma_queue) == self.ma_period:
                self.calculate_entropy_ma()
        
        def calculate_entropy(self):
            if len(self.queue) < self.period:
                return
            tmp_arr = np.array(self.queue)
            value, counts = np.unique(tmp_arr, return_counts=True)
            probs = counts / np.sum(counts)
            self.value = entropy(probs, base=2)
        
        def calculate_entropy_ma(self):
            if len(self.ma_queue) < self.ma_period:
                return
            tmp_arr = np.array(self.ma_queue)
            self.ma_value = np.mean(tmp_arr)
    
    # Initialize indicators
    ma_period = 100
    entropy_period = 10
    ma_indicator = SimpleMovingAverage(ma_period)
    entropy_indicator = EntropyIndicator(entropy_period, ma_period)
    
    # Process price data
    for price in prices:
        ma_indicator.update(price)
        entropy_indicator.update(price)
    
    # Check if indicators are ready
    if not ma_indicator.is_ready or len(entropy_indicator.ma_queue) < entropy_indicator.ma_period:
        return 0  # No signal if indicators are not ready
    
    ma_val = ma_indicator.current_value
    en_val = entropy_indicator.value
    en_ma_val = entropy_indicator.ma_value
    
    # Generate trading signal
    current_price = prices[-1]
    if ma_val < current_price and en_val < en_ma_val:
        return 1  # Buy signal
    elif ma_val > current_price and en_val > en_ma_val:
        return -1  # Sell signal
    else:
        return 0  # No action

def Entropy(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    #     sma100 = SmaArr(npArr[:-1][:,3], 100)
    signal = generate_signal(npArr[:-1][:,3][-109:])
    if (
        signal < 0
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        signal > 0
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def MaCross(npArr, tf, tick_val=0.25):
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
            if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
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

def SimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
        sma10 = SmaArr(npArr[:-1][:,3], 10)
        sma25 = SmaArr(npArr[:-1][:,3], 25)
        if (
            (sma10[-2] < sma25[-2] and
            sma10[-1] > sma25[-1]) or
           (sma10[-1] < sma25[-1] and
            npArr[-2][3] > sma25[-1] and
            npArr[-2][3] > sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            (sma10[-2] > sma25[-2] and
            sma10[-1] < sma25[-1]) or
            (sma10[-1] > sma25[-1] and
            npArr[-2][3] < sma25[-1] and
            npArr[-2][3] < sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OriSimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 7
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    sma10 = SmaArr(npArr[:-1][:,3], 11)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaFr(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    sma100 = SmaArr(npArr[:-1][:,3], 100)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    sma10 = SmaArr(npArr[:-1][:,3], 10)
    if (
        npArr[-2][3] > sma100[-1] and
        npArr[-2][3] < sma25[-1] and
        npArr[-2][3] < sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    elif (
        npArr[-2][3] < sma100[-1] and
        npArr[-2][3] > sma25[-1] and
        npArr[-2][3] > sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SimpleMaCrossOver(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    sma10 = SmaArr(npArr[:-1][:,3][-11:], 10)
    sma25 = SmaArr(npArr[:-1][:,3][-26:], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0