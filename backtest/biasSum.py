rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP, GetGain
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict

gainPath = f"{rootPath}/data/gainDict.csv"
gainDict = LoadDict(gainPath, "gain")

closeDict = GetClose()
closeJPDict = GetCloseJP()
gainable = GetGain()
attrDict = GetAttrJP("ADR")

def Backtest():
    gainUS = np.empty(0)
    gainJP = np.empty(0)
    attrList = []
    for symbol, gain in gainDict.items():
        if gain < 29.6796: continue
        if symbol in closeDict:
            gainUS = np.append(gainUS, gain)
        else:
            gainJP = np.append(gainJP, gain)
    avgGainUS = sum(gainUS) / len(gainUS)
    avgGainJP = sum(gainJP) / len(gainJP)
    print(avgGainUS, avgGainJP)
Backtest()