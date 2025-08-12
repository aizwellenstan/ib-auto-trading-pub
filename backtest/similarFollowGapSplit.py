rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts

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
    for i in range(4, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyAvg = 1
        for symbol, npArr in dataDict.items():
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][1] - npArr[i-1][2] < npArr[i-2][1] - npArr[i-2][2]: continue
            if npArr[i-1][1] - npArr[i-1][2] < npArr[i-3][1] - npArr[i-3][2]: continue
            # if npArr[i][0] >= (npArr[i-1][3] + npArr[i-1][2])/2: continue
            similarPerfomanceList = np.empty(0)
            similarCompanyList = similarCompanyDict[symbol]
            similarPerfomanceList = np.array([dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict])
            # similarCompanyAvg = np.mean(similarPerfomanceList)
            # try:
            #     res = split_list_average_high_low(similarPerfomanceList)
            # except: continue
            # similarCompanyAvg = res[1]
            similarCompanyAvg = np.min(similarPerfomanceList)
            # print(similarCompanyAvg)
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
        gain = tp / npArr[i][0]
        balance *= gain
        print(balance)

# floatShareDict = GetAttr("float_shares_outstanding")
# industryDict = GetAttr("industry")
# assetDict = GetAttr("total_current_assets")
# length = len(dataDictUS["AAPL"])

# industryList = list(set(industryDict.values()))
# print(len(industryList))

# dataDict = {}
# for symbol, industry in industryDict.items():
#     if symbol not in dataDictUS: continue
#     if symbol not in floatShareDict: continue
#     if symbol not in assetDict: continue
#     npArr = dataDictUS[symbol]
#     if len(npArr) < length: continue
#     dataDict[symbol] = npArr

# Backtest(dataDict, length, floatShareDict, industryDict, assetDict)


floatShareDict = GetAttrJP("float_shares_outstanding")
industryDict = GetAttrJP("industry")
assetDict = GetAttrJP("total_current_assets")
netIncomeDict = GetAttrJP("net_income")
length = len(dataDictJP["9101"])

industryList = list(set(industryDict.values()))
print(len(industryList))

import itertools
count = 3945
industryDict = dict(itertools.islice(industryDict.items(), count))

dataDict = {}
for symbol, industry in industryDict.items():
    if symbol not in dataDictJP: continue
    
    # if symbol not in floatShareDict: continue
    if symbol not in similarCompanyDict: continue
    # if symbol not in assetDict: continue
    npArr = dataDictJP[symbol]
    if len(npArr) < length: continue
    dataDict[symbol] = npArr


Backtest(dataDict, length, similarCompanyDict)


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