rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetAll, GetAttr
from modules.data import GetNpData
import pickle
import gc
import pandas as pd
import os

def DumpCsv(csvPath, data):
    df = pd.DataFrame(data, columns = ['Symbol'])
    df.to_csv(csvPath)
    print("dump")

def LoadCsv(csvPath):
    data = []
    if os.path.exists(csvPath):
        df = pd.read_csv(csvPath)
        data = list(df.Symbol.values)
    return data

def GetData(symbolList, update = False):
    dataDict = {}
    if update:
        for symbol in symbolList:
            npArr = GetNpData(symbol)
            if len(npArr) < backtestDays: continue
            npArr = npArr[-backtestDays:]
            dataDict[symbol] = npArr
        pickle.dump(dataDict, open("./pickle/pro/compressed/dataDict.p", "wb"), protocol=-1)
        print("pickle dump finished")
    else:
        output = open("./pickle/pro/compressed/dataDict.p", "rb")
        gc.disable()
        dataDict = pickle.load(output)
        output.close()
        gc.enable()
        print("load pickle finished")
    return dataDict

symbolList = GetAll()
backtestDays = 565

update = False
dataDict = GetData(symbolList, update)

topGainList = []
gainPath = "./data/gain.csv"
if update:
    for i in range(1, 563):
        topGain = 0
        gainDict = {}
        for symbol in dataDict:
            npArr = dataDict[symbol]
            gain = npArr[-i][3] / npArr[-i][0]
            if gain > topGain:
                topGain = gain
                gainDict[symbol] = gain
        for symbol in gainDict:
            if gainDict[symbol] >= topGain:
                topGainList.append(symbol)
            print(symbol)
    print(topGainList)
    DumpCsv(gainPath, topGainList)
else:
    topGainList = LoadCsv(gainPath)

# topGainList = []
# for i in range(1, 563):
#     topGain = 0
#     gainDict = {}
#     for symbol in dataDict:
#         npArr = dataDict[symbol]
#         gain = npArr[-i][3] / npArr[-i][0]
#         if gain > topGain:
#             topGain = gain
#             gainDict[symbol] = gain
#     for symbol in gainDict:
#         if gainDict[symbol] >= topGain:
#             if topGain >= 2:
#                 topGainList.append(symbol)
#         # print(symbol)
# topGainList.sort()
# print(topGainList)

# topPriceList = []
# for i in range(1, 563):
#     topGain = 0
#     gainDict = {}
#     priceDict = {}
#     for symbol in dataDict:
#         npArr = dataDict[symbol]
#         gain = npArr[-i][3] / npArr[-i][0]
#         if gain > topGain:
#             topGain = gain
#             gainDict[symbol] = gain
#             priceDict[symbol] = npArr[-i][0]
#     for symbol in gainDict:
#         if gainDict[symbol] >= topGain:
#             topPriceList.append(priceDict[symbol])
#         print(symbol)
# topPriceList.sort()
# print(topPriceList)

# topPriceList = []
# for i in range(1, 563):
#     topGain = 0
#     gainDict = {}
#     priceDict = {}
#     for symbol in dataDict:
#         npArr = dataDict[symbol]
#         gain = npArr[-i][3] / npArr[-i][0]
#         if gain > topGain:
#             topGain = gain
#             gainDict[symbol] = gain
#             priceDict[symbol] = npArr[-i-1][1]-npArr[-i-1][2]
#     for symbol in gainDict:
#         if gainDict[symbol] >= topGain:
#             topPriceList.append(priceDict[symbol])
#         print(symbol)
# topPriceList.sort()
# print(topPriceList)

# c/o 0.5688624091957055 2.0399999618530273

# high/lo 1 - 4.6875

# cleanList = []
# repeatList = []
# for symbol in topGainList:
#     if symbol not in cleanList:
#         cleanList.append(symbol)
#     else:
#         repeatList.append(symbol)

# print(len(topGainList),len(cleanList))
# print(repeatList)

# attr = "VWMA"
# attrDict = GetAttr(attr)
# attrLimitDict = {}
# for symbol in repeatList:
#     if symbol in attrDict:
#         attrLimitDict[symbol] = attrDict[symbol]
# attrLimitDict = dict(sorted(attrLimitDict.items(), key=lambda item: item[1], reverse=False))
# print(attrLimitDict)

# sectorList = []
# appearTimes = {}
# for k, v in attrLimitDict.items():
#     if v not in appearTimes:
#         appearTimes[v] = 0
# print(appearTimes)
# for k, v in attrLimitDict.items():
#     if v not in sectorList:
#         sectorList.append(v)
#     else:
#         appearTimes[v] = appearTimes[v]+1
# print(sectorList)
# appearTimes = dict(sorted(appearTimes.items(), key=lambda item: item[1], reverse=False))
# print(appearTimes)
# Commercial Services

float_shares_outstanding = 515651435
total_shares_outstanding_fundamental = 521989206
market_cap_basic = "2512316 - 8354411157.886125"
close = "0.06 - 173.82"
average_volume_90d_calc = 15302.63333332
average_volume_60d_calc = 5143.71666666
average_volume_30d_calc = 2279.56666666
average_volume_10d_calc = 939.5
number_of_shareholders = 1
adr = 0.0183572
atr = 0.0183686
volume = 396
valueTraded = 431.24
basic_eps_net_income = -121.452
earnings_per_share_basic_ttm = -148.543
current_ratio = 0.03425761
debt_to_equity = 27.8391966
ebitda = -418100001
enterprise_value_ebitda_ttm = 237.6560874
enterprise_value_fq = -42278301
last_annual_eps = -121.452
earnings_per_share_fq = -6.6
earnings_per_share_diluted_ttm = -148.543
gross_margin = -12785.46666668
gross_profit = -10317366
gross_profit_fq = -10602453
net_income = -1269100001
net_debt = 9468100001
after_tax_margin = -369442.46666668
number_of_employees = 1
operating_margin = -256797.26666668
pre_tax_margin = -369443.03333334
price_book_ratio = 198.3423914
price_book_fq = 30.7438
price_earnings_ttm = 152.30769232
price_free_cash_flow_ttm = 99.3022
price_revenue_ttm = 8728.09008
price_sales_ratio = 94.74593844
quick_ratio = 0.02409647
return_on_assets = -478.05100183
return_on_equity = -1563.9190639
return_on_invested_capital = -1225.32568723
total_assets = 1004999
total_current_assets = 1004999
total_debt = 10456000001
total_liabilities_fy = 13219000001
total_liabilities_fq = 12145100001
volatilityM = 3.71518368
volatilityW = 2.0983205
volatilityD = 0.51813471
vwap = "0.16313332 - 26.26666668"
vwma = "0.16246188 - 29.42710599"
perfY = -98.691411
perfYTD = -97.5283677
perf6M = -94.05566064
perf3M = -83.48214287
perfM = -79.85185186
perfW = -50.52746454
roc = -84.45714287
premarket_volume = 99

from modules.aiztradingview import GetGain
gainList = GetGain()
print(len(gainList))
print(gainList)
if "HKD" not in gainList:
    print("WORST")