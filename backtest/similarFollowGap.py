rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle

from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
# ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
# shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
# shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
# shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
# gennhairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/gennhairisk.p"
# gerakuriskPath = f"{rootPath}/backtest/pickle/pro/compressed/gerakurisk.p"
# zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
# kaitennritsuPath = f"{rootPath}/backtest/pickle/pro/compressed/dekidakakaitennritsu.p"
# haitoukakutsukePath = f"{rootPath}/backtest/pickle/pro/compressed/haitoukakutsuke.p"
# haitourimawarirankPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawarirank.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
# kiboriskPath = f"{rootPath}/backtest/pickle/pro/compressed/kiborisk.p"
# fusairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/fusairisk.p"
# inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
# netIncomeQPath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeQJP.p"
# operatingPath = f"{rootPath}/backtest/pickle/pro/compressed/operatingJP.p"
# investementPath = f"{rootPath}/backtest/pickle/pro/compressed/investementJP.p"
# freeCashFlowPath = f"{rootPath}/backtest/pickle/pro/compressed/freeCashFlowJP.p"
# treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
# ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
# totalSharesPath = f"{rootPath}/backtest/pickle/pro/compressed/totalSharesJP.p"
# interestExpensePath = f"{rootPath}/backtest/pickle/pro/compressed/interestExpenseJP.p"
# operatingIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/operatingIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
plPath = f"{rootPath}/backtest/pickle/pro/compressed/pl.p"
# seichouPath = f"{rootPath}/backtest/pickle/pro/compressed/seichou.p"
eventPath = f"{rootPath}/backtest/pickle/pro/compressed/event.p"
# dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"

rironkabukaDict = LoadPickle(rironkabukaPath)
plbsDict = LoadPickle(plbsPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
financialDetailDict = LoadPickle(financialDetailPath)
gyoushuDict = LoadPickle(gyoushuPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
plDict = LoadPickle(plPath)
eventDict = LoadPickle(eventPath)
dataDictJP = LoadPickle(dataPathJP)

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
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict):
    balance = 1
    biasDict = {}
    ignoreDict = {}
    for i in range(460, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        today = sampleArrJP[i][5]
        print(today,i)
        for symbol, npArr in dataDict.items():
            ignore = False
            if symbol in ignoreDict:
                if ignoreDict[symbol] < 18: ignore = True
                ignoreDict[symbol] += 1
            if ignore: continue
            noTrade = False
            events = eventDict[symbol].get(today,0)
        
            if events != 0:
                eventLength = len(events)
                sell = False
                for event in events:
                    if "再IN" in event:
                        sell = True
                    elif "5%ルール" in event:
                        sell = True
                    elif "開示" in event:
                        sell = True
                    elif "について" in event:
                        sell = True
                    elif "状況" in event:
                        sell = True
                    elif "変更" in event:
                        sell = True
                    elif "説明" in event:
                        sell = True
                    elif "による" in event:
                        sell = True
                if sell:
                    ignoreDict[symbol] = 0
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][3] < 327: continue
            if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
            if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue
    
            if symbol not in financialDetailDict: continue
            if financialDetailDict[symbol][0] != 0:
                if financialDetailDict[symbol][0] < 3: continue
            if symbol not in shisannkachiDict: continue
            if npArr[i-1][3] / shisannkachiDict[symbol] > 7.69: continue

            if (
                npArr[i-3][3] / npArr[i-3][0] > 1.21 and
                npArr[i-3][4] / npArr[i-4][4] > 7 and
                npArr[i-3][0] < npArr[i-4][2]
            ): continue
            
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
        target = npArr[i-1][3] * topSimilarCompanyMin * 0.99
        if npArr[i][1] > npArr[i-1][3] * target:
            tp = target
        gain = tp / op
        balance *= gain
        print(topSymbol, balance, sampleArrJP[i][5])

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

group = ""
# group = "US"
if group == "US":
    industryDict = GetAttr("industry")
    length = len(dataDictUS["AAPL"])
    assetDict = GetAttr("total_current_assets")
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    length = len(dataDictJP["9101"])
    assetDict = GetAttrJP("total_current_assets")
    dataDict = dataDictJP

from modules.data import GetDataWithVolumeDate
sampleArrJP = GetDataWithVolumeDate("9101")
sampleArrJP = sampleArrJP[-length:]

newEventDict = {}
for symbol, items in eventDict.items():
    enventDateDict = {}
    for item in items:
        if len(item) > 2: continue
        if item[0] in enventDateDict:
            enventDateDict[item[0]].append([item[1]])
        else:
            enventDateDict[item[0]] = [item[1]]
    newEventDict[symbol] = enventDateDict
eventDict = newEventDict

import itertools
count = 3945
industryDict = dict(itertools.islice(industryDict.items(), count))

similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

cleanDataDict = {}
ignoreList = [
    "Electronic Production Equipment", 
    "Commercial Printing/Forms",
    "Trucks/Construction/Farm Machinery",
    "Auto Parts: OEM",
    "Tools & Hardware",
    "Recreational Products",
    "Metal Fabrication",
    "Electronics/Appliances"
]

closeDictJP = GetCloseJP()

ignoreSector = [
    "紙・パルプ",
    "鉱業",
    "繊維",
    "保険",
    "建設",
    "海運",
    "銀行"
    "輸送用機器",
    "鉄鋼",
    "情報通信",
    "精密",
    "電力・ガス"
]

for symbol, industry in industryDict.items():
    if symbol not in eventDict: continue
    if symbol not in plbsDict: continue
    plbs = plbsDict[symbol]
    if len(plbs[0]) < 2: continue
    pl = plbs[0][-2]
    keijyouriekiIdx = 3
    junnriekiIdx = 4
    hokatsuriekiIdx = 5
    epsIdx = 6
    roeIdx = 7
    roaIdx = 8

    eigyouriekiritsuIdx = 9
    gennkaritsuIdx = 10
    hankannhiritsuIdx = 11
    
    plLength = len(pl)
    if plLength == 11:
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiritsuIdx = 8
        gennkaritsuIdx = 9
        hankannhiritsuIdx = 10
    elif plLength == 8:
        keijyouriekiIdx = 2
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
    elif plLength == 9:
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiritsuIdx = 8
    elif plLength != 12 and plLength != 10:
        if plLength == 7: continue
    keijyourieki = pl[keijyouriekiIdx]
    junnrieki = pl[junnriekiIdx]
    hokatsurieki = pl[hokatsuriekiIdx]
    eps = pl[epsIdx]
    roe = pl[roeIdx]
    roa = pl[roaIdx]
    if keijyourieki == "-": continue
    if eps == "-": continue
    if eps == "赤字": continue

    if len(plbs[1]) < 2: continue
    bs = plbs[1][-1]
    bs2 = plbs[1][-2]
    bsLength = len(bs)
    if bsLength != 7 and bsLength != 9: continue
    junnshisanIdx = 2
    kabunushishihonnIdx = 3
    riekijouyokinIdx = 5
    junnshisan = int(bs[junnshisanIdx])
    junnshisan2 = int(bs2[junnshisanIdx])
    if junnshisan/junnshisan2 < 0.1: continue
    kabunushishihonn = bs[kabunushishihonnIdx]
    if kabunushishihonn == "-": continue
    riekijouyokin = bs[riekijouyokinIdx]
    if riekijouyokin == "-": continue

    cf = plbs[2][-1]
    cfLength = len(cf)
    if cfLength != 8: continue
    eigyoucf = int(cf[1])
    if eigyoucf < -13000000000: continue
    toushicf = cf[2]
    if toushicf == "-": continue
    gennkin = cf[6]
    if gennkin < 47800000: continue
    cf2 = plbs[2][-2]
    gennkin2 = cf2[6]
    if gennkin2 < 47800000: continue
    eigyoucfmargin = cf[7]
    if eigyoucfmargin == "-": continue

    if len(plbs[3]) < 1: continue
    dividend = plbs[3][-1]
    dividendLength = len(dividend)
    if dividendLength == 2: continue
    if dividendLength == 3: continue
    if dividendLength == 8: continue

    if dividendLength in [3, 6, 7, 10]:
        kabunushisourimawariIdx = 9
        shihyourimawariIdx = 9
        if dividendLength == 6:
            kabunushisourimawariIdx = 4
            shihyourimawariIdx = 5
        elif dividendLength == 7:
            kabunushisourimawariIdx = 5
            shihyourimawariIdx = 6
    
        shihyourimawari = dividend[shihyourimawariIdx]
        if shihyourimawari == "赤字": continue

    if dividendLength in [4, 10]:
        junnshisanhaitouritsuIdx = 4
        if dividendLength == 4:
            junnshisanhaitouritsuIdx = 3

        haitouseikouIdx = 2
        haitouseikou = dividend[haitouseikouIdx]

        junnshisanhaitouritsu = dividend[junnshisanhaitouritsuIdx]
        if junnshisanhaitouritsu == "赤字": continue

    jishakabukaiIdx = 5
    if dividendLength in [5, 6, 7, 10]:
        if dividendLength == 5:
            jishakabukaiIdx = 2
        elif dividendLength == 6:
            jishakabukaiIdx = 1
        elif dividendLength == 7:
            jishakabukaiIdx = 2

        jishakabukai = dividend[jishakabukaiIdx]
        if jishakabukai == "赤字": continue
        if "*" in str(jishakabukai): continue

        if len(plbs[3]) > 1:
            dividend2 = plbs[3][-2]
            jishakabukai2 = dividend2[jishakabukaiIdx]
            if jishakabukai2 == "赤字": continue
            if (
                jishakabukai != "-" and 
                jishakabukai2 != "-"
            ):
                if jishakabukai/jishakabukai2 < 2.6e-06: continue

    if symbol not in plDict: continue
    pl = plDict[symbol]
    if len(pl) < 9: continue
    eigyourieki = pl[1]
    if len(eigyourieki) < 1: continue
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
    cash = pl[8]
    if cash[1] < 61000000: continue
    if symbol not in dataDict: continue
    if symbol not in similarCompanyDict: continue
    if symbol not in rironkabukaDict: continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSector: continue
    if industry in ignoreList: continue
    if symbol not in haitourimawariDict: continue
    if haitourimawariDict[symbol] > 0.032: continue

    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr

Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict
    )
