rootPath = '..'
import sys
sys.path.append(rootPath)
import yfinance as yf
from modules.get_trend_line import find_grad_intercept, findGrandIntercept, GetResistance, GetSupport
from modules.data import GetNpData
import numpy as np

from modules.aiztradingview import GetClose
from modules.csvDump import DumpDict, LoadDict

# import modules.ib as ibc
# from modules.trade.vol import GetVolSlTp
# from modules.csvDump import LoadDict
# from modules.aiztradingview import GetSqueeze

# ibc = ibc.Ib()
# ib = ibc.GetIB(20)

# squeezeTradePath = f'{rootPath}/data/Squeeze.csv'
# squeezeTradeDict = LoadDict(squeezeTradePath,'sl')

# def CheckGap(symbol):
#     shift = 0
#     contract = ibc.GetStockContract(symbol)
#     hisBarsD1 = ib.reqHistoricalData(
#         contract, endDateTime='', durationStr='2 D',
#         barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
#     if len(hisBarsD1) < 2: return False
#     if (
#         hisBarsD1[-1-shift].open>hisBarsD1[-2-shift].close and
#         hisBarsD1[-1].close > hisBarsD1[-1].open
#     ):
#         return True
#     return False

# for symbol, sl in squeezeTradeDict.items():
#     if CheckGap(symbol):
#         print(symbol)

passedList = ['MESO','AGS','ISR']

update = False
resPath = './csv/squeezeRes2.csv'
if update:
    closeDict = GetClose()
    resDict = {}
    for symbol, close in closeDict.items():
        npArr = GetNpData(symbol)
        if len(npArr) < 624: continue
        npArrOrigin = npArr
        npArr = npArrOrigin[-624:]
        lastResistance = 0
        balance = 2700
        positions = 0
        lastSL = 0
        for i in range(len(npArrOrigin)-624, len(npArrOrigin)):
            npArr = npArrOrigin[0: i]
            resistance = findGrandIntercept(npArr[:,1])
            if resistance < 0.01: continue
            if positions > 0:
                if lastSL > npArr[-1][2]:
                    balance += positions*lastSL
                    positions = 0
                    lastSL = 0
            if (
                resistance > lastResistance
            ):
                support = findGrandIntercept(npArr[:,2])
                if support < 0.01: continue
                if positions < 1:
                    op = npArr[-1][0]
                    sl = support
                    if sl > op: continue
                    vol = balance/op
                    positions = vol
                    balance -= vol * op
                    lastSL = sl
                else:
                    lastSL = support
            lastResistance = resistance
        if positions > 0:
            balance += positions * npArr[-1][0]
        print(symbol, balance)
        resDict[symbol] = balance

    DumpDict(resDict,'balance',resPath)

resDict = LoadDict(resPath, 'balance')
resDict = dict(sorted(resDict.items(), key=lambda item: item[1], reverse=True))
# print(resDict)
# from modules.dict import take
# newDict = {}
# count = 0
# for symbol, balance in resDict.items():
#     newDict[symbol] = balance
#     count += 1
#     if count > 100: break
# print(newDict)
from modules.aiztradingview import GetSqueeze
import math

squeezeDict = GetSqueeze()
total = 0
for symbol, balance in resDict.items():
    if math.isnan(balance): continue
    total += balance
# print(total/len(resDict))

from modules.aiztradingview import GetAttr

attrDict = GetAttr("float_shares_outstanding")

newAttrDict = {}
for symbol, attr in attrDict.items():
    if symbol not in squeezeDict: continue
    newAttrDict[symbol] = attr
attrDict = newAttrDict
attrList = list(attrDict.values())
attrList.sort()

# vol90Dict = GetAttr("average_volume_90d_calc")
# vol60Dict = GetAttr("average_volume_60d_calc")
# vol30Dict = GetAttr("average_volume_30d_calc")
# vol10Dict = GetAttr("average_volume_10d_calc")
# volDict = GetAttr("volume")
attrList.sort(reverse=True)

# print(squeezeDict)
# tradeList = ["VZ","VTRS","UNP","SBUX","PFE","NKE","MCD","GS",
# "AMD","ALGO","NVDA","INTC","NFLX","UBER","FDX","MSFT","ZM",
# "AMZN","GOOG","MSOS","TSLA","COIN","BA","AAPL","DIS","QCOM",
# "META","SLV","SHAK","VZ","GLD"]
for symbol in passedList:
    if symbol in squeezeDict:
        print(symbol)

noTradeList = ['KIDS','CEVA','LIND','MTW','PETS','FTK','ETON',
'FGF']
for symbol in noTradeList:
    if symbol in squeezeDict:
        print("NO",symbol)

newDict = {}
for symbol, balance in resDict.items():
    if math.isnan(balance): continue
    if symbol not in squeezeDict: continue
    # if symbol not in attrDict: continue
    newDict[symbol] = balance

resDict = newDict
print(len(newDict))
print(sum(resDict.values())/len(resDict))

squeezeTradePath = f'{rootPath}/data/Squeeze.csv'
squeezeTradeDict = LoadDict(squeezeTradePath,'sl')
# print(squeezeDict)
# for symbol, sl in squeezeTradeDict.items():
#     if symbol in squeezeDict:
#         print(symbol)
tradeList = ['CEVA', 'DENN', 'PETS', 'AQMS', 'ETON', 'YTEN']
for symbol in tradeList:
    if symbol in squeezeDict:
        print(symbol)

# maxBalance = 0
# maxAttrLimit = 0
# volLimit = 94657
# while volLimit < 200000:
#     newDict = {}
#     for symbol, balance in resDict.items():
#         vol90 = vol90Dict[symbol]
#         vol60 = vol60Dict[symbol]
#         vol30 = vol30Dict[symbol]
#         vol10 = vol10Dict[symbol]
#         vol = volDict[symbol]
#         if vol90 < volLimit: continue
#         if vol60 < volLimit: continue
#         if vol30 < volLimit: continue
#         if vol10 < volLimit: continue
#         if vol < volLimit: continue
#         newDict[symbol] = balance
#     balance = sum(newDict.values())/len(newDict)
#     if balance > maxBalance:
#         maxBalance = balance
#         maxAttrLimit = volLimit
#         print(maxBalance, maxAttrLimit)
#     volLimit += 1

if "TSLA" not in squeezeDict:
    print("NO TSLA")

import sys
sys.exit(0)

# close < 0.2769 >49.35
# total_liabilities_fq <2704636 280056
# total_liabilities_fy <4702863 191639
# premarket_volume 37610 120567
# premarket_volume >100
# total_debt <1659427 96005
# current_ratio 52.77624225 79512
# total_shares_outstanding_fundamental 14575000 72135
# debt_to_equity 0.62947974 54454
# debt_to_equity <0.19854978 >0 61001
# total_current_assets 8110065 40051
# price_free_cash_flow_ttm 37.82118457
# dividends_per_share_fq 0 39917
# dividends_per_share_fq <0.00017 66199
# dividends_paid 0 38842
# total_assets 11092751 34584
# Value.Traded 1722440.96 29085
print("ATTR")
print(attrDict["AAPL"])
print(attrDict["AMZN"])
print(attrDict["MSFT"])
print(attrDict["TSLA"])
maxBalance = 0
maxAttrLimit = 0
attrLimit = 200
for attrLimit in attrList:
# while attrLimit > 1:
    newDict = {}
    for symbol, balance in resDict.items():
        if symbol not in attrDict: continue
        attr = attrDict[symbol]
        if attr > attrLimit: continue
        newDict[symbol] = balance
    balance = sum(newDict.values())/len(newDict)
    stop=False
    # for symbol in tradeList:
    #     if symbol not in newDict:
    #         stop=True
    #         break
    if stop:
        break
    if balance > maxBalance:
        maxBalance = balance
        maxAttrLimit = attrLimit
        print(maxBalance, maxAttrLimit)
    elif balance < maxBalance:
        print(attrLimit)
        break
    # attrLimit -= 0.01
    # print(maxBalance, maxAttrLimit)