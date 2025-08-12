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

newDataDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])

for k,v in dataDict.items():
    if len(v) < backtestLength: continue
    if k not in gainList:continue
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
def Backtest(dataDict, period, dev):
    totalGain = 1
    for i in range(1, backtestLength):
        gainList = np.empty(0)
        maxMomentum = 2
        gain = 1
        for symbol, npArr in dataDict.items():
            lowerBand = GetLowerBand(npArr, period, dev)
            # upperBand = GetUpperBand(npArr, period, dev)
            
            if (
                npArr[i-1][3] < lowerBand
                # npArr[i-1][3] > upperBand
            ):
                # maxMomentum = momentum
                gain = npArr[i][4]
                gainList = np.append(gainList, gain)
        # totalGain *= gain
        dailyGain = GetDailyGain(gainList)
        totalGain *= dailyGain
    return totalGain

emptyDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])

# @njit
def main(dataDict, emptyDict, marketCapList, marketCapDict, adrList, adrDict):
    maxTotalGain = 0
    minPeriod = 0
    minMrketCap = 0
    minAdrLimit = 0.0
    maxDev = 0.0

    marketCapLimit = 9124279
    adrLimit = 189
    period = 141
    while period < 1000:
        dev = 0.1
        while dev < 3:
            totalGain = Backtest(dataDict, period, dev)
            if totalGain > maxTotalGain:
                maxTotalGain = totalGain
                minPeriod = period
                maxDev = dev
                
                print(maxTotalGain,minPeriod, maxDev)
            dev += 0.1
        period += 1
main(dataDict, emptyDict, marketCapList, marketCapDict, adrList, adrDict)