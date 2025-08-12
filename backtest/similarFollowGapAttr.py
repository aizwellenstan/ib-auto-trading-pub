rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle

from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
sharePath = f"{rootPath}/backtest/pickle/pro/compressed/share.p"
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
shareDict = LoadPickle(sharePath)
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

def GetShare(npArr):
    latestDate = npArr[0][0]
    total = 0
    for i in npArr:
        if i[0] != latestDate: break
        total += i[2]
    return total

def Backtest(dataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict, attrDict, attrLimit):
    balance = 1
    biasDict = {}
    ignoreDict = {}
    for i in range(460, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        today = sampleArrJP[i][5]
        # print(today,i)
        tradeList = []
        for symbol, npArr in dataDict.items():
            if attrDict[symbol] != 0:
                if attrDict[symbol] < attrLimit: continue
            # ignore = False
            # if symbol in ignoreDict:
            #     if ignoreDict[symbol] < 18: ignore = True
            #     ignoreDict[symbol] += 1
            # if ignore: continue
            # noTrade = False
            # events = eventDict[symbol].get(today,0)
            # karauri = False
            # if events != 0:
            #     # if "IR情報" in event:
            #     # 空売り報告
            #     # 5%ルール
            #     # print(event)
            #     eventLength = len(events)
            #     sell = False
            #     for event in events:
            #         if "再IN" in event:
            #             sell = True
            #         elif "5%ルール" in event:
            #             sell = True
            #         elif "について" in event:
            #             sell = True
            #         elif "変更" in event:
            #             sell = True
            #         elif "空売" in event:
            #             karauri = True
            #     if sell:
            #         ignoreDict[symbol] = 0
            # if not karauri: continue
            # if npArr[i-1][4] >= npArr[i-2][4]: continue
            # if npArr[i-1][3] < 327: continue
            # if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
            # if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue

            if symbol not in financialDetailDict: continue
            # if financialDetailDict[symbol][0] != 0:
            #     if financialDetailDict[symbol][0] < 3: continue
            # if symbol not in shisannkachiDict: continue
            # if npArr[i-1][3] / shisannkachiDict[symbol] > 7.8: continue
            
            # if (
            #     npArr[i-3][3] / npArr[i-3][0] > 1.21 and
            #     npArr[i-3][4] / npArr[i-4][4] > 7 and
            #     npArr[i-3][0] < npArr[i-4][2]
            # ): continue

            tradeList.append(symbol)
        tradeListLen = len(tradeList)
        if tradeListLen < 1: continue
        vol = balance/tradeListLen
        balance = 0
        for symbol in tradeList:
            npArr = dataDict[symbol]
            op = npArr[i][0]
            tp = npArr[i][3]
            gain = tp / op * vol
            balance += gain
        # print(topSymbol, balance, sampleArrJP[i][5])
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
    # "Electronic Production Equipment", 
    # "Commercial Printing/Forms",
    # "Trucks/Construction/Farm Machinery",
    # "Auto Parts: OEM",
    # "Tools & Hardware",
    # "Recreational Products",
    # "Metal Fabrication",
    # "Electronics/Appliances"
]

closeDictJP = GetCloseJP()

ignoreSector = [
    "紙・パルプ",
    "鉱業",
    "繊維",
    # "保険",
    "建設",
    "海運",
    # "銀行",
    "輸送用機器",
    "情報通信",
    "精密",
    "電力・ガス",
    "電機",
    "機械",
    "不動産",
    "その他製造",
    "医薬品",
    "化学",
    "食品",
    "ゴム",
    "証券",
    "窯業",
    "金属製品"
    # "空運"
    # "その他金融"
]
attrDict = {}
n225NpArr = GetDataWithVolumeDate("^N225")[-length:]
for symbol, industry in industryDict.items():
    # if symbol not in eventDict: continue
    if symbol not in plbsDict: continue
    plbs = plbsDict[symbol]
    if len(plbs[0]) < 2: continue
    pl = plbs[0][-2]
    
    hokatsuriekiIdx = 5
    epsIdx = 6
    roeIdx = 7
    roaIdx = 8
    
    plLength = len(pl)
    uriage = 0
    eigyourieki = 0
    keijyourieki = 0
    eigyouriekiritsu = 0
    gennkaritsu = 0
    eigyoushueki = 0
    keichoushueki = 0
    if plLength == 7: continue
    if plLength == 10: continue
    if plLength == 11: continue
    if plLength == 8:
        keichoushuekiIdx = 1
        keichoushueki = pl[keichoushuekiIdx]
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        keijyouriekiIdx = 2
        keijyourieki = pl[keijyouriekiIdx]
        junnriekiIdx = 3
    elif plLength == 9:
        eigyoushuekiIdx = 1
        eigyoushueki = pl[eigyoushuekiIdx]
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiIdx = 2
        eigyourieki = pl[eigyouriekiIdx]
        eigyouriekiritsuIdx = 8
        eigyouriekiritsu = pl[eigyouriekiritsuIdx]
    else:
        uriageIdx = 1
        uriage = pl[uriageIdx]
        # if uriage < 117100000000: continue
        eigyouriekiIdx = 2
        eigyourieki = pl[eigyouriekiIdx]
        keijyouriekiIdx = 3
        keijyourieki = pl[keijyouriekiIdx]
        junnriekiIdx = 4
        eigyouriekiritsuIdx = 9
        eigyouriekiritsu = pl[eigyouriekiritsuIdx]
        gennkaritsuIdx = 10
        gennkaritsu = pl[gennkaritsuIdx]
        if gennkaritsu == "-": continue
        hankannhiritsuIdx = 11
        hankannhiritsu = pl[hankannhiritsuIdx]
    if "*" in str(eigyourieki): continue
    if keijyourieki == "-": continue
    junnrieki = pl[junnriekiIdx]
    hokatsurieki = pl[hokatsuriekiIdx]
    eps = pl[epsIdx]
    roe = pl[roeIdx]
    roa = pl[roaIdx]
    if hokatsurieki == "-": continue
    # if int(hokatsurieki) < -133000000000: continue
    if eps == "-": continue
    if eps == "赤字": continue
    if roe == "赤字": continue

    if len(plbs[1]) < 2: continue
    bs = plbs[1][-1]
    bs2 = plbs[1][-2]
    bsLength = len(bs)
    if bsLength != 7 and bsLength != 9: continue
    soushisannIdx = 1
    soushisann = bs[soushisannIdx]
    junnshisanIdx = 2
    kabunushishihonnIdx = 3
    riekijouyokinIdx = 5
    junnshisan = int(bs[junnshisanIdx])
    junnshisan2 = int(bs2[junnshisanIdx])
    # if junnshisan/junnshisan2 < 0.1: continue
    kabunushishihonn = bs[kabunushishihonnIdx]
    if kabunushishihonn == "-": continue
    riekijouyokin = bs[riekijouyokinIdx]
    if riekijouyokin == "-": continue

    cf = plbs[2][-1]
    cfLength = len(cf)
    if cfLength != 8: continue
    eigyoucf = int(cf[1])
    # if eigyoucf < -13000000000: continue
    toushicf = cf[2]
    if toushicf == "-": continue
    gennkin = cf[6]
    # if gennkin < 46400000: continue
    cf2 = plbs[2][-2]
    gennkin2 = cf2[6]
    # if gennkin2 < 46400000: continue
    eigyoucfmargin = cf[7]
    if eigyoucfmargin == "-": continue

    if len(plbs[3]) < 1: continue
    dividend = plbs[3][-1]
    dividendLength = len(dividend)
    if dividendLength == 2: continue
    if dividendLength == 3: continue
    if dividendLength == 6: continue
    if dividendLength == 7: continue
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
            
    if symbol not in dataDict: continue
    # if symbol not in similarCompanyDict: continue
    if symbol not in rironkabukaDict: continue
    if symbol not in gyoushuDict: continue
    # if gyoushuDict[symbol] in ignoreSector: continue
    # if industry in ignoreList: continue
    if symbol not in haitourimawariDict: continue
    # if haitourimawariDict[symbol] > 0.032: continue
    if symbol not in shareDict: continue
    share = GetShare(shareDict[symbol])

    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr
    c = 0
    for i in range(0, length):
        if (
            n225NpArr[i][3] < n225NpArr[i][0] and
            npArr[i][3] > npArr[i][0]
        ): c += 1
    
    attrDict[symbol] = c/length

def HandleBacktest(cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict, attrDict, attrLimit):
    balance = Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict, attrDict, attrLimit
    )
    return [balance, attrLimit]

# Backtest(
#     cleanDataDict, length, similarCompanyDict, 
#     financialDetailDict, shisannkachiDict, 
#     sampleArrJP,
#     eventDict, attrDict
#     )

attrList = list(attrDict.values())
print(attrList)
attrList.sort()
# attrList.sort(reverse=True)
maxBalance = 1
maxLimit = 0
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleBacktest, cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    sampleArrJP,
    eventDict, attrDict, attrLimit) for attrLimit in attrList]
    for future in as_completed(futures):
        result = future.result()
        if len(result) < 2: continue
        balance = result[0]
        if balance <= 1: continue
        limit = result[1]
        if balance > maxBalance:
            maxBalance = balance
            maxLimit = limit
            print(maxBalance, maxLimit)
