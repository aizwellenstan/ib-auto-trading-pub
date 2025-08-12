rootPath = '..'
import sys
sys.path.append(rootPath)
import numpy as np
from modules.data import GetNpData
from modules.aiztradingview import GetAttr, GetPerformance
from numba import njit
from numba import types
from numba.typed import Dict
from modules.movingAverage import SmaArr

from numba import types

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

# performanceList = GetPerformance()
marketCapDict = GetAttr("market_cap_basic")
newMarCapDict = Dict.empty(key_type=types.unicode_type,value_type=types.uint64)
for symbol, v in marketCapDict.items():
    if symbol in options:
        # if symbol not in performanceList: continue
        newMarCapDict[np.unicode_(symbol)] = np.uint64(marketCapDict[symbol])
marketCapDict = newMarCapDict

tradeList = []
for symbol, v in marketCapDict.items():
    if v < 40370174: continue
    tradeList.append(symbol)
print(tradeList)

backtestLength = 252 * 3

import pickle
# dataDict = {}
# for symbol in options:
#     if symbol not in marketCapDict: continue
#     npArr = GetNpData(symbol)
#     if len(npArr) < backtestLength: continue
#     dataDict[symbol] = npArr


picklePath = "./pickle/pro/compressed/dataDict.p"
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
    if k in options:
        closeArr = v[:,3]
        sma200 = SmaArr(closeArr,200)
        sma75 = SmaArr(closeArr,75)
        sma25 = SmaArr(closeArr,25)
        sma5 = SmaArr(closeArr,5)
        bias200 = (closeArr - sma200) / sma200
        bias75 = (closeArr - sma75) / sma75
        bias25 = (closeArr - sma25) / sma25
        bias5 = (closeArr - sma5) / sma5
        v = np.c_[v, bias200, bias75, bias25, bias5]
        newDataDict[np.unicode_(k)]=np.float32(v)
dataDict = newDataDict

marketCapList = np.uint64(list(marketCapDict.values()))
marketCapList.sort()

# @njit
def GetDailyGain(gainList):
    if len(gainList) < 1: return 1
    vol = 1 / len(gainList)
    dailyGain = 0
    for gain in gainList:
        dailyGain += vol * gain
    return dailyGain
    
# @njit
def GetGain(i, marketCap, npArr, marketCapLimit, gapVal,
    biasLow200, biasHigh200, 
    biasLow75, biasHigh75,
    biasLow25, biasHigh25,
    biasLow5, biasHigh5
    ):
    '''
    bias200 :7 
    75 :6
    25 :5
    5 :4
    '''
    gain = 0
    if marketCap > marketCapLimit:
        # # bias200
        # if npArr[i][7] < -0.1 and npArr[i][7] > -0.4:
        #     return gain
        # # bias75
        # if npArr[i][6] < -0.1 and npArr[i][6] > -0.2:
        #     return gain
        # # bias25
        # if npArr[i][5] < 0.1 and npArr[i][5] > -0.2:
        #     return gain
        # # bias5
        # if npArr[i][4] < 0 and npArr[i][4] > -0.1:
        #     return gain
        # bias200
        if npArr[i][7] < biasHigh200 and npArr[i][7] > biasLow200:
            return gain
        # # bias75
        # if npArr[i][6] < biasHigh75 and npArr[i][6] > biasLow75:
        #     return gain
        # # bias25
        # if npArr[i][5] < biasHigh25 and npArr[i][5] > biasLow25:
        #     return gain
        # # bias5
        # if npArr[i][4] < biasHigh5 and npArr[i][4] > biasLow5:
        #     return gain
        # gap = npArr[i][0] / npArr[i-1][3]
        # if gap > gapVal:
        gain = npArr[i][3] / npArr[i][0]
    return gain

# @njit
def Backtest(dataDict, marketCapDict, marketCapLimit, gapVal,
    biasLow200, biasHigh200,
    biasLow75, biasHigh75,
    biasLow25, biasHigh25,
    biasLow5, biasHigh5):
    totalGain = 1
    for i in range(1, backtestLength):
        gainList = np.empty(0)
        for symbol, npArr in dataDict.items():
            marketCap = marketCapDict[symbol]
            gain = GetGain(i, marketCap, npArr, marketCapLimit, gapVal,
                biasLow200, biasHigh200,
                biasLow75, biasHigh75,
                biasLow25, biasHigh25,
                biasLow5, biasHigh5)
            if gain != 0:
                gainList = np.append(gainList, gain)
        dailyGain = GetDailyGain(gainList)
        totalGain *= dailyGain
    return totalGain

# @njit
def main(dataDict, marketCapDict, marketCapList):
    maxTotalGain = 0
    minMarketCapLimit = 0
    minGapLimit = 0
    minBiasLow200 = 0
    maxBiasHigh200 = 0
    minBiasLow75 = 0
    maxBiasHigh75 = 0
    minBiasLow25 = 0
    maxBiasHigh25 = 0
    minBiasLow5 = 0
    maxBiasHigh5 = 0
    gapVal = 1.03
    gapVal = 0
    changeVal = np.float32(0.1)
    biasLow200 = -1
    biasHigh200 = 0.12
    biasLow75 = -0.3
    biasHigh75 = 0.1
    biasLow25 = -0.1
    biasHigh25 = 0.1
    biasLow5 = -0.1
    biasHigh5 = 0.1
    for marketCapLimit in marketCapList:
        totalGain = Backtest(dataDict, marketCapDict, marketCapLimit, gapVal,
            biasLow200, biasHigh200,
            biasLow75, biasHigh75,
            biasLow25, biasHigh25,
            biasLow5, biasHigh5)
        if totalGain > maxTotalGain:
            maxTotalGain = totalGain
            minMarketCapLimit = marketCapLimit
            minGapLimit = gapVal
            minBiasLow200 = biasLow200
            maxBiasHigh200 = biasHigh200
            minBiasLow75 = biasLow75
            maxBiasHigh75 = biasHigh75
            minBiasLow25 = biasLow25
            maxBiasHigh25 = biasHigh25
            minBiasLow5 = biasLow5
            maxBiasHigh5 = biasHigh5
        
        print(minMarketCapLimit,minGapLimit,maxTotalGain,
            minBiasLow200, maxBiasHigh200,
            minBiasLow75, maxBiasHigh75,
            minBiasLow25, maxBiasHigh25,
            minBiasLow5, maxBiasHigh5)
main(dataDict, marketCapDict, marketCapList)