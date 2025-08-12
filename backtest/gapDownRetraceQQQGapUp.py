rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.movingAverage import SmaArr
from modules.data import GetNpData
import numpy as np
from numba import range, njit
from modules.aiztradingview import GetClose, GetTradable, GetGainable
import pickle
from modules.csvDump import DumpCsv, LoadCsv

dataPath = "./pickle/dataArrOptions.p"
dataArr = {}
closeDict = GetClose()

options = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'DAL','PLUG','JD','AA','HYG','PFE','FCX',
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
    'ARKK','GDX','GLD','SLV',
    # 'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    # 'V','MRNA','CLAR','SE','ZM','DOCU','SPLK',
    # 'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    # 'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    # 'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    # 'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    # 'VIX',
    # 'COIN'
]

update = False
if update:
    for symbol, close in closeDict.items():
        if symbol not in options: continue
        npArr = GetNpData(symbol)
        if len(npArr) < 1: continue
        dataArr[symbol] = npArr
        print(symbol)

    pickle.dump(dataArr, open(dataPath, "wb"))
    print("pickle dump finished")
else:
    # import gc
    output = open(dataPath, "rb")
    # gc.disable()
    dataArr = pickle.load(output)
    output.close()
    # gc.enable()



# # @njit
def Backtest(qqqArr, npArr):
    npArr = npArr[-1058:]
    val = 0.01
    maxBalance = 1
    maxVal = 0
    while val < 1:
        balance = 1
        for i in range(1, len(npArr)):
            if (
                qqqArr[i][0] > qqqArr[i-1][3] and
                npArr[i][0] < npArr[i-1][3]
            ):
                op = npArr[i][0]
                if op < 0.01: return 0
                tp = (npArr[i-1][3] - npArr[i][0]) * val + npArr[i][0]
                if tp - op < 0.01: continue
                if tp > npArr[i][1]:
                    tp = npArr[i][3]
                gain = tp / op
                balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
            print(maxBalance,maxVal)
        val += 0.01
    if maxBalance <= 1: return [0, maxVal]
    print('MaxBalance',maxBalance)
    return [maxBalance/len(npArr), maxVal]



gainPerDayDict = {}
symbolList = ['HIVE']

# from modules.ib_data import Get1mData

ignoreList = []
ignorePath = f"{rootPath}/data/Ignore.csv"
# ignoreList = LoadCsv(ignorePath)

# def FrequencyCheck1m(symbol):
#     df = Get1mData(symbol,1)
#     if len(df) < 1:
#         ignoreList.append(symbol)
#         return False
#     df = df.drop_duplicates(subset=["open","close"],keep=False)
#     if len(df) < 64: return False
#     return True

from ib_insync import *
from datetime import datetime as dt, timedelta
import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=32)
end = dt.strptime(str('2023-02-10 11:00:00'), '%Y-%m-%d %H:%M:%S')
def FrequencyCheck1mShift(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime=end, durationStr='1 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["open","close"],keep=False)
    print(len(df))
    if len(df) < 412: return False
    return True

lowVolPath = f"{rootPath}/data/lowVol2.csv"
lowVolList = LoadCsv(lowVolPath)

# QQQ SPY DIA IWM BRK.B CAT HYG
qqqArr = GetNpData("QQQ")
qqqArr = qqqArr[-1058:]
valDict = {}
for symbol, close in closeDict.items():
# for symbol in options:
#     symbol = 'VXX'
    # symbol = 'TQQQ'
    # symbol = 'AAPL'
    # symbol = 'NKE'
    
    # symbol = 'DIS'
    # symbol = 'QCOM'
    # symbol = 'NVDA'
    if symbol in ignoreList: continue
    if symbol not in dataArr: continue
    if symbol in lowVolList: continue
    if symbol not in options: continue
    npArr = dataArr[symbol]
    if len(npArr) < 1058: continue
    res = Backtest(qqqArr, npArr)
    balance = res[0]
    val = res[1]
    # if not FrequencyCheck1m(symbol):
    # if not FrequencyCheck1mShift(symbol):
    #     lowVolList.append(symbol)
    #     continue
    gainPerDayDict[symbol] = balance
    valDict[symbol] = val
    print(symbol, balance)
    # break
print(len(gainPerDayDict))
gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
# print(gainPerDayDict)

newGainPerDayDict = {}
count = 0
for symbol, gainPerDay in gainPerDayDict.items():
    if gainPerDay == 0: continue
    newGainPerDayDict[symbol] = gainPerDay
    count += 1
    if count > 100: break
print(newGainPerDayDict)

newValDict = {}
for symbol, v in newGainPerDayDict.items():
    newValDict[symbol] = valDict[symbol]
print(newValDict)

import sys
sys.exit(0)

lowVolPath = f"{rootPath}/data/lowVol2.csv"
DumpCsv(lowVolPath, lowVolList)
DumpCsv(ignorePath, ignoreList)

