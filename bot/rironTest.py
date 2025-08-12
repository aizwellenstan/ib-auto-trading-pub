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
'HYG_QQQM': 91,
'QQQ_TSLA': 2, 
'QQQ_AAPL': 53, 'QQQ_NVDA': 2, 
'QQQ_GOOG': 37, 'QQQ_GOOGL': 37,
'QQQ_MSFT': 9,
'QQQ_FNGU': 3, 'QQQ_XLK': 3, 'QQQ_SAP': 4, 'QQQ_XLY': 99, 
'QQQ_SQ': 89, 'QQQ_MDY': 31, 'QQQ_VCR': 81, 
'QQQ_SPY': 31, 'QQQ_TNA': 2, 'QQQ_DIA': 61, 'QQQ_IJH': 31, 
'QQQ_IVV': 19, 'QQQ_IWM': 28, 'QQQ_VOO': 31, 'QQQ_GLD': 5, 
'QQQ_DIS': 3, 'QQQ_MIDU': 75, 'QQQ_IVOO': 31, 'QQQ_AMZN': 2}

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

rironPath = f"{rootPath}/data/RironTest.csv"
DumpDict(rironDict, "riron", rironPath)
