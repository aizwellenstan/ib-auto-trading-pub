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

def Backtest(dataDict, length, similarCompanyDict, debtDict, marketCapDict):
    balance = 1
    for i in range(4, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        for symbol, npArr in dataDict.items():
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            similarPerfomanceList = np.empty(0)
            similarCompanyList = similarCompanyDict[symbol]
            marginList = np.empty(0)
            if symbol not in debtDict: continue
            if symbol not in marketCapDict: continue
            # if debtDict[symbol] > 4927745171*100: continue
            # if debtDict[symbol]/marketCapDict[symbol] >= 0.0177279325139886: continue
            similarPerfomanceList = np.array([dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict])
            if len(similarPerfomanceList) < 1: continue
            similarCompanyMin = np.min(similarPerfomanceList)
            performance = npArr[i][0] / npArr[i-1][3]
            pefToAvg = performance/similarCompanyMin
            if pefToAvg < topPefToAvg:
                topPefToAvg = pefToAvg
                topSymbol = symbol
                topSimilarCompanyMin = similarCompanyMin
        if topSymbol == "": continue
        npArr = dataDict[topSymbol]
        tp = npArr[i][3]
        if npArr[i][1] > npArr[i-1][3] * topSimilarCompanyMin:
            tp = npArr[i-1][3] * topSimilarCompanyMin
        gain = tp / npArr[i][0]
        balance *= gain
        print(balance)

def GetSimilarCompanyDict(industryDict, dataDict):
    grouped_dict = {}
    for key, value in industryDict.items():
        if key not in dataDict: continue
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
    return new_dict

group = ""
group = "US"
if group == "US":
    industryDict = GetAttr("industry")
    debtDict = GetAttr("total_debt")
    marketCapDict = GetAttr("market_cap_basic")
    length = len(dataDictUS["AAPL"])
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    debtDict = GetAttrJP("total_debt")
    marketCapDict = GetAttrJP("market_cap_basic")
    length = len(dataDictJP["9101"])
    dataDict = dataDictJP

print(debtDict["ASML"]/marketCapDict["ASML"])
# sys.exit()

import itertools
count = 3945
industryDict = dict(itertools.islice(industryDict.items(), count))

similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

cleanDataDict = {}
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
for symbol, industry in industryDict.items():
    if industry in ignoreList: continue
    if symbol not in dataDict: continue
    if symbol not in similarCompanyDict: continue
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr


Backtest(cleanDataDict, length, similarCompanyDict, debtDict, marketCapDict)


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