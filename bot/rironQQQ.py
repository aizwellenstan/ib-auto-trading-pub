rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
import numpy as np
# from modules.aiztradingview import GetTradable
from modules.csvDump import DumpDict

# closeDict = GetTradable()
# print(len(closeDict))
orirginQQQArr = GetNpData('QQQ')

shift = 0

attrDict = {
'TSLA': 2, 'ENPH': 90,
'AAPL': 53, 'FERG': 99, 'SPXL': 19, 'NVDA': 2
# 'LIN': 21, 'NFLX': 14, 'GOOGL': 37,
# 'ARGX': 62, 'SPUU': 85, 'MSFT': 9,
# 'FNGU': 3, 'XLK': 3, 'SAP': 4, 'XLY': 99, 'SQ': 89, 'MDY': 31, 'URTY': 2, 'VCR': 81, 'SPY': 31, 'TNA': 2, 'DIA': 61, 'IJH': 31, 'IVV': 19, 'IWM': 28, 'VOO': 31, 'GLD': 5, 'DIS': 3, 'MIDU': 75, 'IVOO': 31, 'AMZN': 2
}

rironDict = {}
for symbol, attr in attrDict.items():
    npArr = GetNpData(symbol)
    if len(npArr) < 2: continue
    minLength = min(len(orirginQQQArr),len(npArr))
    qqqArr = orirginQQQArr[-minLength:]
    npArr = npArr[-minLength:]
    qqqVal = npArr[:,3] / qqqArr[:,3]
    last = len(npArr)-shift
    avgQQQVal = np.sum(qqqVal[last-attr:last])/attr
    tp = qqqArr[-1-shift][3] * avgQQQVal
    if qqqVal[-1-shift] < avgQQQVal:
        rironDict[symbol] = tp
        print(symbol, tp)

rironPath = f"{rootPath}/data/RironQQQ.csv"
DumpDict(rironDict, "rironQQQ", rironPath)
