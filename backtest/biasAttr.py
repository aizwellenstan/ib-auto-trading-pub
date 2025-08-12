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
    attrList = []
    for symbol, gain in gainDict.items():
        if symbol in attrDict:
            attrList.append(attrDict[symbol]) 
    
    maxAvgGainUS = 0
    maxAttrLimit = 0
    # gainJP = np.empty(0)
    attrList.sort()
    for attrLimit in attrList:
        gainUS = np.empty(0)
        for symbol, gain in gainDict.items():
            if symbol in closeJPDict:
                # if closeDict[symbol] < 1.02: continue
                if symbol not in attrDict:continue
                # if symbol not in gainable: continue
                if attrDict[symbol] < attrLimit: continue
                # if attrDict[symbol] > attrLimit: continue
                # if gain> 0.00001: gain = 1
                # else: gain = -1
                gainUS = np.append(gainUS,gain)
                
                # gainJP = np.append(gainJP,gain)
        avgGainUS = sum(gainUS)/len(gainUS)
        if avgGainUS > maxAvgGainUS:
            maxAvgGainUS = avgGainUS
            maxAttrLimit = attrLimit
            print(maxAvgGainUS,maxAttrLimit)
    # avgGainJP = sum(gainJP)/len(gainJP)
  

Backtest()