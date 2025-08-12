rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
import numpy as np
from modules.csvDump import DumpDict

dataArr = {}

shift = 0

attrDict = {'SM_OBE': 84,
'CAT_AI':89,
'HYG_QQQM': 91}

rironDict = {}
for comb, attr in attrDict.items():
    explode = comb.split("_")
    signal = explode[0]
    symbol = explode[1]
    if signal in dataArr:
        signalNpArr = dataArr[signal]
    else:
        signalNpArr = GetNpData(signal)[:-1]
    if symbol in dataArr:
        npArr = dataArr[symbol]
    else:
        npArr = GetNpData(symbol)
    if len(npArr) < 2: continue
    minLength = min(len(signalNpArr),len(npArr),1058)
    signalNpArr = signalNpArr[-minLength:]
    npArr = npArr[-minLength:]
    signalVal = npArr[:,3] / signalNpArr[:,3]
    last = len(npArr)
    avgSignalVal = np.sum(signalVal[last-attr:last])/attr
    tp = signalNpArr[-1][3] * avgSignalVal
    print(signalVal[-1],avgSignalVal)
    if signalVal[-1] < avgSignalVal:
        rironDict[symbol] = tp
        print(symbol, tp)

rironPath = f"{rootPath}/data/Riron.csv"
DumpDict(rironDict, "riron", rironPath)
