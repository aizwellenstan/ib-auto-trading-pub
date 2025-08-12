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
inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryUS.p"
netIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeUS.p"
treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesUS.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    
rironkabukaDict = LoadPickle(rironkabukaPath)
inventoryDict = LoadPickle(inventoryPath)
netIncomeDict = LoadPickle(netIncomePath)
treasurySharesDict = LoadPickle(treasurySharesPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)

# dataDict = dataDictUS
# dataDict.update(dataDictJP)
from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np

def Backtest(dataDict, length, similarCompanyDict, debtDict,
    inventoryDict, netIncomeDict, treasurySharesDict):
    balance = 1
    topPefToAvg = 1
    topSymbol = ""
    topSimilarCompanyAvg = 1
    shift = 1
    for symbol, npArr in dataDict.items():
        if symbol in treasurySharesDict:
            treasuryShares = treasurySharesDict[symbol]
            if treasuryShares[0] < treasuryShares[1]: continue
        # if npArr[-shift-1][4] >= npArr[-shift-2][4]: continue
        # if symbol not in debtDict: continue
        # if debtDict[symbol] > 4927745171: continue
        # if (
        #     npArr[-shift-1][4] <= npArr[-shift-2][4] and
        #     npArr[-shift-2][4] <= npArr[-shift-3][4] and
        #     npArr[-shift-3][4] <= npArr[-shift-4][4] and
        #     npArr[-shift-1][3] <= npArr[-shift-1][0] and
        #     npArr[-shift-2][3] <= npArr[-shift-2][0] and
        #     npArr[-shift-3][3] / npArr[-shift-4][0] > 1.1
        # ): continue
        # if (
        #     npArr[-shift-3][3] / npArr[-shift-3][0] > 1.21 and
        #     npArr[-shift-3][4] / npArr[-shift-4][4] > 7 and
        #     npArr[-shift-3][0] < npArr[-shift-4][2]
        # ): continue
        if (
            symbol in netIncomeDict and
            symbol in inventoryDict
        ):
            netIncome = netIncomeDict[symbol]
            inventory = inventoryDict[symbol]
            if (
                len(inventory) > 2 and
                len(netIncome) > 2 and
                inventory[0] > inventory[1] and
                inventory[1] > inventory[2] and
                netIncome[0] < netIncome[1] and
                netIncome[1] < netIncome[2]
            ): continue
        similarPerfomanceList = np.empty(0)
        similarCompanyList = similarCompanyDict[symbol]
        similarPerfomanceList = [dataDict[t][-shift][0] / dataDict[t][-shift-1][3] for t in similarCompanyList if t in dataDict]
        similarCompanyAvg = np.min(similarPerfomanceList)
        # print(similarCompanyAvg)
        performance = npArr[-shift][0] / npArr[-shift-1][3]
        pefToAvg = performance/similarCompanyAvg
        if pefToAvg < topPefToAvg:
            topPefToAvg = pefToAvg
            topSymbol = symbol
            topSimilarCompanyAvg = similarCompanyAvg
    target = dataDict[topSymbol][-shift-1][3] * topSimilarCompanyAvg
    print("PREVIOUSCLOSE",dataDict[topSymbol][-shift-1][3])
    print(topSymbol, target)
    return balance

floatShareDict = GetAttr("float_shares_outstanding")
industryDict = GetAttr("industry")
debtDict = GetAttr("total_debt")
assetDict = GetAttr("total_current_assets")
liabilitiesDict = GetAttr("total_liabilities_fy")
roaDict = GetAttr("return_on_assets")
length = len(dataDictUS["AAPL"])

oriIndustryDict = industryDict

import pandas as pd
import os
optionPath = f'{rootPath}/data/Options.csv'
if os.path.exists(optionPath):
    df = pd.read_csv(optionPath)
    optionList = list(df.Symbol.values)

import itertools
count = 98
industryDict = dict(itertools.islice(oriIndustryDict.items(), count))

sectorList = list(set(industryDict.values()))

optignoreList = ["MRK","JNJ","CSCO", "T"]
ignoreList = [
    "Electronic Production Equipment", 
    "Telecommunications Equipment", 
    "Environmental Services",
    "Computer Peripherals",
    "Biotechnology",
    "Commercial Printing/Forms",
    "Trucks/Construction/Farm Machinery",
    "Auto Parts: OEM",
    "Tools & Hardware",
    "Recreational Products",
    "Metal Fabrication",
    "Forest Products",
    "Industrial Specialties",
    "Other Consumer Specialties",
    "Movies/Entertainment",
    "Medical Specialties",
    "Office Equipment/Supplies",
    "Electronics/Appliances",
    "Pulp & Paper",
    "Electrical Products",
    "Alternative Power Generation"
]

dataDict = {}
grouped_dict = {}
for key, value in industryDict.items():
    if value in ignoreList: continue
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
    if symbol in optignoreList: continue
    if symbol not in dataDictUS: continue
    if symbol not in optionList: continue
    if symbol not in new_dict: continue
    if symbol not in assetDict: continue
    if symbol not in liabilitiesDict: continue
    if assetDict[symbol] < liabilitiesDict[symbol]/30: continue
    npArr = dataDictUS[symbol]
    if len(npArr) < length: continue
    dataDict[symbol] = npArr

balance = Backtest(dataDict, length, new_dict, debtDict,
    inventoryDict, netIncomeDict, treasurySharesDict)


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