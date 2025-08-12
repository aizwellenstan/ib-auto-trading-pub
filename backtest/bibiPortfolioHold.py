rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.data import GetDataLts
from modules.csvDump import LoadCsv
import numpy as np
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
pegPath = f"{rootPath}/backtest/pickle/pro/compressed/peg.p"
valuepegPath = f"{rootPath}/backtest/pickle/pro/compressed/valuepeg.p"
holderPath = f"{rootPath}/backtest/pickle/pro/compressed/holder.p"
growthPath = f"{rootPath}/backtest/pickle/pro/compressed/growth.p"
employeePath = f"{rootPath}/backtest/pickle/pro/compressed/employee.p"
psrPath = f"{rootPath}/backtest/pickle/pro/compressed/psr.p"
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
pegDict = LoadPickle(pegPath)
valuepegDict = LoadPickle(valuepegPath)
holderDict = LoadPickle(holderPath)
growthDict = LoadPickle(growthPath)
employeeDict = LoadPickle(employeePath)
psrDict = LoadPickle(psrPath)
# fusairiskDict = LoadPickle(fusairiskPath)
# inventoryDict = LoadPickle(inventoryPath)
# netIncomeQDict = LoadPickle(netIncomeQPath)
# operatingDict = LoadPickle(operatingPath)
# investementDict = LoadPickle(investementPath)
# treasurySharesDict = LoadPickle(treasurySharesPath)
# ordinarySharesDict = LoadPickle(ordinarySharesPath)
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
def round_down_to_multiple_of_10(number):
    return (number // 10) * 10

# @njit
def round_up_to_multiple_of_100(number):
    remainder = number % 100
    if remainder == 0:
        return number
    else:
        return number + (100 - remainder)

def Backtest(dataDict, length, valuepegDict, gyoushuDict, pegDict):
    balance = 1
    smaDict = {}
    sma4Dict = {}
    ignoreDict = {}
    gyoushuCheckList = ['保険', '精密', 
'機械', 'その他製造', '銀行',  '医薬品', 
'化学', '鉱業', '建設', '陸運', '鉄鋼', 'ゴム', 
'その他金融', '海運', '電力・ガス', 
'証券', '石油', '空運', '非鉄金属', '窯業', 
'金属製品', '紙・パルプ', '倉庫・運輸', '水産・農林']
    tradeList = []
    i = 460
    for symbol, npArr in dataDict.items():
        # peg = pegDict[symbol]
        # idx = -1
        # pegLength = len(peg)
        # for i in range(1, pegLength+1):
        #     if peg[-i][3] != "-":
        #         idx = -i
        #         break
        # riron = peg[-1][1]*float(peg[-1][2])
        # if npArr[-1][3] > riron * 3: continue
        if symbol not in gyoushuDict: continue
        # gyoushu = gyoushuDict[symbol]
        # if gyoushu in gyoushuCheckList:
        #     value = valuepegDict[symbol][0][-1][3]
        #     if "inf" in str(value): continue
        #     if value == "-" or "inf" in str(value):
        #         value = valuepegDict[symbol][0][-2][3]
        #     if npArr[i-1][3] > value*0.975: continue
        # if npArr[i-1][4] < 18700: continue
        # if npArr[i-1][3] < 327: continue
        # if npArr[i-1][3] / npArr[i-1][0] < 0.8540462428: continue
        # if npArr[i-1][3] / npArr[i-2][3] < 0.7722095672: continue
        # if npArr[i-1][3] * npArr[i-1][4] < 23204600: continue

        # # if symbol not in financialDetailDict: continue
        # # if financialDetailDict[symbol][0] != 0:
        # #     if financialDetailDict[symbol][0] < 3: continue
        # # # if symbol not in shisannkachiDict: continue
        # # # if npArr[i-1][3] / shisannkachiDict[symbol] > 7.8: continue
        
        # if (
        #     npArr[i-3][3] / npArr[i-3][0] > 1.21 and
        #     npArr[i-3][4] / npArr[i-4][4] > 7 and
        #     npArr[i-3][0] < npArr[i-4][2]
        # ): continue

        # if symbol not in smaDict:
        #     closeArr = npArr[:,3]
        #     sma200 = SmaArr(closeArr, 200)
        #     smaDict[symbol] = sma200
        #     sma4 = SmaArr(closeArr, 4)
        #     sma4Dict[symbol] = sma4
        # else:
        #     sma200 = smaDict[symbol]
        #     sma4 = sma4Dict[symbol]
        # if npArr[i-1][3] < sma200[i-1]: continue
        # if npArr[i-1][3] < sma4[i-1]: continue
        # if (
        #     sma4[i-2] / sma4[i-3] <
        #     sma4[i-3] / sma4[i-4] and
        #     sma4[i-1] / sma4[i-2] <
        #     sma4[i-2] / sma4[i-3]
        # ): continue
        # if npArr[i-1][2] < npArr[i-3][2]: continue

        # if (
        #     npArr[i-1][3]/npArr[i-1][0] <
        #     npArr[i-2][3]/npArr[i-2][0] and
        #     npArr[i-2][3]/npArr[i-2][0] <
        #     npArr[i-3][3]/npArr[i-3][0] and
        #     npArr[i-1][4] > npArr[i-2][4] and
        #     npArr[i-2][4] > npArr[i-3][4]
        # ): continue

        # if (
        #     npArr[i-1][0] > npArr[i-2][1] and
        #     npArr[i-1][3] < npArr[i-1][0] and
        #     npArr[i-1][4] > npArr[i-2][4]
        # ): continue

        # if (
        #     npArr[i-1][1] > npArr[i-2][1] and
        #     npArr[i-2][3] < npArr[i-2][0] and
        #     npArr[i-1][4] / npArr[i-2][4] > 2
        # ): continue

        tradeList.append(symbol)
    # for symbol in bibi:
    #     tradeList.append(symbol)
    tradeListLen = len(tradeList)
    vol = balance/tradeListLen
    balance = 0
    print(tradeList)
    for symbol in tradeList:
        npArr = dataDict[symbol]
        op = npArr[i][0]
        tp = npArr[-1][3]
        gain = tp / op * vol
        balance += gain
    print(balance)
    # if (
    #     gain < 1
    # ):
    #     print(npArr[i-1][3] * npArr[i-1][4])
    #     break

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

sampleArrJP = dataDictJP["9101"]
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
gyoushuIgnoreList = [
    # '保険', 
    '精密', 
    'その他製造', 
    # '銀行', 
    'サービス', 
    # '鉱業', 
    # '建設', 
    # '陸運', 
    '鉄鋼', 
    # 'ゴム', 
    'その他金融', 
    # '海運', 
    # '電力・ガス', 
    # '証券', 
    # '石油', 
    # '空運', 
    # '窯業', 
    # '金属製品', 
    # '紙・パルプ', 
    # '倉庫・運輸', 
    # '水産・農林'
]
gyoshuPl = []
gyoushuIgnoreList = [
    '精密', 
    'サービス',
    'その他金融'
]
for symbol, npArr in dataDict.items():
    if symbol not in bibi: continue
    # if symbol not in valuepegDict: continue
    # if symbol not in gyoushuDict: continue
    # gyoushu = gyoushuDict[symbol]
    # if gyoushu in gyoushuIgnoreList: continue
    # if symbol not in shijousizeDict: continue
    # shijousize = shijousizeDict[symbol]
    # if shijousize not in shijousizeList: continue
    # if symbol not in plbsDict: continue
    # plbs = plbsDict[symbol]
    # if len(plbs[0]) < 2: continue
    # plIdx = -1
    # plLast = plbs[0][-1][0]
    # if "予" in plLast:
    #     plIdx = -2
    # pl = plbs[0][plIdx]
    
    # plLength = len(pl)
    # # if plLength == 10:
    # #     if gyoushu not in gyoshuPl:
    # #         gyoshuPl.append(gyoushu)
    # #         print(symbol, gyoushu)
    # # continue
    # if plLength not in [12]: continue
    # junnriekiIdx = 4
    # epsIdx = 6
    # roeIdx = 7
    # roaIdx = 8
    # if plLength == 7:
    #     junnriekiIdx = 2
    #     epsIdx = 4
    #     roeIdx = 5
    #     roaIdx = 6
    # elif plLength == 8:
    #     junnriekiIdx = 3
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7
    # elif plLength == 9:
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7
    # elif plLength == 11:
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7

    # junnrieki = pl[junnriekiIdx]
    # if junnrieki < 1: continue

    # # eps = pl[epsIdx]
    # # if eps == "-": continue
    # # if eps == "赤字": continue

    # roe = pl[roeIdx]
    # if roe == "-": continue
    # if roe != "赤字":
    #     if roe < 5.5: continue

    # # roa = pl[roaIdx]
    # # if roa != "赤字":
    # #     if roa < 1.53: continue

    # # if plLength in [7, 10, 11, 12]:
    # #     uriageIdx = 1
        
    # #     uriage = pl[uriageIdx]
    # #     if uriage < 123000000: continue

    # if plLength in [9, 10, 11, 12]:
    #     eigyouriekiIdx = 2
    #     eigyouriekiritsuIdx = 9
    #     if plLength == 9:
    #         eigyouriekiritsuIdx = 8
    #     elif plLength == 10:
    #         eigyouriekiritsuIdx = 8
    #     elif plLength == 11:
    #         eigyouriekiritsuIdx = 8

    #     eigyourieki = pl[eigyouriekiIdx]
    #     if eigyourieki == "-": continue
    #     if "*" in str(eigyourieki): continue
    #     # if eigyourieki < -257000000: continue

    #     # eigyouriekiritsu = pl[eigyouriekiritsuIdx]
    #     # if eigyouriekiritsu == "-": continue
    #     # if eigyouriekiritsu == "赤字": continue
    #     # if eigyouriekiritsu < -9.26: continue

    #     eigyourieki2 = 0
    #     if len(plbs[0]) < 3: continue
    #     pl2 = plbs[0][-3]
    #     eigyourieki2 = pl2[eigyouriekiIdx]
    #     if eigyourieki2 == "-": continue
    #     if "*" in str(eigyourieki): continue
    #     if eigyourieki - eigyourieki2 < -174000000: continue

    # # if plLength in [8, 9, 10, 11, 12]:
    # #     keijyouriekiIdx = 3
    # #     if plLength == 8:
    # #         keijyouriekiIdx = 2

    # #     keijyourieki = pl[keijyouriekiIdx]

    # # if plLength in [7, 8, 10, 12]:
    # #     houkatsuriekiIdx = 5
    # #     if plLength == 7:
    # #         houkatsuriekiIdx = 3
    # #     elif plLength == 8:
    # #         houkatsurieki = 4

    # #     houkatsurieki = pl[houkatsuriekiIdx]
    # #     if houkatsurieki == "-": continue
    # #     if houkatsurieki < -302000000: continue

    # # if plLength in [11, 12]:
    # #     gennkaritsuIdx = 10
    # #     hannkannhiritsuIdx = 11
    # #     if plLength == 11:
    # #         gennkaritsuIdx = 9
    # #         hannkannhiritsuIdx = 10

    # #     gennkaritsu = pl[gennkaritsuIdx]
    # #     if gennkaritsu == "-": continue
    # #     if gennkaritsu > 83.64: continue

    # #     hannkannhiritsu = pl[hannkannhiritsuIdx]
    # #     if hannkannhiritsu == "-": continue

    # if len(plbs[1]) < 2: continue
    # bs = plbs[1][-1]
    # bs2 = plbs[1][-2]
    # bsLength = len(bs)
    # # if bsLength not in [7, 9]: continue

    # junnshisanIdx = 2

    # # junnshisan = bs[junnshisanIdx]
    # # if junnshisan < 85100000: continue

    # if bsLength in [6, 7, 8, 9]:
    #     soushisannIdx = 1
    #     kabunushishihonnIdx = 3
    #     jikoushihonritsuIdx = 4
    #     bpsIdx = 8
    #     if bsLength == 8:
    #         bpsIdx = 7
    #     elif bsLength == 7:
    #         bpsIdx = 6
    #     elif bsLength == 6:
    #         bpsIdx = 5

    # #     soushisann = bs[soushisannIdx]
    # #     if soushisann < 169000000: continue

    # #     kabunushishihonn = bs[kabunushishihonnIdx]
    # #     if kabunushishihonn == "-": continue
    # #     if kabunushishihonn < 81700000: continue
    
    # #     jikoushihonritsu = bs[jikoushihonritsuIdx]
    # #     if jikoushihonritsu < 8.5: continue

    # #     bps = bs[bpsIdx]
    # #     if bps < 57.32: continue

    # if bsLength in [7, 9]:
    #     riekijouyokinIdx = 5

    #     riekijouyokin = bs[riekijouyokinIdx]
    #     if riekijouyokin == "-": continue

    # # if bsLength in [4, 8, 9]:
    # #     yuurishifusaiIdx = 6

    # #     if bsLength == 8:
    # #         yuurishifusaiIdx = 5
    # #     elif bsLength == 4:
    # #         yuurishifusaihiritsuIdx = 3

    # #     yuurishifusai = bs[yuurishifusaiIdx]
    # #     if yuurishifusai == "-": continue
    # #     if yuurishifusai < 58400000: continue

    # if bsLength in [8, 9]:
    #     yuurishifusaihiritsuIdx = 7
    #     if bsLength == 8:
    #         yuurishifusaihiritsuIdx = 6

    #     yuurishifusaihiritsu = bs[yuurishifusaihiritsuIdx]
    #     if yuurishifusaihiritsu == "-": continue
    #     if yuurishifusaihiritsu < 13.88: continue

    # # junnshisan = int(bs[junnshisanIdx])
    # # junnshisan2 = int(bs2[junnshisanIdx])
    # # if junnshisan/junnshisan2 < 0.1: continue
    
    # if len(plbs[2]) < 1: continue
    # cf = plbs[2][-1]
    # cfLength = len(cf)
    # # if cfLength != 8: continue

    # gennkinIdx = 6
    # eigyoucfmarginIdx = 7
    # if cfLength == 7:
    #     gennkinIdx = 5
    #     eigyoucfmarginIdx = 6

    # eigyoucf = cf[1]
    # if eigyoucf < -604000000: continue

    # toushicf = cf[2]
    # if toushicf == "-": continue

    # saimucf = cf[3]
    # if saimucf == "-": continue
    # if saimucf < -27900000000: continue

    # # freecf = cf[4]

    # gennkin = cf[gennkinIdx]
    # # if gennkin < 47800000: continue

    # eigyoucfmargin = cf[eigyoucfmarginIdx]
    # if eigyoucfmargin == "-": continue

    # if cfLength == 8:
    #     setsubitoushi = cf[5]
    #     if setsubitoushi == "-": continue
    #     # if setsubitoushi > -5000000: continue
    
    # if len(plbs[3]) < 1: continue
    # dividend = plbs[3][-1]
    # dividendLength = len(dividend)
    # if dividendLength not in [6, 10]: continue

    # if dividendLength in [2, 4, 5, 7, 8, 9, 10]:
    #     ichikabuhaitouIdx = 1

    #     ichikabuhaitou = dividend[ichikabuhaitouIdx]
    #     if ichikabuhaitou == "-": continue
    #     if "*" in str(ichikabuhaitou): continue

    # if dividendLength in [4, 5, 7, 8, 9, 10]:
    #     haitouseikouIdx = 2
    #     haitouseikou = dividend[haitouseikouIdx]
    #     if haitouseikou != "-":
    #         if haitouseikou == "赤字": continue
    #         # if haitouseikou < 8.7: continue

    # if dividendLength in [5, 7, 9, 10]:
    #     jouyokinnhaitouIdx = 3
    #     jouyokinnhaitou = dividend[jouyokinnhaitouIdx]

    # if dividendLength in [4, 5, 10]:
    #     junnshisannhaitouritsuIdx = 4
    #     if dividendLength == 4:
    #         junnshisannhaitouritsuIdx = 3
    #     junnshisannhaitouritsu = dividend[junnshisannhaitouritsuIdx]
    #     if junnshisannhaitouritsu == "赤字": continue
    #     if junnshisannhaitouritsu == "-": continue
    #     # if junnshisannhaitouritsu < 0.5: continue

    # if dividendLength in [6, 8, 9, 10]:
    #     jishakabukaiIdx = 5
    #     soukanngenngakuIdx = 6
    #     soukanngennseikouIdx = 7
    #     if dividendLength == 6:
    #         jishakabukaiIdx = 1
    #         soukanngenngakuIdx = 2
    #         soukanngennseikouIdx = 3
    #     elif dividendLength == 9:
    #         jishakabukaiIdx = 4
    #         soukanngenngakuIdx = 5
    #         soukanngennseikouIdx = 6

    #     jishakabukai = dividend[jishakabukaiIdx]
    #     if "*" in str(jishakabukai): continue
    #     if jishakabukai == "赤字": continue
    #     # if jishakabukai != "-":
    #     #     if jishakabukai < 1300: continue

    #     # soukanngenngaku = dividend[soukanngenngakuIdx]

    #     soukanngennseikou = dividend[soukanngennseikouIdx]
    #     if soukanngennseikou == "赤字": continue

    #     if len(plbs[3]) > 1:
    #         dividend2 = plbs[3][-2]
    #         jishakabukai2 = dividend2[jishakabukaiIdx]
    #         if jishakabukai2 == "赤字": continue

    # if dividendLength in [3, 6, 7, 9, 10]:
    #     kabunushisourimawariIdx = 8
    #     shihyourimawariIdx = 9
    #     if dividendLength == 3:
    #         kabunushisourimawariIdx = 1
    #         shihyourimawariIdx = 2
    #     elif dividendLength == 6:
    #         kabunushisourimawariIdx = 4
    #         shihyourimawariIdx = 5
    #     elif dividendLength == 7:
    #         kabunushisourimawariIdx = 5
    #         shihyourimawariIdx = 6
    #     elif dividendLength == 9:
    #         kabunushisourimawariIdx = 7
    #         shihyourimawariIdx = 8

    #     kabunushisourimawari = dividend[kabunushisourimawariIdx]
    #     if kabunushisourimawari == "-": continue
    #     # if kabunushisourimawari < 18.1: continue
    
    #     shihyourimawari = dividend[shihyourimawariIdx]
    #     if shihyourimawari == "-": continue
    #     if shihyourimawari == "赤字": continue
    #     if shihyourimawari < 81.4: continue
            
    # if symbol not in rironkabukaDict: continue
    # if symbol not in gyoushuDict: continue
    # if symbol not in haitourimawariDict: continue
    # if haitourimawariDict[symbol] > 0.0216: continue
    # if ryuudoumeyasuDict[symbol][0] < 200: continue

    # # if symbol not in holderDict: continue
    # # if len(holderDict[symbol]) < 3: continue
    # # if (
    # #     holderDict[symbol][0][1] > 0.41 and
    # #     ryuudoumeyasuDict[symbol][0] < 1100
    # # ): continue

    # # if (
    # #     holderDict[symbol][0][1] > 0.41 and
    # #     gyoushu == "情報通信"
    # # ): continue


    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    if len(npArr) < length: continue

    # # e = 0
    # # for i in range(0, length):
    # #     if (
    # #         topixNpArr[i][3] < topixNpArr[i][0] and
    # #         npArr[i][3] > npArr[i][0]
    # #     ): e += 1
    # # if e/length < 0.16530278232405893: continue

    # f = 0
    # for i in range(0, length):
    #     if (
    #         npArr[i][3] / npArr[i][0] >
    #         n225NpArr[i][3] / n225NpArr[i][0]
    #     ): f += 1
    # if f / length < 0.45081967213114754: continue

    # # value = valueDict[symbol][-2][1]
    # # if "inf" in str(value): continue
    # # if value == "-":
    # #     value = valueDict[symbol][-3][1]
    # # if value < 208000000: continue

    # # peg = pegDict[symbol]
    # # idx = -1
    # # pegLength = len(peg)
    # # for i in range(1, pegLength+1):
    # #     if peg[-i][3] != "-":
    # #         idx = -i
    # #         break
    # # print(pegDict[symbol],symbol)
    # # riron = peg[-1][1]*float(peg[-1][2])
    # # print(riron)
    # # sys.exit()
    # # if float(peg[idx][3]) > 40: continue


    # # psr = psrDict[symbol]
    # # psr = psr[-1][5]
    # # psr = psr.replace("倍","")
    # # if float(psr) > 15: continue

    # if symbol in growthDict:
    #     growth = growthDict[symbol][0]
    #     junnriekiseichouristuIdx = 3
    #     if len(growth) < 4: continue
        

    #     keijyouriekiseichouritsu3y = 0
    #     keijyouriekiseichouritsu5y = 0

    #     uriageseichouritsu3y = growth[0][0]
    #     eigyouriekiseichoyritsu3y = growth[1][0]
    #     uriageseichouritsu5y = growth[0][1]
    #     eigyouriekiseichoyritsu5y = growth[1][1]

    #     if len(growth) < 4:
    #         junnriekiseichouristuIdx = 2
    #     else:
    #         keijyouriekiseichouritsu3y = growth[2][0]
    #         keijyouriekiseichouritsu5y = growth[2][1]
    #     junnriekiseichouristu3y = growth[junnriekiseichouristuIdx][0]
    #     junnriekiseichouristu5y = growth[junnriekiseichouristuIdx][1]

    #     if uriageseichouritsu5y < 0.0058: continue

    #     growthAll = growthDict[symbol][1]
    #     uriageGrowthAll3y = growthAll[0][1]
    #     eigyouriekiGrowthAll3y = growthAll[1][1]
    #     keijyouriekiGrowthAll3y = growthAll[2][1]
    #     juunriekiGrowthAll3y = growthAll[3][1]
    #     # if uriageGrowthAll3y < 0.9: continue
    #     # if len(growth[0]) > 2:
    #     #     uriageseichouritsu10y = growth[0][2]
    #     #     if uriageseichouritsu10y < 0.0022: continue
    #     # if keijyouriekiseichouritsu5y != 0:
    #     #     if keijyouriekiseichouritsu5y < 0.0308: continue
    #     # if junnriekiseichouristu5y != 0:
    #     #     if junnriekiseichouristu5y < 0.0699: continue

    #     # if gyoushu in seichouIgnoreGyoshuList:
    #     #     if junnriekiseichouristu3y < 0.1449: continue
    #     # if keijyouriekiseichouritsu3y != 0:
    #     #     if keijyouriekiseichouritsu3y < 0.1672: continue

    #     # if uriageseichouritsu3y != 0:
    #     #     if uriageseichouritsu3y < 0.004: continue
    #     # if eigyouriekiseichoyritsu3y != 0:
    #     #     if eigyouriekiseichoyritsu3y < 0.1553: continue
    #     # if keijyouriekiseichouritsu3y != 0:
    #     #     if keijyouriekiseichouritsu3y < 0.1672: continue
    #     # if junnriekiseichouristu3y < 0.1449: continue

    # if symbol not in employeeDict: continue
    # employee = employeeDict[symbol]
    # if len(employee) < 7: continue
    # if (
    #     employee[-6][1] < employee[-7][1] and
    #     employee[-5][1] < employee[-6][1] and
    #     employee[-4][1] < employee[-5][1] and
    #     employee[-3][1] < employee[-4][1] and
    #     employee[-2][1] < employee[-3][1] and
    #     employee[-1][1] < employee[-2][1]
    # ): continue

    # # if int(employee[-1][1])/int(employee[-2][1]) < 0.9589893811790553: continue
    # # employeePerc = 100
    # # if employee[-1][2] != "-":
    # #     employeePerc = int(employee[-1][1])/(int(employee[-1][1])+int(employee[-1][2]))
    # # if employeePerc < 0.24: continue
    # # if int(employee[-1][1]) < 498: continue
    # # if (
    # #     employee[-1][2] == "-"
    # # ): continue

    cleanDataDict[symbol] = npArr

    attr = 1
    # # # # if attr == 0: continue
    # # if attr == "-": continue
    # # if attr == "赤字": continue
    
    if attr not in attrList:
        attrList.append(attr)

    # if gyoushuDict[symbol] not in attrDict:
    #     attrDict[gyoushuDict[symbol]] = [attr]
    # else:
    #     attrList = attrDict[gyoushuDict[symbol]]
    #     attrList.append(attr)
    #     attrList.sort()
    #     attrDict[gyoushuDict[symbol]] = attrList

print(len(cleanDataDict))
attrList.sort()
print(attrList)
print(attrDict)
# sys.exit()
# assetIgnore.sort()
# print(assetIgnore)
# bibiRyuudoumeyasu.sort()
# print(bibiRyuudoumeyasu)
Backtest(cleanDataDict, length, valuepegDict, gyoushuDict, pegDict)
