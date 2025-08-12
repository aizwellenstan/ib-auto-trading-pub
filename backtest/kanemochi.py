rootPath = ".."
import sys
sys.path.append(rootPath)
# from modules.csvDump import load_csv_to_dict
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.data import GetDataLts
from modules.csvDump import LoadCsv
# from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np
# from modules.rsi import GetRsi
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate
from datetime import datetime, timedelta

# similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
# shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
# financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
# shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
# shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
# gennhairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/gennhairisk.p"
# gerakuriskPath = f"{rootPath}/backtest/pickle/pro/compressed/gerakurisk.p"
# zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
# kaitennritsuPath = f"{rootPath}/backtest/pickle/pro/compressed/dekidakakaitennritsu.p"
# haitoukakutsukePath = f"{rootPath}/backtest/pickle/pro/compressed/haitoukakutsuke.p"
# haitourimawarirankPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawarirank.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
holderPath = f"{rootPath}/backtest/pickle/pro/compressed/holder.p"
# kiboriskPath = f"{rootPath}/backtest/pickle/pro/compressed/kiborisk.p"
# fusairiskPath = f"{rootPath}/backtest/pickle/pro/compressed/fusairisk.p"
# inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
# netIncomeQPath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeQJP.p"
# operatingPath = f"{rootPath}/backtest/pickle/pro/compressed/operatingJP.p"
# investementPath = f"{rootPath}/backtest/pickle/pro/compressed/investementJP.p"
# freeCashFlowPath = f"{rootPath}/backtest/pickle/pro/compressed/freeCashFlowJP.p"
# treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
# totalSharesPath = f"{rootPath}/backtest/pickle/pro/compressed/totalSharesJP.p"
# interestExpensePath = f"{rootPath}/backtest/pickle/pro/compressed/interestExpenseJP.p"
# operatingIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/operatingIncomeJP.p"
# shuuekiriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shuuekirisk.p"
# haitouseikouriskPath = f"{rootPath}/backtest/pickle/pro/compressed/haitouseikourisk.p"
# shisannriskPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannrisk.p"
# seichouPath = f"{rootPath}/backtest/pickle/pro/compressed/seichou.p"
# eventPath = f"{rootPath}/backtest/pickle/pro/compressed/event.p"
# sharePath = f"{rootPath}/backtest/pickle/pro/compressed/share.p"
# dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
# ignorePathJP = f"{rootPath}/data/IgnoreJPLts.csv"

rironkabukaDict = LoadPickle(rironkabukaPath)
plbsDict = LoadPickle(plbsPath)
# shisannkachiDict = LoadPickle(shisannkachiPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
# financialScoreDict = LoadPickle(financialScorePath)
# financialDetailDict = LoadPickle(financialDetailPath)
# shuuekiDict = LoadPickle(shuuekiPath)
# shijouDict = LoadPickle(shijouPath)
shijousizeDict = LoadPickle(shijousizePath)
gyoushuDict = LoadPickle(gyoushuPath)
# gennhairiskDict = LoadPickle(gennhairiskPath)
# gerakuriskDict = LoadPickle(gerakuriskPath)
# zandakaDict = LoadPickle(zandakaPath)
# kaitennritsuDict = LoadPickle(kaitennritsuPath)
# haitoukakutsukeDict = LoadPickle(haitoukakutsukePath)
# haitourimawarirankDict = LoadPickle(haitourimawarirankPath)
# kiboriskDict = LoadPickle(kiboriskPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
holderDict = LoadPickle(holderPath)
# fusairiskDict = LoadPickle(fusairiskPath)
# inventoryDict = LoadPickle(inventoryPath)
# netIncomeQDict = LoadPickle(netIncomeQPath)
# operatingDict = LoadPickle(operatingPath)
# investementDict = LoadPickle(investementPath)
# treasurySharesDict = LoadPickle(treasurySharesPath)
ordinarySharesDict = LoadPickle(ordinarySharesPath)
# totalSharesDict = LoadPickle(totalSharesPath)
# interestExpenseDict = LoadPickle(interestExpensePath)
# operatingIncomeDict = LoadPickle(operatingIncomePath)
# freeCashFlowDict = LoadPickle(freeCashFlowPath)
# shuuekiriskDict = LoadPickle(shuuekiriskPath)
# haitouseikouriskDict = LoadPickle(haitouseikouriskPath)
# shisannriskDict = LoadPickle(shisannriskPath)
# seichouDict = LoadPickle(seichouPath)
# eventDict = LoadPickle(eventPath)
# shareDict = LoadPickle(sharePath)
# dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
# ignoreListJP = LoadCsv(ignorePathJP)

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

def Backtest(dataDict, length, percentageDict):
    balance = 1
    smaDict = {}
    sma3Dict = {}
    ignoreDict = {}
    tradeList = []
    for symbol, npArr in dataDict.items():
        if symbol in percentageDict:
            tradeList.append(symbol)
    # for i in range(460, length):
    #     topPerf = 0
    #     topSymbol = ""
    #     today = sampleArrJP[i][5]
        # print(today,i)
        # for symbol, npArr in dataDict.items():
        #     if npArr[i-1][4] < 18700: continue
        #     if npArr[i-1][3] < 327: continue
        #     if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
        #     if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue
        #     if npArr[i-1][3] * npArr[i-1][4] < 23204600: continue

        #     # if symbol not in financialDetailDict: continue
        #     # if financialDetailDict[symbol][0] != 0:
        #     #     if financialDetailDict[symbol][0] < 3: continue
        #     # # if symbol not in shisannkachiDict: continue
        #     # # if npArr[i-1][3] / shisannkachiDict[symbol] > 7.8: continue
            
        #     if (
        #         npArr[i-3][3] / npArr[i-3][0] > 1.21 and
        #         npArr[i-3][4] / npArr[i-4][4] > 7 and
        #         npArr[i-3][0] < npArr[i-4][2]
        #     ): continue

        #     if symbol not in smaDict:
        #         closeArr = npArr[:,3]
        #         sma200 = SmaArr(closeArr, 200)
        #         smaDict[symbol] = sma200
        #         sma3 = SmaArr(closeArr, 3)
        #         sma3Dict[symbol] = sma3
        #     else:
        #         sma200 = smaDict[symbol]
        #         sma3 = sma3Dict[symbol]
        #     if npArr[i-1][3] < sma200[i-1]: continue
        #     if npArr[i-1][3] < sma3[i-1]: continue
        #     if npArr[i-1][2] < npArr[i-2][2]: continue
        #     if npArr[i-1][2] < npArr[i-3][2]: continue

        #     if (
        #         npArr[i-1][3]/npArr[i-1][0] <
        #         npArr[i-2][3]/npArr[i-2][0] and
        #         npArr[i-2][3]/npArr[i-2][0] <
        #         npArr[i-3][3]/npArr[i-3][0] and
        #         npArr[i-1][4] > npArr[i-2][4] and
        #         npArr[i-2][4] > npArr[i-3][4]
        #     ): continue

        #     if (
        #         npArr[i-1][0] > npArr[i-2][1] and
        #         npArr[i-1][3] < npArr[i-1][0] and
        #         npArr[i-1][4] > npArr[i-2][4]
        #     ): continue

        #     if (
        #         npArr[i-1][1] > npArr[i-2][1] and
        #         npArr[i-2][3] < npArr[i-2][0] and
        #         npArr[i-1][4] / npArr[i-2][4] > 2
        #     ): continue

        #     perf = npArr[i-1][3] / npArr[i-2][0]
        #     if perf > topPerf:
        #         topPerf = perf
        #         topSymbol = symbol
        # if topSymbol == "": continue
        # npArr = dataDict[topSymbol]
        # tp = npArr[i][0] * 1.085
        # sl = npArr[i][0] * 0.996
        # if npArr[i][1] > tp:
        #     close = tp 
        # # elif npArr[i][2] < sl:
        # #     close = sl
        # else:
        #     close = npArr[i][3]
        # gain = close / npArr[i][0]
        # balance *= gain
        # tradeListLen = len(tradeList)
        # if tradeListLen < 1: continue
        # vol = balance/tradeListLen

        # lastBalance = balance
        # balance = 1
        # # print(tradeList)
        # total = 0
        # for symbol in tradeList:
        #     npArr = dataDict[symbol]
        #     op = npArr[i][0]
        #     tp = npArr[i][3]
        #     used = lastBalance*percentageDict[symbol]
        #     balance -= used
        #     gain = tp / op * used
        #     balance += gain
        #     total += percentageDict[symbol]
    lastBalance = balance
    balance = 1
    # print(tradeList)
    total = 0
    for symbol in tradeList:
        npArr = dataDict[symbol]
        op = npArr[460][0]
        tp = npArr[-1][3]
        used = lastBalance*percentageDict[symbol]
        balance -= used
        gain = tp / op * used
        balance += gain
        total += percentageDict[symbol]
    return balance

# def GetSimilarCompanyDict(industryDict, dataDict):
#     grouped_dict = {}
#     for key, value in industryDict.items():
#         if key not in dataDict: continue
#         if value not in grouped_dict:
#             grouped_dict[value] = [key]
#         else:
#             grouped_dict[value].append(key)
#     new_dict = {}
#     for industry, symbols in grouped_dict.items():
#         for symbol in symbols:
#             filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
#             if len(filtered_symbols) >= 3:
#                 new_dict.setdefault(symbol, []).extend(filtered_symbols)
#     return new_dict

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
# if group == "US":
#     industryDict = GetAttr("industry")
#     length = len(dataDictUS["AAPL"])
#     dataDict = dataDictUS
# else:
# industryDict = GetAttrJP("industry")
length = len(dataDictJP["9101"])
dataDict = dataDictJP

sampleArrJP = GetDataWithVolumeDate("9101")
sampleArrJP = sampleArrJP[-length:]

# newEventDict = {}
# for symbol, items in eventDict.items():
#     enventDateDict = {}
#     for item in items:
#         if len(item) > 2: continue
#         if item[0] in enventDateDict:
#             enventDateDict[item[0]].append([item[1]])
#         else:
#             enventDateDict[item[0]] = [item[1]]
#     newEventDict[symbol] = enventDateDict
# eventDict = newEventDict

# import itertools
# count = 3945
# industryDict = dict(itertools.islice(industryDict.items(), count))

# similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

cleanDataDict = {}
ignoreList = [
    "Electronic Production Equipment", 
    "Commercial Printing/Forms",
    # "Trucks/Construction/Farm Machinery",
    # "Auto Parts: OEM",
    "Tools & Hardware",
    "Metal Fabrication",
    # "Medical Specialties",
    "Electronics/Appliances"
]

ignoreSector = [
    "紙・パルプ",
    "鉱業",
    "繊維",
    # "保険",
    "建設",
    # "海運",
    # "銀行",
    # "輸送用機器",
    # "情報通信",
    "精密",
    "電力・ガス",
    "電機",
    "機械",
    # "不動産",
    "その他製造",
    # "医薬品",
    # "化学",
    # "食品",
    "ゴム",
    "証券",
    "窯業",
    "金属製品"
    # # "空運"
    # # "その他金融"
]


def get_unique_values(dictionary):
    unique_values = []
    
    for value in dictionary.values():
        if value not in unique_values:
            unique_values.append(value)
    
    return unique_values

def GetShare(npArr):
    total = 0
    for i in npArr:
        total += i[2]
    return total
gyoushuList = ['情報通信', '電機', '保険', '精密', 
'輸送用機器', '卸売業', '機械', 
'不動産', 'その他製造', '銀行', '小売業', '医薬品', 
'サービス', 
'化学', '鉱業', '建設', '陸運', '食品', '鉄鋼', 'ゴム', 
'その他金融', '海運', '電力・ガス', 
'証券', '石油', '空運', '非鉄金属', '窯業', '繊維', 
'金属製品', '紙・パルプ', '倉庫・運輸', 
'水産・農林']

bibi = ['7686', '6526', '3561', '3561', '3561', '3561', '9107', '8136', '3496', '4487', '7014', '4487', '4570', '4487', '6526', '7388', '4570', '3083', '4176', '3697', '7369', '7369', '7369',
'7369', '3561', '6027', '4570', '7369', '8750', '4487', '6526', '4739', '7369', '7687', '4570', '4570', '2222', '4046', '4570', '7214', '7214', '7014', '6526', '4570', '7369', '4570', '3561', '3399',
'5406']

bibiGyoushu = [
    "サービス",
    # "不動産",
    # "保険",
    # "化学",
    # "医薬品",
    "卸売業",
    "小売業",
    "情報通信",
    # "機械",
    # "窯業",
    "輸送用機器"
    # "銀行",
    # "電機",
    # "食品",
    # "鉄鋼"
]
shijousizeList = ['ＰＲＭ大型', 'ＧＲＴ中型', 'ＳＴＤ中型', 'ＰＲＭ中型', 'ＳＴＤ小型', 'ＧＲＴ小型']
bibiRyuudoumeyasu = []
assetIgnore = []
attrList = []
attrDict = {}
# s = []
# for symbol, npArr in dataDict.items():
#     if symbol not in plbsDict: continue
#     plbs = plbsDict[symbol]
#     # if len(plbs[0]) < 2: continue
#     # pl = plbs[0][-2]
#     # plLength = len(pl)

#     # if len(plbs[1]) < 2: continue
#     # bs = plbs[1][-1]
#     # bsLength = len(bs)

#     # if len(plbs[2]) < 1: continue
#     # cf = plbs[2][-1]
#     # cfLength = len(cf)

#     if len(plbs[3]) < 1: continue
#     dividend = plbs[3][-1]
#     dividendLength = len(dividend)

#     if dividendLength  not in attrList:
#         attrList.append(dividendLength)
#         s.append([dividendLength,symbol])
# print(s)
# sys.exit()

# pl [[12, '5820'], [11, '7505'], [8, '8410'], [10, '1949'], [9, '7383'], [7, '7741']]
# bs [[9, '5820'], [7, '3763'], [6, '7751'], [4, '9285'], [8, '4519']]
# cf [[8, '8904'], [7, '8793']]
# df [[10, '9009'], [9, '7751'], [7, '2587'], [6, '6723'], [8, '9147'], [4, '6526'], [3, '4385'], [5, '9336'], [2, '7110']]

# eigyouriekiLimit = {'卸売業': [80300000.0, 13200000000.0], '情報通信': [-114000000.0, 691000000.0], 'サービス': [109000000.0], '小売業': [228000000.0, 514000000.0], '輸送用機器': [214000000.0]}
n225NpArr = dataDictJP["^N225"][-length:]
topixNpArr = dataDictJP["1475"][-length:]
# jpxNpArr = dataDictJP["1591"][-length:]

# def previous_date(date_string):
#     # Convert the input date string to a datetime object
#     date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    
#     # Calculate the previous date by subtracting one day
#     previous_date_obj = date_obj - timedelta(days=1)
    
#     # Convert the previous date object back to a string
#     previous_date_string = previous_date_obj.strftime('%Y-%m-%d')
    
#     return previous_date_string

# spyNpArr = dataDictUS["SPY"]
# spyDict = {item[5]: [item[0],item[1],item[2],item[3],item[4]] for item in spyNpArr}
# spySignalDict = {}
# max_attempts = 10  # Set a maximum number of attempts
# for i in range(0, length):
#     dateKey = previous_date(topixNpArr[i][5])
#     attempts = 0  # Initialize the attempts counter
    
#     while attempts < max_attempts:
#         try:
#             spySignalDict[topixNpArr[i][5]] = spyDict[dateKey]
#             break  # Break out of the loop if successful
#         except KeyError:
#             dateKey = previous_date(dateKey)
#             attempts += 1
#     else:
#         print(f"Max attempts reached for {topixNpArr[i][5]}")  # Print a message if max attempts are reached

# sys.exit()
gyoshuPl = []
holderNameDict = {}
for symbol, npArr in dataDict.items():
    if symbol not in holderDict: continue
    if symbol not in ordinarySharesDict: continue
    ordinaryShares = ordinarySharesDict[symbol][0]
    holders = holderDict[symbol]
    for h in holders:
        holderName = h[0]
        if holderName not in holderNameDict:
            holderNameDict[holderName] = ordinaryShares * h[1] * npArr[-1][3]
        else:
            holderNameDict[holderName] += ordinaryShares * h[1] * npArr[-1][3]

holderNameDict = dict(sorted(holderNameDict.items(), key=lambda item: item[1], reverse=True))
# print(holderNameDict)
from modules.csvDump import dump_result_list_to_csv_utf8
res = []
count = 0
for k, v in holderNameDict.items():
    res.append([k,v])
    # count += 1
    # if count > 100:
    #     break
# cashPath = f"{rootPath}/data/kanemochi.csv"
# header = ["Name","Cash"]
# dump_result_list_to_csv_utf8(res,cashPath,header)
# print(holderNameDict)
def HandleHolder(holder, dataDict, holderDict, ordinarySharesDict, holderNameDict):
    holder = holder[0]
    holderList = [holder]
    cleanDataDict = {}
    percentageDict = {}
    buyList = []
    for symbol, npArr in dataDict.items():
        if symbol not in holderDict: continue
        if symbol not in ordinarySharesDict: continue
        ordinaryShares = ordinarySharesDict[symbol][0]
        holders = holderDict[symbol]
        for h in holders:
            if h[0] in holderList:
                if symbol not in dataDict: continue
                npArr = dataDict[symbol]
                if len(npArr) < length: continue
                cleanDataDict[symbol] = npArr
                perc = ordinaryShares * h[1] * npArr[-1][3] / holderNameDict[holderList[0]]
                percentageDict[symbol] = perc
                buyList.append(symbol)
    print(buyList)
    balance = Backtest(cleanDataDict, length, percentageDict)
    print(holder, balance)
    return [holder, balance]

# holder = ["エイケン工業"]
holder = ["アリスタゴラ・アドバイザーズ"]
HandleHolder(holder, dataDict, holderDict, ordinarySharesDict, holderNameDict)
sys.exit()

from concurrent.futures import ThreadPoolExecutor, as_completed

import math
perfDict = {}
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleHolder, holder, dataDict, holderDict, ordinarySharesDict, holderNameDict) for holder in res]
    for future in as_completed(futures):
        result = future.result()
        if result[1] < 1: continue
        holder = result[0]
        balance = result[1]
        if math.isnan(balance): continue
        perfDict[holder] = balance

perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1], reverse=True))
# print(perfDict)

count = 0
for k, v in perfDict.items():
    print(k, v)
    count += 1
    if count > 50:
        break