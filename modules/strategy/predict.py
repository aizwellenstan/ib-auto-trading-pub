import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr, EmaArr
from modules.entropy import Entropy
from modules.strategy.sweep import GetSweep
import numpy as np

import numpy as np
from collections import Counter

def get_signal(sequence):
    latest_value = sequence[-1]
    
    # Count occurrences of each number
    count = Counter(sequence)
    
    # Determine how many times the latest value has been repeated
    latest_count = count[latest_value]
    
    # Calculate larger and smaller counts
    larger_count = sum(1 for x in sequence if x > latest_value)
    smaller_count = sum(1 for x in sequence if x < latest_value)

    # Basic prediction based on the counts
    if larger_count > smaller_count:
        prediction = 1
    elif smaller_count > larger_count:
        prediction = -1
    else:
        prediction = 0
    
    # print({
    #     "latest_value": latest_value,
    #     "latest_count": latest_count,
    #     "larger_count": larger_count,
    #     "smaller_count": smaller_count,
    #     "prediction": prediction
    # })

    return prediction

def Predict(npArr, tf, tick_val=0.25):
    if len(npArr) < 43 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    signal = get_signal(npArr[:-2][:,3][-40:])
    rr = 2.4
    if (
        npArr[-2][1] > npArr[-3][1] and
        signal > 0
    ):
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if tp - op > (op - sl) * rr:
            signal = 1
            return signal, op, sl, tp
    elif (
        npArr[-2][2] < npArr[-3][2] and
        signal < 0
    ):
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if op - tp > (sl - op) * rr:
            signal = -1
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
