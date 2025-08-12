rootPath = ".."
import sys
sys.path.append(rootPath)
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import numpy as np
from modules.aiztradingview import GetClose, GetCloseJP, GetAttr, GetAttrJP, GetBestGainUS
from modules.rironkabuka import GetRironkabuka
import csv

import math
import pickle

closeDictJP = GetCloseJP()
closeDictUS = GetClose()
symbolList = list(closeDictJP.keys()) + list(closeDictUS.keys())

def GetData(symbol):
    try:
        ticker = symbol
        if ticker in closeDictJP: 
            ticker += ".T"
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Volume"]].to_numpy()
        return [symbol, npArr]
    except: return []

dataDictJP = {}
dataDictUS = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolumeJP.p"
picklePathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolumeUS.p"
def UpdateData():
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetData, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            npArr = result[1]
            if len(npArr) < 1: continue
            if symbol in closeDictJP:
                dataDictJP[symbol] = npArr
            else:
                dataDictUS[symbol] = npArr

update = False
if update:
    UpdateData()
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")
    
    pickle.dump(dataDictUS, open(picklePathUS, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(picklePathUS, "rb")
    dataDictUS = pickle.load(output)
    output.close()

# attrDict = GetAttr("total_shares_outstanding_fundamental")
attrDict = GetAttr("market_cap_basic")
sectorDict = GetAttr("sector")
industryDict = GetAttr("industry")

def GetBestGain(dataDict, attrDict, i):
    bestGainer = ""
    bestGain = 0
    bestFloatShares = 0
    bestVolumeFloat = 0
    highestVolumeFloat = 0
    back = 1
    for symbol, npArr in dataDict.items():
        if len(npArr) < i + back: continue
        gain = npArr[-i][3] / npArr[-i][0]
        if gain > bestGain:
            if npArr[-i-back][4] < 1: continue
            if symbol not in attrDict: continue
            floatShares = attrDict[symbol]
            volumeFloat = npArr[-i-back][4] / floatShares
            bestGain = gain
            bestFloatShares = floatShares
            bestVolumeFloat = volumeFloat
            bestGainer = symbol
    return [bestGainer, bestFloatShares, bestVolumeFloat, i]

length = len(dataDictUS[next(iter(dataDictUS.keys()))])
# for i in range(0, length):
#     bestGainer, volumeFloat = GetBestGain(dataDictUS, attrDict, i)
#     print(bestGainer, volumeFloat)

symbolList = []
sectorList = []
industryList = []
floatSharesList = np.empty(0)
volumeFloatList = np.empty(0)
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(GetBestGain, dataDictUS, attrDict, i) for i in range(0, length-1)]
    for future in as_completed(futures):
        result = future.result()
        bestGainer = result[0]
        floatShares = result[1]
        volumeFloat = result[2]
        i = result[3]
        print(bestGainer, floatShares, volumeFloat, i)
        sector = sectorDict[bestGainer]
        industry = industryDict[bestGainer]
        floatSharesList = np.append(floatSharesList, floatShares)
        volumeFloatList = np.append(volumeFloatList, volumeFloat)
        if bestGainer not in symbolList:
            symbolList.append(bestGainer)
        # if sector not in sectorList:
        sectorList.append(sector)
        # if industry not in industryList:
        industryList.append(industry)

# print(symbolList)
# missing = []
# bestGainDict = GetBestGainUS()
# for symbol in symbolList:
#     if symbol not in bestGainDict:
#         missing.append(symbol)

# attrDict = GetAttr("market_cap_basic")
# missingAttr = []
# for symbol in missing:
#     attr = attrDict[symbol]
#     if attr not in missingAttr:
#         missingAttr.append(symbol)
# missingAttr.sort()
# print(missingAttr)
# print(len(bestGainDict))
# print(np.min(floatSharesList), np.max(floatSharesList))
# print('{0:.10f}'.format(np.min(volumeFloatList)), np.max(volumeFloatList))
# print(sectorList)
# print(industryList)

# sectorCountDict = {}
# for sector in sectorList:
#     if sector not in sectorCountDict:
#         sectorCountDict[sector] = 1
#     else:
#         sectorCountDict[sector] += 1
# sectorCountDict = dict(sorted(sectorCountDict.items(), key=lambda item: item[1], reverse=True))
# print(sectorCountDict)

industryCountDict = {}
for industry in industryList:
    if industry not in industryCountDict:
        industryCountDict[industry] = 1
    else:
        industryCountDict[industry] += 1
industryCountDict = dict(sorted(industryCountDict.items(), key=lambda item: item[1], reverse=True))
print(industryCountDict)

# 'Technology Services': 92, 'Finance': 91,

# npArr = dataDictUS["AAPL"]
# print(npArr[-1][4]/attrDict["AAPL"])
# float 611052.0 945973407.8
# volume/floatShares 0.0000035453 12.78313364410371
# [
#     'Producer Manufacturing', 
#     'Technology Services', 
#     'Consumer Services', 
#     'Finance', 
#     'Commercial Services', 
#     'Electronic Technology', 
#     'Health Technology', 
#     'Retail Trade', 
#     'Distribution Services',
#     'Non-Energy Minerals', 
#     'Industrial Services', 
#     'Consumer Non-Durables', 
#     'Consumer Durables', 
#     'Energy Minerals', 
#     'Process Industries', 
#     'Miscellaneous', 
#     'Health Services', 
#     'Transportation', 
#     'Communications'
# ]
# [
#     'Industrial Conglomerates', 
#     'Packaged Software', 
#     'Other Consumer Services', 
#     'Investment Managers', 
#     'Advertising/Marketing Services', 
#     'Aerospace & Defense', 
#     'Medical Specialties', 
#     'Specialty Stores', 
#     'Multi-Line Insurance',
#     'Semiconductors', 
#     'Internet Software/Services', 
#     'Wholesale Distributors', 
#     'Data Processing Services', 
#     'Steel', 
#     'Biotechnology',
#     'Pharmaceuticals: Major', 
#     'Miscellaneous Commercial Services', 
#     'Electronic Components', 
#     'Movies/Entertainment', 
#     'Financial Conglomerates', 
#     'Environmental Services', 
#     'Building Products', 
#     'Finance/Rental/Leasing', 
#     'Real Estate Development', 
#     'Precious Metals', 
#     'Auto Parts: OEM', 
#     'Internet Retail', 
#     'Food: Meat/Fish/Dairy', 
#     'Motor Vehicles', 
#     'Personnel Services', 
#     'Regional Banks', 
#     'Apparel/Footwear Retail', 
#     'Metal Fabrication', 
#     'Life/Health Insurance', 
#     'Electrical Products', 
#     'Office Equipment/Supplies', 
#     'Electronic Production Equipment', 
#     'Oil & Gas Production', 
#     'Home Furnishings', 
#     'Commercial Printing/Forms', 
#     'Chemicals: Agricultural', 
#     'Information Technology Services', 
#     'Real Estate Investment Trusts', 
#     'Agricultural Commodities/Milling', 
#     'Industrial Machinery', 
#     'Investment Trusts/Mutual Funds', 
#     'Savings Banks', 
#     'Services to the Health Industry', 
#     'Electronics/Appliances', 
#     'Marine Shipping', 
#     'Chemicals: Specialty', 
#     'Coal', 
#     'Engineering & Construction',
#     'Chemicals: Major Diversified',
#     'Oilfield Services/Equipment', 
#     'Insurance Brokers/Services', 
#     'Electronic Equipment/Instruments', 
#     'Broadcasting', 
#     'Telecommunications Equipment', 
#     'Medical/Nursing Services', 
#     'Recreational Products', 
#     'Investment Banks/Brokers', 
#     'Food: Specialty/Candy', 
#     'Property/Casualty Insurance', 
#     'Other Consumer Specialties', 
#     'Hotels/Resorts/Cruise lines', 
#     'Trucking', 'Tools & Hardware', 
#     'Major Telecommunications', 
#     'Construction Materials', 
#     'Industrial Specialties', 
#     'Homebuilding', 
#     'Air Freight/Couriers', 
#     'Other Metals/Minerals', 
#     'Consumer Sundries', 
#     'Hospital/Nursing Management', 
#     'Electronics Distributors', 
#     'Integrated Oil'
# ]
# res = GetBestGain(dataDictUS, attrDict, 373)
# print(res)