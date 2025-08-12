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

def Backtest(dataDict, length, similarCompanyDict, industryDict, ignoreIndustry):
    ignoreList = []
    for symbol, npArr in dataDict.items():
        industry = industryDict[symbol]
        if industry == ignoreIndustry: 
            ignoreList.append(symbol)
    balance = 1
    for i in range(4, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        for symbol, npArr in dataDict.items():
            if symbol in ignoreList: continue
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            similarPerfomanceList = np.empty(0)
            similarCompanyList = similarCompanyDict[symbol]
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
    return balance

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

def HandleBacktest(cleanDataDict, length, similarCompanyDict, industryDict, ignoreIndustry):
    balance = Backtest(cleanDataDict, length, similarCompanyDict, industryDict, ignoreIndustry)
    return[ignoreIndustry, balance]

group = ""
# group = "US"
if group == "US":
    industryDict = GetAttr("industry")
    length = len(dataDictUS["AAPL"])
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    length = len(dataDictJP["9101"])
    dataDict = dataDictJP

import itertools
count = 3945
industryDict = dict(itertools.islice(industryDict.items(), count))

similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

cleanDataDict = {}
for symbol, industry in industryDict.items():
    if symbol not in dataDict: continue
    if symbol not in similarCompanyDict: continue
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr

grouped_dict = {}
for key, value in industryDict.items():
    if key not in dataDict: continue
    if value not in grouped_dict:
        grouped_dict[value] = [key]
    else:
        grouped_dict[value].append(key)
industryList = list(grouped_dict.keys())
industryList.insert(0,"")
print(industryList)

maxBalance = 1
ignoreDict = {}

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleBacktest, cleanDataDict, length, similarCompanyDict, industryDict, ignoreIndustry) for ignoreIndustry in industryList]
    for future in as_completed(futures):
        result = future.result()
        if len(result) < 2: continue
        balance = result[1]
        if balance <= 1: continue
        industryIgnored = result[0]
        ignoreDict[industryIgnored] = balance
        print(industryIgnored, balance)

# for industry in industryList:
#     balance = Backtest(cleanDataDict, length, similarCompanyDict, industryDict, industry)
#     ignoreDict[industry] = balance

from modules.dict import SortDict
ignoreDict = SortDict(ignoreDict)
print(ignoreDict)