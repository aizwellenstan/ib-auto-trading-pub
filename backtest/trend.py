import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.holdings import GetHoldings
from modules.data import GetDf
from modules.movingAverage import SmaArr

etfs = ['XLE','XLU','XLP','XLV','XLI','XLK','XLY','XLF']

def updateData(etfs):
    for etf in etfs:
        etfdf = GetDf(etf)
        holdings = GetHoldings(etf)
        for symbol in holdings:
            df = GetDf(symbol)
            print(etf,symbol)

days =  1000
dataDict = {}
holdingsDict = {}
for etf in etfs:
    etfdf = GetDf(etf, update=False)
    closeArr = etfdf.Close.values
    Sma25 = SmaArr(closeArr,25)
    Bias = (closeArr-Sma25) / Sma25
    etfdf['Bias'] = Bias
    etfdf = etfdf[['Open','High','Low','Close','Vwap','Bias']]
    etfdf = etfdf.tail(days)
    etfNpArr = etfdf.to_numpy()
    dataDict[etf] = etfNpArr
    holdings = GetHoldings(etf)
    holdingsDict[etf] = holdings
    for symbol in holdings:
        df = GetDf(symbol)
        if len(df) < 1: continue
        closeArr = df.Close.values
        Sma25 = SmaArr(closeArr,25)
        Bias = (closeArr-Sma25) / Sma25
        df['Bias'] = Bias
        df = df[['Open','High','Low','Close','Vwap','Bias']]
        df = df.tail(days)
        npArr = df.to_numpy()
        dataDict[symbol] = npArr

# maxGain = 0
# maxDay = 0
# day = 0
# while day <= 365:
#     day += 1
#     gain = 1
#     for i in range(367, days-1):
#         performanceDict = {}
#         for etf in etfs:
#             npArr = dataDict[etf]
#             performance = npArr[i-1][3] / npArr[i-day][3]
#             performanceDict[etf] = performance
#         performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
#         holdings = holdingsDict[next(iter(performanceDict))]
#         for symbol in holdings:
#             if symbol not in dataDict: continue
#             npArr = dataDict[symbol]
#             gap = npArr[i][0] / npArr[i-1][3]
#             # if gap > 1:
#             # if npArr[i-1][5] < 1:
#             gain *= npArr[i][3] / npArr[i][0]
#     print(gain)
#     if gain > maxGain:
#         maxGain = gain
#         maxDay = day
#     print(f"maxGain {maxGain} maxDay {maxDay}")

# maxGain 31.89880484462636 maxDay 34

# maxGain = 0
# maxDay = 0
# minBiasVal = 1
# day = 0
# while day <= 365:
#     day += 1
#     biasVal = 0
#     while biasVal >= -0.0482831585:
#         gain = 1
#         for i in range(367, days-1):
#             performanceDict = {}
#             for etf in etfs:
#                 npArr = dataDict[etf]
#                 performance = npArr[i-1][3] / npArr[i-day][3]
#                 performanceDict[etf] = performance
#             performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
#             holdings = holdingsDict[next(iter(performanceDict))]
#             for symbol in holdings:
#                 if symbol not in dataDict: continue
#                 npArr = dataDict[symbol]
#                 gap = npArr[i][0] / npArr[i-1][3]
#                 # if gap > 1:
#                 if npArr[i-1][5] < biasVal:
#                     gain *= npArr[i][3] / npArr[i][0]
#         print(gain)
#         if gain > maxGain:
#             maxGain = gain
#             maxDay = day
#             minBiasVal = biasVal
#         print(f"maxGain {maxGain} maxDay {maxDay} minBiasVal {minBiasVal}")
#         biasVal -= 0.001

# maxGain 31.89880484462636 maxDay 34

maxGain = 0
maxDay = 0
day = 34
# while day <= 365:
#     day += 1
performanceVal = 0.88
# while performanceVal > 0:
# performanceVal -= 0.01
gain = 1
for i in range(367, days-1):
    performanceDict = {}
    for etf in etfs:
        npArr = dataDict[etf]
        etfperformance = npArr[i-1][3] / npArr[i-day][3]
        performanceDict[etf] = etfperformance
    performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
    holdings = holdingsDict[next(iter(performanceDict))]
    for symbol in holdings:
        if symbol not in dataDict: continue
        npArr = dataDict[symbol]
        performance = npArr[i-1][3] / npArr[i-day][3]
        if performance > etfperformance * performanceVal:
        # gap = npArr[i][0] / npArr[i-1][3]
        # if gap > 1:
        # if npArr[i-1][5] < 1:
            if (
                npArr[i-1][3] < npArr[i-1][0]
            ):
                # 1.036091549 1.032309942
                if npArr[i][0] / npArr[i-1][3] > 1.032: continue
                gain *= npArr[i][3] / npArr[i][0]
print(gain)
if gain > maxGain:
    maxGain = gain
    maxDay = day
    minPerformanceVal = performanceVal
print(f"maxGain {maxGain} maxDay {maxDay} minPerformanceVal {minPerformanceVal}")

# 0.87