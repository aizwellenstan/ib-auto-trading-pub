rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts
from modules.csvDump import LoadCsv
from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np

floatDictJP = GetAttrJP("float_shares_outstanding")
totalShareDictJP = GetAttrJP("total_shares_outstanding_fundamental")

def GetZandakaHiritsu(symbol, zandakaDict, floatDictJP, totalShareDictJP):
    zandaka = zandakaDict[symbol]
    return zandaka[0][7] / zandaka[0][1]
    urizan_kashitsukezan = zandaka[0][7] - zandaka[0][1]

    floatShares = 0
    if symbol in floatDictJP:
        floatShares = floatDictJP[symbol]
    elif symbol in totalShareDictJP:
        floatShares = totalShareDictJP[symbol]
    zandakaHiritsuTofloatShares = urizan_kashitsukezan/floatShares
    return zandakaHiritsuTofloatShares

similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
gennhairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/gennhairisk.p"
gerakuriskPath = f"{rootPath}/backtest/pickle/pro/compressed/gerakurisk.p"
zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
kaitennritsuPath = f"{rootPath}/backtest/pickle/pro/compressed/dekidakakaitennritsu.p"
haitoukakutsukePath = f"{rootPath}/backtest/pickle/pro/compressed/haitoukakutsuke.p"
haitourimawarirankPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawarirank.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
kiboriskPath = f"{rootPath}/backtest/pickle/pro/compressed/kiborisk.p"
fusairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/fusairisk.p"
inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
netIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
ignorePathJP = f"{rootPath}/data/IgnoreJPLts.csv"

rironkabukaDict, financialScoreDict, financialDetailDict = {}, {}, {}
rironkabukaDict = LoadPickle(rironkabukaPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
# financialScoreDict = LoadPickle(financialScorePath)
financialDetailDict = LoadPickle(financialDetailPath)
shuuekiDict = LoadPickle(shuuekiPath)
shijouDict = LoadPickle(shijouPath)
shijousizeDict = LoadPickle(shijousizePath)
gyoushuDict = LoadPickle(gyoushuPath)
gennhairiskDict = LoadPickle(gennhairiskPath)
gerakuriskDict = LoadPickle(gerakuriskPath)
zandakaDict = LoadPickle(zandakaPath)
kaitennritsuDict = LoadPickle(kaitennritsuPath)
haitoukakutsukeDict = LoadPickle(haitoukakutsukePath)
haitourimawarirankDict = LoadPickle(haitourimawarirankPath)
kiboriskDict = LoadPickle(kiboriskPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
fusairiskDict = LoadPickle(fusairiskPath)
inventoryDict = LoadPickle(inventoryPath)
netIncomeDict = LoadPickle(netIncomePath)
# shuuekiriskDict = LoadPickle(shuuekiriskPath)
# haitouseikouriskDict = LoadPickle(haitouseikouriskPath)
# shisannriskDict = LoadPickle(shisannriskPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
ignoreListJP = LoadCsv(ignorePathJP)

financialScoreDict = dict(sorted(financialScoreDict.items(), key=lambda item: item[1], reverse=True))
# zandakaHiritsu = GetZandakaHiritsu("7721",zandakaDict,floatDictJP,totalShareDictJP)
# print(zandakaHiritsu)
# print(gyoushuDict["2788"])
# dataDict = dataDictUS
# dataDict.update(dataDictJP)

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

def Backtest(dataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict):
    balance = 1
    # ignoreSector = ["鉱業","繊維",
    #     "電ガ","通信","運輸","空運","不動","保険","他金","銀行","小売","卸売","他製","輸送","金製","非鉄","鉄鋼","医薬","紙パ","農水","サビ"]
    positon = 0
    for i in range(4, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        if positon < 1:
            for symbol, npArr in dataDict.items():
                if npArr[i-1][4] >= npArr[i-2][4]: continue
                if (
                    npArr[i-1][4] <= npArr[i-2][4] and
                    npArr[i-2][4] <= npArr[i-3][4] and
                    npArr[i-3][4] <= npArr[i-4][4] and
                    npArr[i-1][3] <= npArr[i-1][0] and
                    npArr[i-2][3] <= npArr[i-2][0] and
                    npArr[i-3][3] / npArr[i-4][0] > 1.1
                ): continue
                if symbol not in financialDetailDict: continue
                if financialDetailDict[symbol][0] != 0:
                    if financialDetailDict[symbol][0] < 3: continue
                if shuuekiDict[symbol] < 0.021: continue
                if symbol not in shisannkachiDict: continue
                if npArr[i-1][3] / shisannkachiDict[symbol] > 7.69: continue
                if symbol not in ryuudoumeyasuDict: continue
                if symbol not in shijouDict: continue
                if shijouDict[symbol] == "東証グロース": continue
                if shijouDict[symbol] == "東証プライム": continue
                if symbol not in gyoushuDict: continue
                if gyoushuDict[symbol] in ignoreSector: continue
                if symbol not in kiboriskDict: continue
                if kiboriskDict[symbol] == 0: continue
                
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
            # shisannkachiTp = shisannkachiDict[topSymbol] * 7.7
            if npArr[i][1] > npArr[i-1][3] * topSimilarCompanyMin:
                tp = npArr[i-1][3] * topSimilarCompanyMin
            # tp = min(shisannkachiTp,tp)
                gain = tp / npArr[i][0]
                balance *= gain
                print(balance)
            else:
                op = npArr[i][0]
                positon = 1
        else:
            closeArr = npArr[:,3]
            sma25 = SmaArr(closeArr, 25)
            if npArr[i][0] < sma25[-1]:
                tp = npArr[i][0]
                gain = tp / op
                balance *= gain
                print(balance)
                positon = 0

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
# group = "US"
if group == "US":
    industryDict = GetAttr("industry")
    length = len(dataDictUS["AAPL"])
    assetDict = GetAttr("total_current_assets")
    liabilitiesDict = GetAttr("total_liabilities_fy")
    roaDict = GetAttr("return_on_assets")
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    length = len(dataDictJP["9101"])
    assetDict = GetAttrJP("total_current_assets")
    liabilitiesDict = GetAttrJP("total_liabilities_fy")
    roaDict = GetAttrJP("return_on_assets")
    dataDict = dataDictJP

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

closeDictJP = GetCloseJP()
ignoreSector = ["輸送用機器","情報通信",
        "鉱業","繊維",
        "空運","保険","鉄鋼",
        "銀行"]
ignoreSectorFirst = [
    "紙・パルプ",
    "鉱業","繊維",
    "空運","鉄鋼",
    "保険"]

def get_unique_values(dictionary):
    unique_values = []
    
    for value in dictionary.values():
        if value not in unique_values:
            unique_values.append(value)
    
    return unique_values

# gyoushuList = get_unique_values(gyoushuDict)
# print(gyoushuList)
gyoushuList = ['情報通信', '電機', '保険', '精密', '輸送用機器', '卸売業', '機械', 
'不動産', 'その他製造', '銀行', '小売業', '医薬品', 'サービス', 
'化学', '鉱業', '建設', '陸運', '食品', '鉄鋼', 'ゴム', 'その他金融', '海運', '電力・ガス', 
'証券', '石油', '空運', '非鉄金属', '窯業', '繊維', '金属製品', '紙・パルプ', '倉庫・運輸', 
'水産・農林']
for symbol, industry in industryDict.items():
    if symbol not in dataDict: continue
    if symbol not in similarCompanyDict: continue
    if symbol not in rironkabukaDict: continue
    if symbol not in shuuekiDict: continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSectorFirst: continue
    if industry in ignoreList: continue
    if symbol not in zandakaDict: continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if zandaka[0][1] < 900: continue
    if symbol not in haitourimawariDict: continue
    if haitourimawariDict[symbol] > 0.033: continue
    if symbol not in assetDict: continue
    if symbol not in liabilitiesDict: continue
    if assetDict[symbol] < liabilitiesDict[symbol]/30: continue
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr

Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict)
