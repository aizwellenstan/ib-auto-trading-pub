rootPath="..";import sys;sys.path.append(rootPath)
from modules.irbank import GetNisshokinRank
from modules.loadPickle import LoadPickle
from numba import range

def Backtest(dataDict, nisshokinRankDict, length):
    print(nisshokinRankDict)
    balance = 1
    for i in range(2, length):
        date = dataDict["9101"][i][5]
        signalDate = dataDict["9101"][i-2][5]
        symbol = nisshokinRankDict.get(signalDate,0)
        npArr = dataDict[symbol]
        # if npArr[i-1][4] >= npArr[i-2][4]: continue
        op = npArr[i][0]
        close = npArr[i][3]
        gain = close/op
        balance *= gain
        print(balance, symbol)
        # print(date, signalDate)

def main(update=False):
    nisshokinPath = f"{rootPath}/backtest/pickle/pro/compressed/nisshokinRank.p"
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
    ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeDateJP.p"

    if update:
        import pickle
        nisshokinRank = GetNisshokinRank()
        pickle.dump(nisshokinRank, open(nisshokinPath , "wb"))
    else:
        nisshokinRank = LoadPickle(nisshokinPath)
    rironkabukaDict = LoadPickle(rironkabukaPath)
    ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
    ordinarySharesDict = LoadPickle(ordinarySharesPath)
    dataDict = LoadPickle(dataPathJP)

    length = len(dataDict["9101"])
    cleanDataDict = {}
    for symbol, npArr in dataDict.items():
        if len(npArr) < length: continue
        cleanDataDict[symbol] = npArr

    nisshokinRankDict = {}
    for i in nisshokinRank:
        resList = []
        for d in i[2]:
            symbol = d[0]
            if symbol not in rironkabukaDict: continue
            if symbol not in cleanDataDict: continue
            if symbol not in ordinarySharesDict: continue
            if symbol not in ryuudoumeyasuDict: continue
            # if ryuudoumeyasuDict[symbol][0] <= 100: continue
            ordinaryShares = ordinarySharesDict[symbol][0]
            kaizan = d[1]
            urizan = d[2]
            zandakaHiritsu = (urizan-kaizan)/ordinaryShares
            resList.append([symbol, zandakaHiritsu])
        resList = sorted(resList, key=lambda x: x[1], reverse=True)
        nisshokinRankDict[i[0]] = resList[0][0]
    print(nisshokinRankDict)
    # nisshokinRankDict = {item[0]: item[1] for item in cleanNpArr}
    # print(nisshokinRankDict)

    
    balance = Backtest(cleanDataDict, nisshokinRankDict, length)

if __name__ == "__main__":
    # main(True)
    main()