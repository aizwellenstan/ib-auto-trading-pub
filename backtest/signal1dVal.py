# rootPath = '..'
# import sys
# sys.path.append(rootPath)
# from modules.movingAverage import SmaArr
# from modules.data import GetNpData
# import numpy as np
# from numba import range, njit
# from modules.aiztradingview import GetClose
# import pickle

# dataPath = "./pickle/dataArr.p"
# dataArr = {}
# closeDict = GetClose()

# update = False
# if update:
#     for symbol, close in closeDict.items():
#         npArr = GetNpData(symbol)
#         if len(npArr) < 1: continue
#         dataArr[symbol] = npArr
#         print(symbol)

#     pickle.dump(dataArr, open(dataPath, "wb"))
#     print("pickle dump finished")
# else:
#     # import gc
#     output = open(dataPath, "rb")
#     # gc.disable()
#     dataArr = pickle.load(output)
#     output.close()
#     # gc.enable()

# # @njit
# def GetGainPerDay(lenSignal, signalNpArr,npArr,gainVal):
#     lenNpArr = len(npArr)
#     minLen = min(lenSignal, lenNpArr)

#     newSignalArr = signalNpArr[-minLen:]
#     npArr = npArr[-minLen:]

#     balance = 1
#     for i in range(0, len(npArr)):
#         if newSignalArr[i-1][3] > newSignalArr[i-1][0]*gainVal:
#             op = npArr[i][0]
#             close = npArr[i][3]
#             if op < 0.01: return 0
#             gain = close/op
#             balance *= gain
#     if balance < 1: return 0
#     gainPerDay = balance/minLen
#     return gainPerDay

# symbol = 'CAT'
# signalNpArr = dataArr[symbol]
# lenSignal = len(signalNpArr)

# symbol = "HROW"
# npArr = dataArr[symbol]
# maxGainPerDay = 0
# maxGainVal = 0
# gainVal = 1
# while gainVal < 2:
#     gainPerDay = GetGainPerDay(lenSignal,signalNpArr,npArr, gainVal)
#     if gainPerDay > maxGainPerDay:
#         maxGainPerDay = gainPerDay
#         maxGainVal = gainVal
#         print(maxGainPerDay, maxGainVal)
#     gainVal += 0.0001

# # 'HROW': 1058342.4689861748 QQQ