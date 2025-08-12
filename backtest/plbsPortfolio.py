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
from modules.data import GetDataWithVolumeDate

def GetBias(npArr, period):
    closeArr = npArr[:,3]
    sma25 = SmaArr(closeArr, period)
    bias25 = (closeArr-sma25)/closeArr
    return bias25

similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
# shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
gennhairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/gennhairisk.p"
gerakuriskPath = f"{rootPath}/backtest/pickle/pro/compressed/gerakurisk.p"
# zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
# kaitennritsuPath = f"{rootPath}/backtest/pickle/pro/compressed/dekidakakaitennritsu.p"
haitoukakutsukePath = f"{rootPath}/backtest/pickle/pro/compressed/haitoukakutsuke.p"
haitourimawarirankPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawarirank.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
kiboriskPath = f"{rootPath}/backtest/pickle/pro/compressed/kiborisk.p"
fusairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/fusairisk.p"
# inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
# netIncomeQPath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeQJP.p"
operatingPath = f"{rootPath}/backtest/pickle/pro/compressed/operatingJP.p"
investementPath = f"{rootPath}/backtest/pickle/pro/compressed/investementJP.p"
freeCashFlowPath = f"{rootPath}/backtest/pickle/pro/compressed/freeCashFlowJP.p"
# treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
# ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
totalSharesPath = f"{rootPath}/backtest/pickle/pro/compressed/totalSharesJP.p"
interestExpensePath = f"{rootPath}/backtest/pickle/pro/compressed/interestExpenseJP.p"
operatingIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/operatingIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
plPath = f"{rootPath}/backtest/pickle/pro/compressed/pl.p"
seichouPath = f"{rootPath}/backtest/pickle/pro/compressed/seichou.p"
eventPath = f"{rootPath}/backtest/pickle/pro/compressed/event.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
ignorePathJP = f"{rootPath}/data/IgnoreJPLts.csv"

rironkabukaDict, financialScoreDict, financialDetailDict = {}, {}, {}
rironkabukaDict = LoadPickle(rironkabukaPath)
plbsDict = LoadPickle(plbsPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
# financialScoreDict = LoadPickle(financialScorePath)
financialDetailDict = LoadPickle(financialDetailPath)
# shuuekiDict = LoadPickle(shuuekiPath)
shijouDict = LoadPickle(shijouPath)
shijousizeDict = LoadPickle(shijousizePath)
gyoushuDict = LoadPickle(gyoushuPath)
gennhairiskDict = LoadPickle(gennhairiskPath)
gerakuriskDict = LoadPickle(gerakuriskPath)
# zandakaDict = LoadPickle(zandakaPath)
# kaitennritsuDict = LoadPickle(kaitennritsuPath)
haitoukakutsukeDict = LoadPickle(haitoukakutsukePath)
haitourimawarirankDict = LoadPickle(haitourimawarirankPath)
kiboriskDict = LoadPickle(kiboriskPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
fusairiskDict = LoadPickle(fusairiskPath)
# inventoryDict = LoadPickle(inventoryPath)
# netIncomeQDict = LoadPickle(netIncomeQPath)
operatingDict = LoadPickle(operatingPath)
investementDict = LoadPickle(investementPath)
# treasurySharesDict = LoadPickle(treasurySharesPath)
# ordinarySharesDict = LoadPickle(ordinarySharesPath)
totalSharesDict = LoadPickle(totalSharesPath)
interestExpenseDict = LoadPickle(interestExpensePath)
operatingIncomeDict = LoadPickle(operatingIncomePath)
# freeCashFlowDict = LoadPickle(freeCashFlowPath)
# shuuekiriskDict = LoadPickle(shuuekiriskPath)
# haitouseikouriskDict = LoadPickle(haitouseikouriskPath)
# shisannriskDict = LoadPickle(shisannriskPath)
plDict = LoadPickle(plPath)
seichouDict = LoadPickle(seichouPath)
eventDict = LoadPickle(eventPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
ignoreListJP = LoadCsv(ignorePathJP)

financialScoreDict = dict(sorted(financialScoreDict.items(), key=lambda item: item[1], reverse=True))

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
    financialDetailDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    operatingDict, investementDict,
    totalSharesDict,
    interestExpenseDict, operatingIncomeDict, sampleArrJP,
    eventDict
    # ,
    # spyDict, qqqDict, diaDict, iwmDict, tltDict, gldDict,
    # usoDict
    ):
    balance = 1
    biasDict = {}
    # smaDict = {}
    ignoreDict = {}
    for i in range(460, length):
        topPefToAvg = 1
        topSymbol = ""
        topSimilarCompanyMin = 1
        today = sampleArrJP[i][5]
        print(today,i)
        tradeList = []
        for symbol, npArr in dataDict.items():
            ignore = False
            if symbol in ignoreDict:
                if ignoreDict[symbol] < 18: ignore = True
                ignoreDict[symbol] += 1
            if ignore: continue
            noTrade = False
            events = eventDict[symbol].get(today,0)
            if events != 0:
                # if "IR情報" in event:
                # 空売り報告
                # 5%ルール
                # print(event)
                eventLength = len(events)
                sell = False
                for event in events:
                    if "再IN" in event:
                        sell = True
                    elif "5%ルール" in event:
                        sell = True
                    elif "について" in event:
                        sell = True
                    elif "変更" in event:
                        sell = True
                if sell:
                    ignoreDict[symbol] = 0
            # if not karauri: continue
            if npArr[i-1][4] >= npArr[i-2][4]: continue
            if npArr[i-1][3] < 327: continue
            if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
            if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue

            if symbol not in financialDetailDict: continue
            if financialDetailDict[symbol][0] != 0:
                if financialDetailDict[symbol][0] < 3: continue
            # if symbol not in shisannkachiDict: continue
            # if npArr[i-1][3] / shisannkachiDict[symbol] > 7.8: continue
            
            if (
                npArr[i-3][3] / npArr[i-3][0] > 1.21 and
                npArr[i-3][4] / npArr[i-4][4] > 7 and
                npArr[i-3][0] < npArr[i-4][2]
            ): continue

            tradeList.append(symbol)
        tradeListLen = len(tradeList)
        if tradeListLen < 1: continue
        vol = balance/tradeListLen
        balance = 0
        print(tradeList)
        for symbol in tradeList:
            npArr = dataDict[symbol]
            op = npArr[i][0]
            tp = npArr[i][3]
            gain = tp / op * vol
            balance += gain
        print(topSymbol, balance, sampleArrJP[i][5])
        # if (
        #     gain < 1 and 
        #     gyoushuDict[topSymbol] not in bibiGyoushu
        # ):
        #     print(gyoushuDict[topSymbol])
        #     break

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
    dataDict = dataDictUS
else:
    industryDict = GetAttrJP("industry")
    length = len(dataDictJP["9101"])
    assetDict = GetAttrJP("total_current_assets")
    dataDict = dataDictJP

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
    # "Telecommunications Equipment", 
    # "Environmental Services",
    # "Biotechnology",
    "Commercial Printing/Forms",
    "Trucks/Construction/Farm Machinery",
    "Auto Parts: OEM",
    # "Tools & Hardware",
    "Metal Fabrication",
    # "Medical Specialties",
    "Electronics/Appliances"
    # "Pulp & Paper",
    # "Electrical Products"
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


def get_unique_values(dictionary):
    unique_values = []
    
    for value in dictionary.values():
        if value not in unique_values:
            unique_values.append(value)
    
    return unique_values

# gyoushuList = get_unique_values(gyoushuDict)
# print(gyoushuList)
gyoushuList = ['情報通信', '電機', '保険', '精密', 
'輸送用機器', '卸売業', '機械', 
'不動産', 'その他製造', '銀行', '小売業', '医薬品', 
'サービス', 
'化学', '鉱業', '建設', '陸運', '食品', '鉄鋼', 'ゴム', 
'その他金融', '海運', '電力・ガス', 
'証券', '石油', '空運', '非鉄金属', '窯業', '繊維', 
'金属製品', '紙・パルプ', '倉庫・運輸', 
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
assetIgnore = []
for symbol, industry in industryDict.items():
    if symbol not in eventDict: continue
    if symbol not in plbsDict: continue
    plbs = plbsDict[symbol]
    if len(plbs[0]) < 2: continue
    pl = plbs[0][-2]
    
    hokatsuriekiIdx = 5
    epsIdx = 6
    roeIdx = 7
    roaIdx = 8

    hankannhiritsuIdx = 11
    
    plLength = len(pl)
    uriage = 0
    eigyourieki = 0
    keijyourieki = 0
    eigyouriekiritsu = 0
    if plLength == 7: continue
    if plLength == 10: continue
    if plLength == 11: continue
    if plLength == 8:
        keichoushuekiIdx = 1
        keichoushueki = pl[keichoushuekiIdx]
        # if keijyourieki < 1110000000000: continue
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        keijyouriekiIdx = 2
        keijyourieki = pl[keijyouriekiIdx]
    elif plLength == 9:
        eigyoushuekiIdx = 1
        eigyoushueki = pl[eigyoushuekiIdx]
        # if eigyoushueki < 1310000000000: continue
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiritsuIdx = 8
        eigyouriekiIdx = 2
        eigyourieki = pl[eigyouriekiIdx]
        eigyouriekiritsuIdx = 8
        eigyouriekiritsu = pl[eigyouriekiritsuIdx]
    else:
        uriageIdx = 1
        uriage = pl[uriageIdx]
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
        # if gennkaritsu > 95.34: continue
        # hankannhiritsuIdx = 11
        # hankannhiritsu = pl[hankannhiritsuIdx]
    if "*" in str(eigyourieki): continue
    if keijyourieki == "-": continue
    junnrieki = pl[junnriekiIdx]
    hokatsurieki = pl[hokatsuriekiIdx]
    eps = pl[epsIdx]
    roe = pl[roeIdx]
    roa = pl[roaIdx]
    if hokatsurieki == "-": continue
    # if hokatsurieki < 992400000000: continue
    if eps == "-": continue
    if eps == "赤字": continue
    if roe == "赤字": continue
    if roa < 1.27: continue
    # if eigyouriekiritsu < 0.75: continue

    if len(plbs[1]) < 2: continue
    bs = plbs[1][-1]
    bs2 = plbs[1][-2]
    bsLength = len(bs)
    if bsLength != 7 and bsLength != 9: continue
    soushisannIdx = 1
    soushisann = bs[soushisannIdx]
    # if soushisann < 131800000000: continue
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
    if gennkin < 46400000: continue
    cf2 = plbs[2][-2]
    gennkin2 = cf2[6]
    if gennkin2 < 46400000: continue
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

print(len(cleanDataDict))
# sys.exit()
# assetIgnore.sort()
# print(assetIgnore)
# bibiRyuudoumeyasu.sort()
# print(bibiRyuudoumeyasu)
Backtest(
    cleanDataDict, length, similarCompanyDict, 
    financialDetailDict, shisannkachiDict, 
    ryuudoumeyasuDict, shijouDict, gyoushuDict, 
    shijousizeDict, gennhairiskDict, gerakuriskDict, 
    haitoukakutsukeDict, 
    haitourimawarirankDict, haitourimawariDict, 
    kiboriskDict, fusairiskDict,
    operatingDict, investementDict,
    totalSharesDict,
    interestExpenseDict, operatingIncomeDict, sampleArrJP,
    eventDict
    # ,
    # spyDict, qqqDict, diaDict, iwmDict, tltDict, gldDict,
    # usoDict
    )
