from modules.holdings import GetHoldings
from modules.aiztradingview import GetSectorIndustry, GetPerformance, GetTrend, GetSectorIndustryPerformance
import yfinance as yf
from modules.movingAverage import SmaArr
from modules.vwap import Vwap
from collections import defaultdict

def GetPerformance(symbol, days=35):
    try:
        stockInfo = yf.Ticker(symbol)
        vwapDf = stockInfo.history(period=f"{days}d")
        if len(vwapDf) < 3: return 1
        performance = vwapDf.iloc[-1].Close/vwapDf.iloc[-1].Open
        return performance
    except:
        return 1

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
    'COIN',
]

sectorPerf, industryPerf = GetSectorIndustryPerformance()
print(sectorPerf)
print(industryPerf)

sectorDict, industryDict = GetSectorIndustry()

sectorGroup = defaultdict(list)
industryGroup = defaultdict(list)
for symbol in options:
    if symbol in sectorDict:
        sectorGroup[sectorDict[symbol]].append(symbol)
    if symbol in industryDict:
        industryGroup[industryDict[symbol]].append(symbol)

tradable = []
for k, v in industryPerf.items():
    if k in industryGroup:
        tradable = industryGroup[k]
        break
print(tradable)


import sys
sys.exit(0)

performanceDict = {}
for symbol in options:
    performance = GetPerformance(symbol)
    if performance > 1:
        performanceDict[symbol] = performance
performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))

print(performanceDict)



# sectorDict, industryDict = GetSectorIndustry()

# newSectorDict = {}
# newIndustryDict = {}
# for symbol in options:
#     if symbol in sectorDict:
#         newSectorDict[symbol] = sectorDict[symbol]
#     if symbol in industryDict:
#         newIndustryDict[symbol] = industryDict[symbol]

# sectorGroup = defaultdict(list)
# for key, val in sorted(newIndustryDict.items()):
#     sectorGroup[val].append(key)
# industryGroup = defaultdict(list)
# for key, val in sorted(newSectorDict.items()):
#     industryGroup[val].append(key)

# performanceDict = {}
# secotrPerformanceDict = {}
# industryPerformanceDict = {}
# for k, v in sectorGroup.items():
#     count = 0
#     totalPerformance = 0
#     for symbol in v:
#         performance = 1
#         if symbol in performanceDict:
#             performance = performanceDict[symbol]
#         else:
#             performance = GetPerformance(symbol)
#             performanceDict[symbol] = performance
#         totalPerformance += performance
#         count += 1
#     secotrPerformanceDict[k] = totalPerformance/count

# for k, v in industryGroup.items():
#     count = 0
#     totalPerformance = 0
#     for symbol in v:
#         performance = 1
#         if symbol in performanceDict:
#             performance = performanceDict[symbol]
#         else:
#             performance = GetPerformance(symbol)
#             performanceDict[symbol] = performance
#         totalPerformance += performance
#         count += 1
#     industryPerformanceDict[k] = totalPerformance/count

# industryPerformanceDict = dict(sorted(industryPerformanceDict.items(), key=lambda item: item[1], reverse=True))
# print(industryPerformanceDict)
# optionList = industryGroup[next(iter(industryPerformanceDict))]
# print(optionList)



performanceDict = {}
for symbol in etfs:
    try:
        stockInfo = yf.Ticker(symbol)
        vwapDf = stockInfo.history(period="35d")
        if len(vwapDf) < 3: continue
        performance = vwapDf.iloc[-1].Close/vwapDf.iloc[-34].Close
        performanceDict[symbol] = performance
    except:
        continue
performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
print(performanceDict)

holdings = GetHoldings(next(iter(performanceDict)))
print(holdings)


tradableSectorList = []
tradableIndustryList = []
for symbol in holdings:
    if symbol in sectorDict:
        sector = sectorDict[symbol]
        if sector not in tradableSectorList:
            tradableSectorList.append(sector)
    if symbol in industryDict:
        industry = industryDict[symbol]
        if sector not in tradableIndustryList:
            tradableIndustryList.append(industry)

tradableList = []
newSectorDict = {}
newIndustryDict = {}
performanceList = GetTrend()
for symbol in performanceList:
    if symbol in sectorDict:
        if symbol in industryDict:
            sector = sectorDict[symbol]
            industry = industryDict[symbol]
            if sector in tradableSectorList:
                if industry in tradableIndustryList:
                    tradableList.append(symbol)
                    newSectorDict[symbol] = sector
                    newIndustryDict[symbol] = industry

from collections import defaultdict
sectorGroup = defaultdict(list)
for key, val in sorted(newIndustryDict.items()):
    sectorGroup[val].append(key)
industryGroup = defaultdict(list)
for key, val in sorted(newSectorDict.items()):
    industryGroup[val].append(key)

print(tradableList)
print(sectorGroup)
print(industryGroup)

def GetPerformanceDict(symbolList, etfPerformance):
    performanceDict = {}
    for symbol in symbolList:
        try:
            stockInfo = yf.Ticker(symbol)
            vwapDf = stockInfo.history(period="76d")
            vwapDf = vwapDf[:-1]
            if len(vwapDf) < 3: continue
            optionChain=list(stockInfo.options)
            if len(optionChain) > 0:
                v = vwapDf.Volume.values
                h = vwapDf.High.values
                l = vwapDf.Low.values
                vwapDf['Vwap'] = Vwap(v,h,l)
                closeArr = vwapDf.Close.values
                Sma5 = SmaArr(closeArr,5)[-1]
                bias5 = (closeArr[-1]/Sma5)/Sma5
                Sma25 = SmaArr(closeArr,25)[-1]
                bias25 = (closeArr[-1]-Sma25)/Sma25
                # Sma75 = SmaArr(closeArr,75)[-1]
                # bias75 = (closeArr[-1]-Sma75)/Sma75
                if bias5 > 0.267: continue
                # if bias25 > 0.232: continue
                # if bias25 < -0.074: continue
                # if bias75 > 0.42: continue
                # if bias75 < -0.347: continue
                if (
                    vwapDf.iloc[-1].Close / vwapDf.iloc[-1].Vwap > 21.3
                ): continue

                if (
                    vwapDf.iloc[-1].Close < vwapDf.iloc[-2].Close and
                    vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open
                ):
                    performance = vwapDf.iloc[-1].Close/vwapDf.iloc[-34].Close
                    if performance > etfPerformance * 0.88:
                        performanceDict[symbol] = performance
        except: continue
    return performanceDict

etfPerformance = list(performanceDict.items())[0][1]
print(etfPerformance)
performanceDict = GetPerformanceDict(tradableList, etfPerformance)
# if len(performanceDict) < 2:
#     performanceDictSecond = GetPerformanceDict(holdings, etfPerformance)
#     performanceDict = performanceDict | performanceDictSecond

performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
print(performanceDict)
