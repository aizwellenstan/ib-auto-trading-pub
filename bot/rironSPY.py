# rootPath = '..'
# import sys
# sys.path.append(rootPath)
# from modules.data import GetNpData
# import numpy as np
# from modules.csvDump import DumpDict

# orirginQQQArr = GetNpData('SPY')

# shift = 0

# attrDict = {'KOLD': 5}

# rironDict = {}
# for symbol, attr in attrDict.items():
#     npArr = GetNpData(symbol)
#     if len(npArr) < 2: continue
#     minLength = min(len(orirginQQQArr),len(npArr))
#     qqqArr = orirginQQQArr[-minLength:]
#     npArr = npArr[-minLength:]
#     qqqVal = npArr[:,3] / qqqArr[:,3]
#     last = len(npArr)-shift
#     avgQQQVal = np.sum(qqqVal[last-attr:last])/attr
#     tp = qqqArr[-1-shift][3] * avgQQQVal
#     if qqqVal[-1-shift] < avgQQQVal:
#         rironDict[symbol] = tp
#         print(symbol, tp)

# rironPath = f"{rootPath}/data/RironSPY.csv"
# DumpDict(rironDict, "rironSPY", rironPath)
