rootPath = '..'
import sys
sys.path.append(rootPath)
import numpy as np
from modules.data import GetNpData
from modules.aiztradingview import GetAttr, GetPerformance
from numba import njit
from numba import types
from numba.typed import Dict

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
    # 'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    # 'V','CAT','MRNA','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    # 'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    # 'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    # 'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    # 'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    # 'VIX',
    # 'COIN'
]

# performanceList = GetPerformance()
marketCapDict = GetAttr("market_cap_basic")
newMarCapDict = {}
for symbol, v in marketCapDict.items():
    if symbol in options:
        # if symbol not in performanceList: continue
        newMarCapDict[symbol] = marketCapDict[symbol]
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

newDataDict = {}
for k,v in dataDict.items():
    if k in options:
        newDataDict[k] = v
dataDict = newDataDict


marketCapList = list(marketCapDict.values())
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
def GetGain(i, marketCap, npArr, marketCapLimit, gapVal):
    gain = 0
    if marketCap > marketCapLimit:
        gap = npArr[i][0] / npArr[i-1][3]
        if gap > gapVal:
            gain = npArr[i][3] / npArr[i][0]
    return gain

def Backtest(marketCapLimit, gapVal):
    totalGain = 1
    for i in range(1, backtestLength):
        gainList = np.empty(0)
        for symbol, npArr in dataDict.items():
            marketCap = marketCapDict[symbol]
            gain = GetGain(i, marketCap, npArr, marketCapLimit, gapVal)
            if gain != 0:
                gainList = np.append(gainList, gain)
        dailyGain = GetDailyGain(gainList)
        totalGain *= dailyGain
    return totalGain

def main():
    maxTotalGain = 0
    minMarketCapLimit = 0
    minGapLimit = 0
    for marketCapLimit in marketCapList:
        gapVal = 1
        while gapVal < 1.5:
            totalGain = Backtest(marketCapLimit, gapVal)
            if totalGain > maxTotalGain:
                maxTotalGain = totalGain
                minMarketCapLimit = marketCapLimit
                minGapLimit = gapVal
            gapVal += 0.001
        print(minMarketCapLimit,minGapLimit,maxTotalGain)
main()