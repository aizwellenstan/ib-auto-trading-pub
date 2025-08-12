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
def split_list_average_low(lst):
    average = np.mean(lst)
    
    low_indices = np.where(lst < average)[0]
    low_values = lst[low_indices]
    average_low = np.mean(low_values)
    
    return np.array([average_low])


def backtest(dataDict, length, similarCompanyDict):
    balance = 1
    for i in range(3, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyAvg = 1
        for symbol, npArr in dataDict.items():
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][1] - npArr[i-1][2] < npArr[i-2][1] - npArr[i-2][2]: continue
            if npArr[i-1][1] - npArr[i-1][2] < npArr[i-3][1] - npArr[i-3][2]: continue
            similarCompanyList = similarCompanyDict[symbol]
            similarPerfomanceList = np.array([dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict])
            
            if len(similarPerfomanceList) == 0:
                continue
            
            # try:
            #     res = split_list_average_low(similarPerfomanceList)
            # except:
            #     continue
            
            # similarCompanyAvg = res[0]
            similarCompanyAvg = np.min(similarPerfomanceList)
            performance = npArr[i][0] / npArr[i-1][3]
            pefToAvg = performance / similarCompanyAvg
            
            if pefToAvg < topPefToAvg:
                topPefToAvg = pefToAvg
                topSymbol = symbol
                topSimilarCompanyAvg = similarCompanyAvg
        
        npArr = dataDict[topSymbol]
        tp = npArr[i][3]
        
        if npArr[i][1] > npArr[i-1][3] * topSimilarCompanyAvg:
            tp = npArr[i-1][3] * topSimilarCompanyAvg
        
        gain = tp / npArr[i][0]
        balance *= gain
    
    return balance


def HandleBacktest(oriIndustryDict, dataDictUS, similarCompanyDict, count):
    industryDict = dict(itertools.islice(oriIndustryDict.items(), count))

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
        
        # if symbol not in floatShareDict: continue
        if symbol not in similarCompanyDict: continue
        if symbol not in new_dict: continue
        npArr = dataDictUS[symbol]
        if len(npArr) < length: continue
        dataDict[symbol] = npArr
    
    try:
        balance = backtest(dataDict, length, similarCompanyDict)
    except: return [count, 0]
    return [count, balance]

floatShareDict = GetAttr("float_shares_outstanding")
industryDict = GetAttr("industry")
assetDict = GetAttr("total_current_assets")
length = len(dataDictUS["AAPL"])

grouped_dict = {}
for key, value in industryDict.items():
    if key not in dataDictUS: continue
    if value not in grouped_dict:
        grouped_dict[value] = [key]
    else:
        grouped_dict[value].append(key)

# industryList = list(grouped_dict.keys())
# for industry in industryList:
#     print(industry)

new_dict = {}

for industry, symbols in grouped_dict.items():
    for symbol in symbols:
        filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
        if len(filtered_symbols) >= 4:
            new_dict.setdefault(symbol, []).extend(filtered_symbols)

similarCompanyDict = new_dict

oriIndustryDict = industryDict



import itertools
maxCount = 50
maxBalance = 1
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleBacktest, oriIndustryDict, dataDictUS, similarCompanyDict, count) for count in range(2, length)]
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
# industryDict = GetAttrJP("industry")
# assetDict = GetAttrJP("total_current_assets")
# length = len(dataDictJP["9101"])

# oriIndustryDict = industryDict

# import itertools
# maxCount = 50
# maxBalance = 1
# with ThreadPoolExecutor(max_workers=100) as executor:
#     futures = [executor.submit(HandleBacktest, oriIndustryDict, dataDictJP, similarCompanyDict, count) for count in range(2, 4303)]
#     for future in as_completed(futures):
#         result = future.result()
#         if len(result) < 2: continue
#         balance = result[1]
#         if balance <= 1: continue
#         count = result[0]
#         if balance > maxBalance:
#             maxBalance = balance
#             maxCount = count
#             print(maxBalance, maxCount)


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