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
    'NVDA','SMH','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','TSM','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'CSCO','DAL','PLUG','JD','AA','HYG','BMY','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','WMT','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY',
    # 'GOOG',
    # 'GOOGL',
    'ARKK','GDX','GLD','SLV',
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
    if v < 142589022538: continue
    tradeList.append(symbol)
print(tradeList)

backtestLength = 252 * 4

# dataDict = {}
# for symbol in tradeList:
#     if symbol not in marketCapDict: continue
#     npArr = GetNpData(symbol)
#     if len(npArr) < backtestLength: continue
#     dataDict[symbol] = npArr
import pickle
# pickle.dump(dataDict, open("./pickle/pro/compressed/dataDict.p", "wb"), protocol=-1)
# print("pickle dump finished")

import gc
output = open("./pickle/pro/compressed/dataDict.p", "rb")
gc.disable()
dataDict = pickle.load(output)
output.close()
gc.enable()

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
        if npArr[i][0] > npArr[i-1][1]:
            gap = npArr[i][0] / npArr[i-1][3]
            if gap > gapVal:
                gain = npArr[i][3] / npArr[i][0]
    return gain

def Backtest(marketCapLimit, gapVal):
    totalGain = 1
    for i in range(2, backtestLength):
        gainList = np.empty(0)
        for symbol, npArr in dataDict.items():
            if symbol not in marketCapDict: continue
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
    marketCapLimit = 142589022538
    gapVal = 1.0338
    totalGain = Backtest(marketCapLimit, gapVal)
    if totalGain > maxTotalGain:
        maxTotalGain = totalGain
        minMarketCapLimit = marketCapLimit
        minGapLimit = gapVal
    print(minMarketCapLimit,minGapLimit,maxTotalGain)
main()