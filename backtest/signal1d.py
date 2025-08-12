# rootPath = '..'
# import sys
# sys.path.append(rootPath)
# from modules.movingAverage import SmaArr
# from modules.data import GetNpData
# import numpy as np
# from numba import range, njit
# from modules.aiztradingview import GetTradable
# import pickle

# dataPath = "./pickle/dataArr.p"
# dataArr = {}
# closeDict = GetTradable()

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
# def GetGainPerDay(lenSignal, signalNpArr,npArr):
#     lenNpArr = len(npArr)
#     minLen = min(lenSignal, lenNpArr)

#     newSignalArr = signalNpArr[-minLen:]
#     npArr = npArr[-minLen:]

#     balance = 1
#     for i in range(0, len(npArr)):
#         if newSignalArr[i-1][3] > newSignalArr[i-1-50][0]:
#             op = npArr[i][0]
#             close = npArr[i][3]
#             if op < 0.01: return 0
#             gain = close/op
#             balance *= gain
#     if balance < 1: return 0
#     gainPerDay = balance/minLen
#     return gainPerDay

# symbol = 'HYG'
# signalNpArr = dataArr[symbol]
# lenSignal = len(signalNpArr)

# gainPerDayDict = {}
# for symbol, close in closeDict.items():
#     if symbol not in dataArr: continue
#     npArr = dataArr[symbol]
#     gainPerDay = GetGainPerDay(lenSignal,signalNpArr,npArr)
#     if gainPerDay == 0: continue
#     gainPerDayDict[symbol] = gainPerDay

# gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
# # print(gainPerDayDict)

# newGainPerDayDict = {}
# count = 0
# for symbol, gainPerDay in gainPerDayDict.items():
#     newGainPerDayDict[symbol] = gainPerDay
#     count += 1
#     if count > 100: break
# print(newGainPerDayDict)

# # 'HROW': 1058342.4689861748 QQQ