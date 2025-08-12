rootPath = "..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv, dump_result_list_to_csv
from numba import range
from datetime import datetime
from datetime import datetime as dt, timedelta
import modules.ib as ibc

s_format = '%Y-%m-%d'

# ibc = ibc.Ib()
# ib = ibc.GetIB(3)

# avalible_cash = ibc.GetAvailableCash() - 1737
# avalible_price = int(avalible_cash)/100
# print(avalible_price)

def GetZandakaHiritsu(symbol, nisshokinDict, ordinarySharesDict):
    nisshokin = nisshokinDict[symbol][0]
    ordinaryShares = ordinarySharesDict[symbol][0]

    return [symbol, (nisshokin[2] - nisshokin[1])/ordinaryShares]

# Buy when high1 break range
def CheckShortSqueeze(symbol, nisshokinDict, ordinarySharesDict, dataDict):

    zandaka = nisshokinDict[symbol][::-1]
    floatShares = ordinarySharesDict[symbol][0]
    npArr = dataDict[symbol]
    dateDict = {item[5]:[item[0],item[1],item[2],item[3],item[4], i] for i, item in enumerate(npArr)}
    zandakaDict = {item[0]:[item[1], item[2]] for item in zandaka}

    urizanTradeList = []
    kaizanList = []
    idx = dateDict.get(zandaka[0][0], 0)[5]
    for i in range(idx, len(npArr)):
        # cleanUrizanTradeList = []
        # cleanKaizanList = []
        # for j, urizanTrade in enumerate(urizanTradeList):
        #     if urizanTrade[2] < 1:
        #         if npArr[i][1] > urizanTrade[0]:
        #             urizanTrade[2] = 1
        #     elif npArr[i][2] <= urizanTrade[1]: continue
        #     cleanUrizanTradeList.append(urizanTrade)
        # urizanTradeList = cleanUrizanTradeList
        # for j, kaizanTrade in enumerate(kaizanList):
        #     if npArr[i][1] > kaizanTrade[0]: continue
        #     cleanKaizanList.append(kaizanTrade)
        # urizanTradeList = cleanUrizanTradeList
        # kaizanList = cleanKaizanList
        date = npArr[i][5]
        if date in zandakaDict:
            currentZandaka = zandakaDict[date]
            if currentZandaka[0] < currentZandaka[1]:
                urizanHiritsu = (currentZandaka[1] - currentZandaka[0]) / floatShares
                urizanTradeList.append([npArr[i][1],npArr[i][2],0,date,urizanHiritsu])
            elif currentZandaka[0] > currentZandaka[1]:
                kaizanHiritsu = (currentZandaka[0] - currentZandaka[1]) / floatShares
                kaizanList.append([npArr[i][1],npArr[i][2],1,date,kaizanHiritsu])

    kaizanDate = ""
    tp = 9999
    if len(kaizanList) > 0:
        for kaizan in kaizanList:
            if kaizan[1] < tp:
                tp = kaizan[1]
                kaizanDate = kaizan[3]

    urizanSignal = []
    for urizanTrade in urizanTradeList:
        if urizanTrade[2] > 0:
            if npArr[-1][3] < urizanTrade[0] and tp - urizanTrade[0] > 5:
                urizanSignal.append(urizanTrade)
    
    res = []
    for urizan in urizanSignal:
        row = [symbol, urizan[0], urizan[1], urizan[3], urizan[4],
            tp, kaizanDate]
        res.append(row)
        
    return [symbol, urizanTradeList, kaizanList]

durLimit = timedelta(days=2)
def CheckDur(zandaka, timeLimit):
    zandakaDate = datetime.strptime(zandaka[0], s_format).date()
    if zandakaDate > timeLimit: return False
    dur = timeLimit - zandakaDate
    if dur < durLimit: return False
    return True


def CleanSignalDict(CleanSignalDict, timeLimit):
    resDict = {}
    for symbol, signal in CleanSignalDict.items():
        arr = []
        for s in signal:
            if CheckDur(s, timeLimit):
                arr.append(s)
        resDict[symbol] = arr
    return resDict

def CheckShortSqueezeOri(symbol, nisshokinDict, ordinarySharesDict, npArr):

    zandaka = nisshokinDict[symbol][::-1]
    # if symbol not in nisshokinDict: return[]
    floatShares = ordinarySharesDict[symbol][0]
    # dateDict = {item[5]:[item[0],item[1],item[2],item[3],item[4], i] for i, item in enumerate(npArr)}
    if len(zandaka) < 1: return []
    # # print(zandaka)
    # zandakaDict = {item[0]:[item[1], item[2]] for item in zandaka}
    

    # urizanTradeList = []
    # kaizanList = []
    # # print(zandaka[0])
    # # print(zandaka[0][0])
    # # print(npArr[0][5])
    # # print(dateDict.get(zandaka[0][0], 0))
    # try:
    #     idx = dateDict.get(zandaka[0][0], 0)[5]
    # except: return []
    # for i in range(idx, len(npArr)):
    #     cleanUrizanTradeList = []
    #     cleanKaizanList = []
    #     for j, urizanTrade in enumerate(urizanTradeList):
    #         if urizanTrade[2] < 1:
    #             if npArr[i][1] > urizanTrade[0]:
    #                 urizanTrade[2] = 1
    #         elif npArr[i][2] <= urizanTrade[1]: continue
    #         cleanUrizanTradeList.append(urizanTrade)
    #     urizanTradeList = cleanUrizanTradeList
    #     for j, kaizanTrade in enumerate(kaizanList):
    #         if npArr[i][1] > kaizanTrade[0]: continue
    #         cleanKaizanList.append(kaizanTrade)
    #     urizanTradeList = cleanUrizanTradeList
    #     kaizanList = cleanKaizanList
    #     date = npArr[i][5]
    #     if date in zandakaDict:
    #         currentZandaka = zandakaDict[date]
    #         if currentZandaka[0] < currentZandaka[1]:
    #             urizanHiritsu = (currentZandaka[1] - currentZandaka[0]) / floatShares
    #             urizanTradeList.append([npArr[i][1],npArr[i][2],0,date,urizanHiritsu])
    #         elif currentZandaka[0] > currentZandaka[1]:
    #             kaizanHiritsu = (currentZandaka[0] - currentZandaka[1]) / floatShares
    #             kaizanList.append([npArr[i][1],npArr[i][2],1,date,kaizanHiritsu])
    # # print(symbol, zandakaTradeList)

    # kaizanDate = ""
    # tp = 9999
    # if len(kaizanList) > 0:
    #     for kaizan in kaizanList:
    #         if kaizan[1] < tp:
    #             tp = kaizan[1]
    #             kaizanDate = kaizan[3]

    # urizanSignal = []
    # for urizanTrade in urizanTradeList:
    #     if urizanTrade[2] > 0:
    #         if npArr[-1][3] < urizanTrade[0] and tp - urizanTrade[0] > 19:
    #             urizanSignal.append(urizanTrade)

    # res = []
    # for urizan in urizanSignal:
    #     row = [symbol, urizan[0], urizan[1], urizan[3], urizan[4],
    #         tp, kaizanDate]
    #     res.append(row)

    # print(zandaka[-1][1],zandaka[-1][2],floatShares,zandaka[-1][0])
    urizanhiritsu = (zandaka[-1][2]-zandaka[-1][1])/floatShares
    # if len(zandaka) < 2:
    #     return []
    # urizanhiritsu = (zandaka[-1][2]-zandaka[-2][2])/(zandaka[-1][1]-zandaka[-2][1]+1)
    # urizanhiritsu = ((zandaka[-1][2]-zandaka[-2][2])-(zandaka[-1][1]-zandaka[-2][1]))/floatShares
    return [symbol, urizanhiritsu]

def main():
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    nisshokinPath = f"{rootPath}/backtest/pickle/pro/compressed/nisshokin.p"
    ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
    ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeDateJP.p"

    rironkabukaDict = LoadPickle(rironkabukaPath)
    nisshokinDict = LoadPickle(nisshokinPath)
    ordinarySharesDict = LoadPickle(ordinarySharesPath)
    ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
    dataDict = LoadPickle(dataPathJP)

    closeDict = GetCloseJP()

    length = len(dataDict["9101"])

    # from modules.aiztradingview import GetAttrJP
    # industryDict = GetAttrJP("industry")

    # ignoreList = [
    #     "Electronic Production Equipment", 
    #     "Telecommunications Equipment", 
    #     "Environmental Services",
    #     "Computer Peripherals",
    #     "Biotechnology",
    #     "Commercial Printing/Forms",
    #     "Trucks/Construction/Farm Machinery",
    #     "Auto Parts: OEM",
    #     "Tools & Hardware",
    #     "Recreational Products",
    #     "Metal Fabrication",
    #     "Forest Products",
    #     "Industrial Specialties",
    #     "Other Consumer Specialties",
    #     "Movies/Entertainment",
    #     "Medical Specialties",
    #     "Office Equipment/Supplies",
    #     "Electronics/Appliances",
    #     "Pulp & Paper",
    #     "Electrical Products",
    #     "Alternative Power Generation"
    # ]

    gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
    gyoushuDict = LoadPickle(gyoushuPath)

    # ignoreSectorFirst = [
    # "紙・パルプ",
    # "鉱業","繊維",
    # "空運","鉄鋼",
    # "保険"]

    # ignoreSector = ["輸送用機器","情報通信",
    #     "鉱業","繊維",
    #     "空運","保険","鉄鋼",
    #     "銀行"]

    ignoreSector = ["鉄鋼"]

    symbolList = []
    for symbol, close in closeDict.items():
        # if close > avalible_price: continue
        if symbol not in rironkabukaDict: continue
        if close >= rironkabukaDict[symbol] - 5: continue
        if symbol not in nisshokinDict: continue
        if symbol not in ordinarySharesDict: continue
        if symbol not in ryuudoumeyasuDict: continue
        if ryuudoumeyasuDict[symbol][0] <= 100: continue

        if symbol not in gyoushuDict: continue
        if gyoushuDict[symbol] in ignoreSector: continue

        # if symbol not in industryDict: continue
        # industry = industryDict[symbol]
        # if industry in ignoreList: continue

        symbolList.append(symbol)

    signalDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckShortSqueeze, symbol, nisshokinDict, ordinarySharesDict, dataDict) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            symbol = result[0]
            urizan = result[1]
            if len(dataDict[symbol]) < length: continue
            if len(urizan) < 1: continue
            kaizan = result[2]
            signalDict[symbol] = [urizan, kaizan]
    # print(signalDict)

    
    today = datetime.now().date()
    startDate = today
    for symbol, l in signalDict.items():
        urizanList = l[0]
        for urizan in urizanList:
            # print(urizan[3])
            
            time = datetime.strptime(urizan[3], s_format).date()
            if time < startDate:
                startDate = time
                # print(time)

    startDateStr = str(startDate)
    # print(startDateStr)

    

    startIdx = 0
    for symbol, l in signalDict.items():
        if startIdx != 0: break
        npArr = dataDict[symbol]
        if len(npArr) < length: continue
        start = False
        
        for i in range(0, len(npArr)):
            if startIdx != 0: break
            if start == False:
                if npArr[i][5] == startDateStr:
                    start = True
                    startIdx=i
                    break
    # print(startIdx)

    cleanDataDict = {}
    for symbol, l in signalDict.items():
        npArr = dataDict[symbol]
        if len(npArr) < length: continue
        npArr = npArr[startIdx:]
        cleanDataDict[symbol] = npArr

    length = len(cleanDataDict["9101"])

    
    balance = 1
    position = 0
    positionSymbol = ""
    op = 0
    sl = 0
    tp = 0
    for i in range(0, length):
        if position < 1:
            todayStr = cleanDataDict["9101"][i][5]
            today = datetime.strptime(todayStr, s_format).date()
            cleanSignalDict = CleanSignalDict(nisshokinDict, today)
            zandakaSignalList = []
            zandakaSignalListNoTp = []
            for symbol, npArr in cleanDataDict.items():
                npArr = npArr[0:i]
                resOri = CheckShortSqueezeOri(symbol, cleanSignalDict, ordinarySharesDict, npArr)
                if len(resOri) < 1: continue
                symbol = resOri[0]
                urizanHiritsu = resOri[1]
                zandakaSignalList.append([symbol, urizanHiritsu])
                # for r in res:
                #     r.append(urizanHiritsu)
                #     # zandakaSignalList.append(r)
                #     # tp = float(r[5])
                #     # op = float(r[1])
                #     # sl = float(r[2])
                #     # rr = (tp-op)/(op-sl)
                #     # r.append(rr)
                #     # if rr < 1: continue
                #     if r[6] != "":
                #         zandakaSignalList.append(r)
                #     else:
                #         zandakaSignalListNoTp.append(r)
            # if len(zandakaSignalList) < 1: continue
            zandakaSignalList.sort(key=lambda zandakaSignalList: zandakaSignalList[-1], reverse=True)
            # zandakaSignalListNoTp.sort(key=lambda zandakaSignalListNoTp: zandakaSignalListNoTp[4], reverse=True)
            # for z in zandakaSignalListNoTp:
            #     zandakaSignalList.append(z)
            positionSymbol = zandakaSignalList[0][0]
            npArr = cleanDataDict[positionSymbol]
            gain = npArr[i][3]/npArr[i][0]
            balance *= gain
        else:
            if cleanDataDict[positionSymbol][i][2] < sl:
                gain = sl/op
                balance *= gain
                position = 0
            elif cleanDataDict[positionSymbol][i][1] > tp:
                gain = tp/op
                balance *= gain
                position = 0
        print(balance)
    # for symbol, npArr in cleanDataDict.items():
    #     print(npArr[0][5])


if __name__ == "__main__":
    main()
