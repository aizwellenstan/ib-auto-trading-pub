rootPath = "../..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv, dump_result_list_to_csv, load_csv_rows
from numba import range
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(4)


avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

positions = ibc.GetAllPositions()

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
        cleanUrizanTradeList = []
        cleanKaizanList = []
        for j, urizanTrade in enumerate(urizanTradeList):
            if urizanTrade[2] < 1:
                if npArr[i][1] > urizanTrade[0]:
                    urizanTrade[2] = 1
            elif npArr[i][2] <= urizanTrade[1]: continue
            cleanUrizanTradeList.append(urizanTrade)
        urizanTradeList = cleanUrizanTradeList
        for j, kaizanTrade in enumerate(kaizanList):
            if npArr[i][1] > kaizanTrade[0]: continue
            cleanKaizanList.append(kaizanTrade)
        urizanTradeList = cleanUrizanTradeList
        kaizanList = cleanKaizanList
        date = npArr[i][5]
        if date in zandakaDict:
            currentZandaka = zandakaDict[date]
            if currentZandaka[0] < currentZandaka[1]:
                urizanHiritsu = (currentZandaka[1] - currentZandaka[0]) / floatShares
                if urizanHiritsu > 0.013156917822963833:
                    urizanTradeList.append([npArr[i][1],npArr[i][2],0,date,urizanHiritsu])
            elif currentZandaka[0] > currentZandaka[1]:
                kaizanHiritsu = (currentZandaka[0] - currentZandaka[1]) / floatShares
                kaizanList.append([npArr[i][1],npArr[i][2],1,date,kaizanHiritsu])
    # print(symbol, zandakaTradeList)

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
            if npArr[-1][3] < urizanTrade[0] and tp - urizanTrade[0] > 19 and tp != 9999:
                urizanSignal.append(urizanTrade)

    res = []
    for urizan in urizanSignal:
        row = [symbol, urizan[0], urizan[1], urizan[3], urizan[4],
            tp, kaizanDate]
        res.append(row)
        
    return res

def main(update=True):
    urizanPtah = f"{rootPath}/data/Urizan.csv"
    if update:
        print("UPDATE")
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

        gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
        gyoushuDict = LoadPickle(gyoushuPath)

        ignoreSector = ["鉄鋼"]

        closeDict = GetCloseJP()

        symbolList = []
        for symbol, close in closeDict.items():
            if close > avalible_price: continue
            if symbol not in rironkabukaDict: continue
            if close >= rironkabukaDict[symbol] - 5: continue
            if symbol not in nisshokinDict: continue
            if symbol not in ordinarySharesDict: continue
            if symbol not in ryuudoumeyasuDict: continue
            if symbol not in gyoushuDict: continue
            if gyoushuDict[symbol] in ignoreSector: continue
            if ryuudoumeyasuDict[symbol][0] <= 100: continue
            symbolList.append(symbol)

        zandakaSignalList = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(CheckShortSqueeze, symbol, nisshokinDict, ordinarySharesDict, dataDict) for symbol in symbolList]
            for future in as_completed(futures):
                result = future.result()
                if len(result) < 1: continue
                res = result[0]
                if len(res) < 1: continue
                zandakaSignalList.append(res)

        zandakaSignalList.sort(key=lambda zandakaSignalList: zandakaSignalList[4], reverse=True)
        print(zandakaSignalList)
        header = ["Symbol","High","Low","UriDate","ZandakaHiritsu","Target","KaiDate"]
        dump_result_list_to_csv(zandakaSignalList,urizanPtah,header)
    else:
        zandakaSignalList = load_csv_rows(urizanPtah)

    if not update:
        tradedList = positions
        for zandakaSignal in zandakaSignalList:
            symbol = zandakaSignal[0]
            if symbol in tradedList: continue
            ibc.HandleBuyLimitSlTrail(symbol, 100, float(zandakaSignal[2]), limit=float(zandakaSignal[1]))
            tradedList.append(symbol)

    # zandakaHiritsuPath = f"{rootPath}/data/ZandakaHiritsu.csv"
    # DumpCsv(zandakaHiritsuPath, symbolList)
    # ibc.HandleBuyLimitTpTrailWithContract(contractDict[topSymbol], contractSmartDict[topSymbol], 100, int(target))

if __name__ == "__main__":
    update = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'false':
            update = False
    main(update)
