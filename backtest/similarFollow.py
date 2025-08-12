rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts
from concurrent.futures import ThreadPoolExecutor, as_completed


similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    
rironkabukaDict = LoadPickle(rironkabukaPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)

# dataDict = dataDictUS
# dataDict.update(dataDictJP)
from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np

# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    average_high = np.mean(high_values)
    
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    average_low = np.mean(low_values)
    
    return np.array([average_high, average_low])

def Backtest(dataDict, length, similarCompanyDict):
    balance = 1
    try:
        for i in range(3, length):
            topPefToAvg = 1
            topSimilarCompanyAvg = 1
            topSymbol = ""
            for symbol, npArr in dataDict.items():
                # if npArr[i-1][4] >= npArr[i-2][4]: continue
                # if npArr[i-1][1] - npArr[i-1][2] < npArr[i-2][1] - npArr[i-2][2]: continue
                # if npArr[i-1][1] - npArr[i-1][2] < npArr[i-3][1] - npArr[i-3][2]: continue
                similarPerfomanceList = np.empty(0)
                similarCompanyList = similarCompanyDict[symbol]
                similarPerfomanceList = [dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict]
                similarCompanyAvg = np.min(similarPerfomanceList)
                # if similarCompanyAvg <= 1: continue
                performance = npArr[i][0] / npArr[i-1][3]
                pefToAvg = performance/similarCompanyAvg
                if pefToAvg < topPefToAvg:
                    topPefToAvg = pefToAvg
                    topSymbol = symbol
                    topSimilarCompanyAvg = similarCompanyAvg
            if topSymbol == "": continue
            npArr = dataDict[topSymbol]
            tp = npArr[i][3]
            if npArr[i][1] > npArr[i-1][3] * topSimilarCompanyAvg:
                tp = npArr[i-1][3] * topSimilarCompanyAvg
            gain = tp * topSimilarCompanyAvg / npArr[i][0]
            balance *= gain
        return balance
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0


import itertools
def HandleBacktest(oriIndustryDict, dataDictUS, similarCompanyDict, count):
    industryDict = dict(itertools.islice(oriIndustryDict.items(), count))

    sectorList = list(set(industryDict.values()))

    dataDict = {}
    grouped_dict = {}
    for key, value in industryDict.items():
        if key not in dataDictUS: continue
        if value not in grouped_dict:
            grouped_dict[value] = [key]
        else:
            grouped_dict[value].append(key)

    new_dict = {}

    for industry, symbols in grouped_dict.items():
        for symbol in symbols:
            filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
            if len(filtered_symbols) >= 4:
                new_dict.setdefault(symbol, []).extend(filtered_symbols)

    for symbol, sector in industryDict.items():
        if symbol not in dataDictUS: continue
        if symbol not in new_dict: continue
        npArr = dataDictUS[symbol]
        if len(npArr) < length: continue
        dataDict[symbol] = npArr

    try:
        balance = Backtest(dataDict, length, new_dict)
    except: return [count, 0]
    return [count, balance]

floatShareDict = GetAttr("float_shares_outstanding")
industryDict = GetAttr("industry")
assetDict = GetAttr("total_current_assets")
length = len(dataDictUS["AAPL"])

oriIndustryDict = industryDict


maxCount = 50
maxBalance = 1
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleBacktest, oriIndustryDict, dataDictUS, similarCompanyDict, count) for count in range(2, length-1)]
    for future in as_completed(futures):
        result = future.result()
        if len(result) < 2: continue
        balance = result[1]
        if balance <= 1: continue
        count = result[0]
        if balance > maxBalance:
            maxBalance = balance
            maxCount = count
            print(maxBalance, maxCount)


# floatShareDict = GetAttrJP("float_shares_outstanding")
# sectorDict = GetAttrJP("industry")
# assetDict = GetAttrJP("total_current_assets")
# length = len(dataDictJP["9101"])

# sectorList = list(set(sectorDict.values()))
# print(len(sectorList))

# dataDict = {}
# for symbol, sector in sectorDict.items():
#     if symbol not in dataDictJP: continue
    
#     # if symbol not in floatShareDict: continue
#     if symbol not in similarCompanyDict: continue
#     # if symbol not in assetDict: continue
#     npArr = dataDictJP[symbol]
#     if len(npArr) < length: continue
#     dataDict[symbol] = npArr

# Backtest(dataDict, length, similarCompanyDict)


# # attrList = list(reversed(list(floatShareDict.values())))

# # 5375322
# balance = 1
# for i in range(2, length):
#     topVolChange = 1
#     topSymbol = ""
#     for symbol, npArr in dataDict.items():
#         if symbol not in floatShareDict: continue
#         volChange = npArr[-1][4] / npArr[-2][4]
#         if (
#             volChange > topVolChange and
#             (npArr[-1][2] < npArr[-2][2] and npArr[-1][3] > npArr[-2][1])
#         ):
#             topVolChange = volChange
#             topSymbol = symbol

#     npArr = dataDict[topSymbol]
#     gain = npArr[i][3] / npArr[i][0]
#     balance *= gain
#     print(balance)