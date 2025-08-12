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
from modules.rsi import GetRsi
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def GetBias(npArr, period):
    closeArr = npArr[:,3]
    sma25 = SmaArr(closeArr, period)
    bias25 = (closeArr-sma25)/closeArr
    return bias25

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
operatingPath = f"{rootPath}/backtest/pickle/pro/compressed/operatingJP.p"
investementPath = f"{rootPath}/backtest/pickle/pro/compressed/investementJP.p"
freeCashFlowPath = f"{rootPath}/backtest/pickle/pro/compressed/freeCashFlowJP.p"
treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
totalSharesPath = f"{rootPath}/backtest/pickle/pro/compressed/totalSharesJP.p"
interestExpensePath = f"{rootPath}/backtest/pickle/pro/compressed/interestExpenseJP.p"
operatingIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/operatingIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
plPath = f"{rootPath}/backtest/pickle/pro/compressed/pl.p"
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
operatingDict = LoadPickle(operatingPath)
investementDict = LoadPickle(investementPath)
treasurySharesDict = LoadPickle(treasurySharesPath)
ordinarySharesDict = LoadPickle(ordinarySharesPath)
totalSharesDict = LoadPickle(totalSharesPath)
interestExpenseDict = LoadPickle(interestExpensePath)
operatingIncomeDict = LoadPickle(operatingIncomePath)
# freeCashFlowDict = LoadPickle(freeCashFlowPath)
# shuuekiriskDict = LoadPickle(shuuekiriskPath)
# haitouseikouriskDict = LoadPickle(haitouseikouriskPath)
# shisannriskDict = LoadPickle(shisannriskPath)
plDict = LoadPickle(plPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
ignoreListJP = LoadCsv(ignorePathJP)

financialScoreDict = dict(sorted(financialScoreDict.items(), key=lambda item: item[1], reverse=True))
# zandakaHiritsu = GetZandakaHiritsu("7721",zandakaDict,floatDictJP,totalShareDictJP)
# print(zandakaHiritsu)
# print(gyoushuDict["2788"])
# dataDict = dataDictUS
# dataDict.update(dataDictJP)
# print(freeCashFlowDict["9827"])
# totalShares = totalSharesDict[symbol]
# treasuryShares = treasurySharesDict[symbol]
# print((treasuryShares[0]/totalShares[0])/(treasuryShares[1]/totalShares[1]))
# print(zandakaDict[symbol][0][7]/zandakaDict[symbol][0][1])
# urizan = zandakaDict[symbol][0][3]
# print(urizan)
# urizan1 = zandakaDict[symbol][0][3]
# if urizan1 < 1: urizan1 = 1
# urizan2 = zandakaDict[symbol][1][3]
# if urizan2 < 1: urizan2 = 1
# print(zandakaDict[symbol][0][1]/urizan1)
# print(zandakaDict[symbol][1][1]/urizan2)
# symbol = "9827"
# zandaka = zandakaDict[symbol]
# print(ordinarySharesDict[symbol][0])
# print((zandaka[0][1]-zandaka[0][3])/ordinarySharesDict[symbol][0])
# print(zandaka[0][1]/ordinarySharesDict[symbol][0])
# print(zandaka[1][1]/ordinarySharesDict[symbol][0])
# sys.exit()

# @njit
def round_down_to_multiple_of_10(number):
    return (number // 10) * 10

# @njit
def round_up_to_multiple_of_100(number):
    remainder = number % 100
    if remainder == 0:
        return number
    else:
        return number + (100 - remainder)

def Backtest(dataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict,
    operatingDict, investementDict,
    treasurySharesDict, totalSharesDict,
    gorssMarginDict,
    interestExpenseDict, operatingIncomeDict):
    balance = 1
    biasDict = {}
    # smaDict = {}
    for i in range(26, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        for symbol, npArr in dataDict.items():
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][3] < 327: continue
            if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
            if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue
            # if symbol not in smaDict:
            #     sma202 = SmaArr(npArr[:,3], 202)
            #     smaDict[symbol] = sma202
            # else:
            #     sma202 = smaDict[symbol]
            # if npArr[i-1][3] < sma202[i-1]: continue
            # if symbol not in ryuudoumeyasuDict: continue
            # if ryuudoumeyasuDict[symbol][0] <= 100: continue
            # treasuryShares = treasurySharesDict[symbol]
            # if treasuryShares[0] < treasuryShares[1]: continue
            
            # if symbol not in totalSharesDict: continue
            # totalShares = totalSharesDict[symbol]
            # if treasuryShares[0]/totalShares[0] >= 0.028996217057202203: continue
            
            # if (
            #     npArr[i-1][4] <= npArr[i-2][4] and
            #     npArr[i-2][4] <= npArr[i-3][4] and
            #     npArr[i-3][4] <= npArr[i-4][4] and
            #     npArr[i-1][3] <= npArr[i-1][0] and
            #     npArr[i-2][3] <= npArr[i-2][0] and
            #     npArr[i-3][3] / npArr[i-4][0] > 1.1
            # ): continue
            if symbol not in financialDetailDict: continue
            if financialDetailDict[symbol][0] != 0:
                if financialDetailDict[symbol][0] < 3: continue
            # if shuuekiDict[symbol] < 0.02: continue
            if symbol not in shisannkachiDict: continue
            if npArr[i-1][3] / shisannkachiDict[symbol] > 7.69: continue
            # if symbol not in shijouDict: continue
            # if shijouDict[symbol] == "東証プライム": continue
            if symbol not in gyoushuDict: continue
            if gyoushuDict[symbol] in ignoreSector: continue

            # if (
            #     npArr[i-3][3] / npArr[i-3][0] > 1.21 and
            #     npArr[i-3][4] / npArr[i-4][4] > 7 and
            #     # npArr[i-1][3] < npArr[i-2][2] and
            #     # npArr[i-1][3] < npArr[i-3][3] and
            #     # npArr[i-1][1] < npArr[i-2][1] and
            #     # npArr[i-1][3] / npArr[i-1][0] < 0.91 and
            #     # abs(npArr[i-3][3] - npArr[i-3][0]) / 
            #     # abs(npArr[i-4][3] - npArr[i-4][0]) > 20 and
            #     npArr[i-3][0] < npArr[i-4][2]
            # ): continue
            
            # if (
            #     symbol in netIncomeDict and
            #     symbol in inventoryDict
            # ):
            #     netIncome = netIncomeDict[symbol]
            #     inventory = inventoryDict[symbol]
            #     if (
            #         len(inventory) > 2 and
            #         len(netIncome) > 2 and
            #         inventory[0] > inventory[1] and
            #         inventory[1] > inventory[2] and
            #         netIncome[0] < netIncome[1] and
            #         netIncome[1] < netIncome[2]
            #     ): continue
            
            similarPerfomanceList = np.empty(0)
            similarCompanyList = similarCompanyDict[symbol]
            similarPerfomanceList = np.array([dataDict[t][i][0] / dataDict[t][i-1][3] for t in similarCompanyList if t in dataDict])
            if len(similarPerfomanceList) < 1: continue
            similarCompanyMin = np.min(similarPerfomanceList)
            if npArr[i-1][3] * similarCompanyMin - npArr[i][0] < 16: continue
            performance = npArr[i][0] / npArr[i-1][3]
            pefToAvg = performance/similarCompanyMin
            if pefToAvg < topPefToAvg:
                topPefToAvg = pefToAvg
                topSymbol = symbol
                topSimilarCompanyMin = similarCompanyMin
        if topSymbol == "": continue
        npArr = dataDict[topSymbol]
        op = npArr[i][0]
        tp = npArr[i][3]
        # shisannkachiTp = shisannkachiDict[topSymbol] * 7.7
        target = npArr[i-1][3] * topSimilarCompanyMin * 0.99
        if npArr[i][1] > npArr[i-1][3] * target:
            tp = target
        gain = tp / op
        balance *= gain
        print(topSymbol, balance)

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
            if len(filtered_symbols) >= 3:
                new_dict.setdefault(symbol, []).extend(filtered_symbols)
    return new_dict

# @njit
def BacktestWR(npArr):
    win = 0
    loss = 0
    winList = np.empty(0)
    lossList = np.empty(0)
    for i in range(1, len(npArr)):
        if npArr[i-1][4] >= npArr[i-2][4]: continue
        if npArr[i][3] > npArr[i][0]:
            win += 1
            winList = np.append(winList, npArr[i][3]-npArr[i][0])
        else:
            loss += 1
            lossList = np.append(lossList, npArr[i][0]-npArr[i][3])
    wr = win / (win+loss)
    if wr * np.mean(winList) <= (1-wr) * np.mean(lossList):
        wr = 0
    return wr

def HandleBacktestWR(dataDict, symbol):
    npArr = dataDict[symbol]
    wr = BacktestWR(npArr)
    return [symbol, wr]

group = ""
# group = "US"
if group == "US":
    industryDict = GetAttr("industry")
    length = len(dataDictUS["AAPL"])
    assetDict = GetAttr("total_current_assets")
    liabilitiesDict = GetAttr("total_liabilities_fy")
    roaDict = GetAttr("return_on_assets")
    gorssMarginDict = GetAttr("gross_margin")
    netIncomeDict = GetAttr("net_income")
    epsDict = GetAttr("basic_eps_net_income")
    last_annual_revenueDict = GetAttr("last_annual_revenue")
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    length = len(dataDictJP["9101"])
    assetDict = GetAttrJP("total_current_assets")
    liabilitiesDict = GetAttrJP("total_liabilities_fy")
    roaDict = GetAttrJP("return_on_assets")
    gorssMarginDict = GetAttrJP("gross_margin")
    netIncomeDict = GetAttrJP("net_income")
    epsDict = GetAttrJP("basic_eps_net_income")
    last_annual_revenueDict = GetAttrJP("last_annual_revenue")
    price_revenue_ttmDict = GetAttrJP("price_revenue_ttm")
    price_sales_ratioDict = GetAttrJP("price_sales_ratio")
    float_shares_outstandingDict = GetAttrJP("float_shares_outstanding")
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

bibi = [
"7686",
"4485",
"5258",
"8031",
"8058",
"6526",
"7203",
"3561",
"3099",
"3399",
"4911",
"6080",
"7014",
"3697",
"8002",
"6857",
"8766",
"6027",
"7373",
"8001",
"4005",
"4063",
"4185",
"4186",
"8316",
"8424",
"4046",
"6723",
"9432",
"8411",
"8306",
"6890",
"5533",
"3498",
"5401",
"5406",
"9107",
"8750",
"8411",
"4487",
"3083",
"6104",
"7388",
"2222",
"3498",
"5137",
"4413",
"4176",
"4570",
"2884",
"7373",
"7369",
"2651",
"6146",
"9158",
"6305",
"3758",
"4617",
"9552",
"3496",
"4739",
"8136",
"6418",
"6457",
"8002",
"7011",
"5344",
"5122",
"3186",
"4886",
"7687",
"4933",
"7267",
"7246",
"5310",
"5202",
"2340",
"4691",
"7048",
"9346",
"7214",
"3452",
"7532",
"7611",
"6857",
"8306",
"7130",
"7011",
"3097"
]

bibiGyoushu = [
    "サービス",
    "不動産",
    "保険",
    "化学",
    "医薬品",
    "卸売業",
    "小売業",
    "情報通信",
    "機械",
    "窯業",
    "輸送用機器",
    "銀行",
    "電機",
    "食品"
]
bibiRyuudoumeyasu = []
for symbol, industry in industryDict.items():
    if symbol not in plDict: continue
    pl = plDict[symbol]
    if len(pl) < 9: continue
    uriage = pl[0]
    if len(uriage) < 1: continue
    # uriageChange = uriage[0]
    # if uriageChange != "大幅増":
    #     if float(uriageChange) < 0.0036: continue
    # if uriage[1] < 635960000: continue
    eigyourieki = pl[1]
    if len(eigyourieki) < 1: continue
    keijyourieki = pl[2]
    if len(keijyourieki) < 1: continue
    if keijyourieki[1] < -511260000: continue
    # toukijunnrieki = pl[3]
    # if len(toukijunnrieki) < 1: continue
    # try:
    #     int(toukijunnrieki[1])
    # except:
    #     toukijunnrieki[1] = float(toukijunnrieki[1][:-1])
    # if toukijunnrieki[1] < -130395000000: continue
    # soushisan = pl[4]
    # soushisanChange = soushisan[0]
    # if soushisanChange == "赤拡": continue
    junnshisan = pl[5]
    junnshisanChange = junnshisan[0]
    if junnshisanChange == "±0": continue
    if junnshisanChange == "赤転": continue
    if (
        junnshisanChange != "大幅増" and
        junnshisanChange != "黒転" and
        junnshisanChange != "赤拡"
    ):
        if junnshisanChange < -0.2621: continue
    # kabunushishihonn = pl[6]
    # if kabunushishihonn[0] < -0.2703: continue
    cash = pl[8]
    if cash[1] < 61000000: continue
    if symbol not in dataDict: continue
    if symbol not in similarCompanyDict: continue
    if symbol not in rironkabukaDict: continue
    if symbol not in ryuudoumeyasuDict: continue
    if symbol in bibi:
        bibiRyuudoumeyasu.append(ryuudoumeyasuDict[symbol][1])
    # if symbol not in treasurySharesDict: continue
    # treasuryShares = treasurySharesDict[symbol]
    # if len(treasuryShares) < 2: continue
    if symbol not in shuuekiDict: continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSectorFirst: continue
    if industry in ignoreList: continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if zandaka[0][1] < 900: continue
    if symbol not in haitourimawariDict: continue
    if haitourimawariDict[symbol] > 0.033: continue
    if symbol not in assetDict: continue
    if symbol not in liabilitiesDict: continue
    if assetDict[symbol] < liabilitiesDict[symbol]/30: continue
    if netIncomeDict[symbol] < -494355000: continue
    if symbol not in epsDict: continue
    if epsDict[symbol] < -104.8953: continue
    if symbol not in last_annual_revenueDict: continue
    if last_annual_revenueDict[symbol] < 794621000: continue
    if symbol not in price_revenue_ttmDict: continue
    if price_revenue_ttmDict[symbol] > 11.75388472: continue
    if symbol not in price_sales_ratioDict: continue
    if price_sales_ratioDict[symbol] > 12.3398292: continue
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr
# bibiRyuudoumeyasu.sort()
# print(bibiRyuudoumeyasu)
Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shuuekiDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    kaitennritsuDict, haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    inventoryDict, netIncomeDict,
    operatingDict, investementDict,
    treasurySharesDict, totalSharesDict,
    gorssMarginDict,
    interestExpenseDict, operatingIncomeDict)
