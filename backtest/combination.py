from itertools import combinations
L = ['O','H','L','C']
L = [
    'coVal>','coVal<',
    'chVal>','chVal<',
    'clVal>','clVal<',
    'hlVal>','hlVal<',
    'hoVal>','hoVal<',
    'loVal>','loVal<'
]
comb = [",".join(map(str, comb)) for comb in combinations(L, 2)]
print(comb)

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
from modules.data import GetDividend

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


backtestLength = 252 * 3

import pickle


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
        co = v[:,3]/v[:,0]
        ch = v[:,3]/v[:,1]
        cl = v[:,3]/v[:,2]
        hl = v[:,1]/v[:,2]
        ho = v[:,1]/v[:,0]
        lo = v[:,2]/v[:,0]
        v = np.c_[v, co, ch, cl, hl, ho, lo]
        newDataDict[np.unicode_(k)]=np.float32(v)
dataDict = newDataDict

# @njit
def GetDailyGain(gainList):
    if len(gainList) < 1: return 1
    vol = 1 / len(gainList)
    dailyGain = 0
    for gain in gainList:
        dailyGain += vol * gain
    return dailyGain
    
# @njit
def GetGain(i, npArr,
    coVal,
    chVal,
    clVal,
    hlVal,
    hoVal,
    loVal
    ):
    coValH = coVal * 1.01
    chValH = coVal * 1.01
    clValH = coVal * 1.01
    hlValH = coVal * 1.01
    hoValH = coVal * 1.01
    loValH = coVal * 1.01
    coValL = coVal * 0.99
    chValL = coVal * 0.99
    clValL = coVal * 0.99
    hlValL = coVal * 0.99
    hoValL = coVal * 0.99
    loValL = coVal * 0.99
    gain = 0
    # co, ch, cl, hl, ho, lo
    if (
        npArr[i][4] < coValH and
        npArr[i][5] < chValH and
        npArr[i][6] < clValH and
        npArr[i][7] < hlValH and
        npArr[i][8] < hoValH and
        npArr[i][9] < loValH and
        npArr[i][4] > coValL and
        npArr[i][5] > chValL and
        npArr[i][6] > clValL and
        npArr[i][7] > hlValL and
        npArr[i][8] > hoValL and
        npArr[i][9] > loValL
    ): 
        gain = npArr[i][3] / npArr[i][0]
    return gain

# @njit
def Backtest(dataDict, coVal,
    chVal,
    clVal,
    hlVal,
    hoVal,
    loVal):
    totalGain = 1
    for i in range(1, backtestLength):
        gainList = np.empty(0)
        for symbol, npArr in dataDict.items():
            gain = GetGain(i, npArr, coVal,
                    chVal,
                    clVal,
                    hlVal,
                    hoVal,
                    loVal)
            if gain != 0:
                gainList = np.append(gainList, gain)
        dailyGain = GetDailyGain(gainList)
        totalGain *= dailyGain
    return totalGain

# @njit
def main(dataDict):
    maxTotalGain = 0
    maxcoVal=0
    maxchVal=0
    maxclVal=0
    maxhlVal=0
    maxhoVal=0
    maxloVal=0
    coVal=0.01
    chVal=1
    clVal=1
    hlVal=1
    hoVal=1
    loVal=1
    while coVal < 2:
        chVal = 1
        while chVal > 0:
            clVal = 1
            while clVal < 2:
                hlVal = 1
                while hlVal < 2:
                    hoVal = 1
                    while hoVal < 2:
                        loVal = 1
                        while loVal > 0:
                            totalGain = Backtest(dataDict, coVal,
                                chVal,
                                clVal,
                                hlVal,
                                hoVal,
                                loVal)
                            if totalGain > maxTotalGain:
                                maxTotalGain = totalGain
                                maxcoVal=coVal
                                maxchVal=chVal
                                maxclVal=clVal
                                maxhlVal=hlVal
                                maxhoVal=hoVal
                                maxloVal=loVal
                            
                            print(maxTotalGain,maxcoVal,
                                maxchVal,
                                maxclVal,
                                maxhlVal,
                                maxhoVal,
                                maxloVal)
                            loVal -= 0.1
                        hoVal += 0.1
                    hlVal += 0.1
                clVal += 0.1
            chVal -= 0.1
        coVal += 0.1
main(dataDict)