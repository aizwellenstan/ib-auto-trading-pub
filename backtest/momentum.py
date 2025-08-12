rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
from modules.aiztradingview import GetAttr, GetPerformance, GetClose, GetHistoricalGain
from numba import njit
from numba import types
from numba.typed import Dict
from modules.movingAverage import SmaArr
from modules.data import GetDividend
import numpy as np

gainList = GetHistoricalGain()

print(gainList)

options = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV',
    'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    'V','CAT','MRNA','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    'VIX',
    'COIN'
]

# # performanceList = GetPerformance()

# newMarCapDict = Dict.empty(key_type=types.unicode_type,value_type=types.uint64)
# for symbol, v in marketCapDict.items():
#     if symbol in options:
#         # if symbol not in performanceList: continue
#         newMarCapDict[np.unicode_(symbol)] = np.uint64(marketCapDict[symbol])
# marketCapDict = newMarCapDict

# tradeList = []
# for symbol, v in marketCapDict.items():
#     if v < 40370174: continue
#     tradeList.append(symbol)
# print(tradeList)

backtestLength = 252 * 4

closeDict = GetClose()

import pickle
# dataDict = {}
# for symbol, v in closeDict.items():
#     print(symbol)
#     npArr = GetNpData(symbol)
#     if len(npArr) < backtestLength: continue
#     dataDict[symbol] = npArr


picklePath = "./pickle/pro/compressed/dataDictAll.p"
# pickle.dump(dataDict, open(picklePath, "wb"))
# print("pickle dump finished")



import gc
output = open(picklePath, "rb")
gc.disable()
dataDict = pickle.load(output)
output.close()
gc.enable()


# newDataDict = {}
# for k,v in dataDict.items():
#     v = np.c_[v[:,0],v[:,1],v[:,2],v[:,3]]
#     newDataDict[np.unicode_(k)]=np.float32(v)
# dataDict = newDataDict
# picklePath = "./pickle/pro/compressed/dataDictAll.p"
# pickle.dump(dataDict, open(picklePath, "wb"))

newDataDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])
# print("pickle dump finished")

# optionList = []
# import os
# import pandas as pd
# optionPath = f'{rootPath}/data/Options.csv'
# if os.path.exists(optionPath):
#     df = pd.read_csv(optionPath)
#     optionList = list(df.Symbol.values)

for k,v in dataDict.items():
    if len(v) < backtestLength: continue
    if k not in gainList:continue
    # if k not in optionList: continue
    # if k in options:
    closeArr = v[:,3]
    gain = v[:,3]/v[:,0]
    if np.isinf(gain).any(): 
        print(k)
        continue
    v = np.c_[v, gain]
    newDataDict[np.unicode_(k)]=np.float32(v)
dataDict = newDataDict

newMarCapDict = Dict.empty(key_type=types.unicode_type,value_type=types.uint64)
marketCapDict = GetAttr("market_cap_basic")
for symbol, v in marketCapDict.items():
    if symbol not in dataDict: continue
    newMarCapDict[np.unicode_(symbol)] = np.uint64(marketCapDict[symbol])
marketCapDict = newMarCapDict
marketCapList = np.uint64(list(marketCapDict.values()))
marketCapList.sort()
marketCapList = marketCapList[::-1]

newAdrDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32)
adrDict = GetAttr("number_of_shareholders")
for symbol, v in adrDict.items():
    if symbol not in dataDict: continue
    newAdrDict[np.unicode_(symbol)] = np.float32(adrDict[symbol])
adrDict = newAdrDict
adrList = np.float32(list(adrDict.values()))
adrList.sort()
adrList = adrList[::-1]

# @njit
def GetDailyGain(gainList):
    if len(gainList) < 1: return 1
    vol = 1 / len(gainList)
    dailyGain = 0
    for gain in gainList:
        dailyGain += vol * gain
    return dailyGain

# @njit
def GetLowerBand(npArr, period, dev):
    closeArr = npArr[:,3]
    closeArr = closeArr[-period:]
    stddev = np.std(closeArr)
    mean = np.mean(closeArr)
    lowerBand = mean-(dev * stddev)
    return lowerBand

# @njit
def GetUpperBand(npArr, period, dev):
    closeArr = npArr[:,3]
    closeArr = closeArr[-period:]
    stddev = np.std(closeArr)
    mean = np.mean(closeArr)
    lowerBand = mean+(dev * stddev)
    return lowerBand

# @njit
def Backtest(dataDict, period, retraceVal):
    totalGain = 1
    for i in range(10, backtestLength):
        gainList = np.empty(0)
        maxMomentum = 2
        gain = 1
        for symbol, npArr in dataDict.items():
            momentum = npArr[i-1][3]/npArr[i-1][0]
            # period = 141
            # dev = 1.1
            # lowerBand = GetLowerBand(npArr, period, dev)
            if (
                momentum < maxMomentum and
                npArr[i][0] < npArr[i-1][2] and
                npArr[i-1][3] / npArr[i-6][3] > 0.49 and
                npArr[i-1][3] / npArr[i-5][3] > 0.58 and
                npArr[i-1][3] / npArr[i-4][3] > 0.55 and
                npArr[i-1][3] / npArr[i-3][3] > 0.56 and
                npArr[i-1][3] / npArr[i-2][3] > 0.69 and
                npArr[i-1][3] / npArr[i-3][3] < 1.02 and
                npArr[i-1][3] / npArr[i-2][3] < 1.71
            ):
                maxMomentum = momentum
                gain = npArr[i][4]
                # gainList = np.append(gainList, gain)
        totalGain *= gain
        # dailyGain = GetDailyGain(gainList)
        # totalGain *= dailyGain
    return totalGain

emptyDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])
# # @njit
# def main(dataDict):
#     maxTotalGain = 0
#     minPeriod = 0
#     period = 1
#     while period < 500:
#         totalGain = Backtest(dataDict, period)
#         if totalGain > maxTotalGain:
#             maxTotalGain = totalGain
#             minPeriod = period
        
#         print(maxTotalGain,minPeriod)
#         period += 1
# main(dataDict)

# @njit
def main(dataDict, emptyDict, marketCapList, marketCapDict, adrList, adrDict):
    maxTotalGain = 0
    minPeriod = 0
    minMrketCap = 0
    minAdrLimit = 0.0
    maxRetraceVal = 0.0

    marketCapLimit = 9124279
    adrLimit = 189
    period = 1
    retraceVal = 0.01
    # for marketCapLimit in marketCapList:
    # for adrLimit in adrList:
    # newDataDict = {}
    # for symbol in dataDict.keys():
    #     if symbol not in marketCapDict: continue
    #     if symbol not in adrDict: continue
    #     marketCap = marketCapDict[symbol]
    #     if marketCap < marketCapLimit: continue
    #     adr = adrDict[symbol]
    #     if adr < adrLimit: continue
    #     newDataDict[symbol] = dataDict[symbol]

    
    # while period < 252:
    # while retraceVal < 2:
    totalGain = Backtest(dataDict, period, retraceVal)
    if totalGain > maxTotalGain:
        maxTotalGain = totalGain
        minPeriod = period
        minMrketCap = marketCapLimit
        minAdrLimit = adrLimit
        maxRetraceVal = retraceVal
        
        print(maxTotalGain,minPeriod,minMrketCap, minAdrLimit, maxRetraceVal)
        # retraceVal += 0.01
main(dataDict, emptyDict, marketCapList, marketCapDict, adrList, adrDict)