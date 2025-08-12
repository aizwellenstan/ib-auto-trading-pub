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

def Backtest(dataDict, length, similarCompanyDict):
    balance = 1
    for i in range(2, length):
        topSimilarCompanyAvg = 1
        topPefToAvg = 1
        topSymbol = ""
        for symbol, npArr in dataDict.items():
            similarPerfomanceList = np.empty(0)
            similarCompanyList = similarCompanyDict[symbol]
            similarPerfomanceList = [dataDict[t][i-1][3] * dataDict[t][i-1][4] for t in similarCompanyList if t in dataDict]
            similarCompanyAvg = np.mean(similarPerfomanceList)
            # print(similarCompanyAvg)
            # performance = npArr[i][0] / npArr[i-1][3]
            # pefToAvg = performance/similarCompanyAvg
            if (
                similarCompanyAvg > topSimilarCompanyAvg and
                npArr[i-1][3] < npArr[i-1][0]
            ):
                topSimilarCompanyAvg = similarCompanyAvg
                topSymbol = symbol
        npArr = dataDict[topSymbol]
        gain = npArr[i][3] / npArr[i][0]
        balance *= gain
        print(balance)

# floatShareDict = GetAttr("float_shares_outstanding")
# sectorDict = GetAttr("industry")
# assetDict = GetAttr("total_current_assets")
# length = len(dataDictUS["AAPL"])

# sectorList = list(set(sectorDict.values()))
# print(len(sectorList))

# dataDict = {}
# for symbol, sector in sectorDict.items():
#     if symbol not in dataDictUS: continue
#     if symbol not in floatShareDict: continue
#     if symbol not in assetDict: continue
#     npArr = dataDictUS[symbol]
#     if len(npArr) < length: continue
#     dataDict[symbol] = npArr

# Backtest(dataDict, length, floatShareDict, sectorDict, assetDict)


floatShareDict = GetAttrJP("float_shares_outstanding")
sectorDict = GetAttrJP("industry")
assetDict = GetAttrJP("total_current_assets")
length = len(dataDictJP["9101"])

sectorList = list(set(sectorDict.values()))
print(len(sectorList))

dataDict = {}
for symbol, sector in sectorDict.items():
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