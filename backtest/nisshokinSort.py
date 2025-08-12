rootPath = "..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.csvDump import DumpCsv

def GetZandakaHiritsu(symbol, nisshokinDict, ordinarySharesDict):
    nisshokin = nisshokinDict[symbol][0]
    ordinaryShares = ordinarySharesDict[symbol][0]

    return [symbol, (nisshokin[2] - nisshokin[1])/ordinaryShares]


def main():
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    nisshokinPath = f"{rootPath}/backtest/pickle/pro/compressed/nisshokin.p"
    ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"

    rironkabukaDict = LoadPickle(rironkabukaPath)
    nisshokinDict = LoadPickle(nisshokinPath)
    ordinarySharesDict = LoadPickle(ordinarySharesPath)

    closeDict = GetCloseJP()

    symbolList = []
    for symbol, close in closeDict.items():
        if symbol not in rironkabukaDict: continue
        if close >= rironkabukaDict[symbol] - 5: continue
        if symbol not in nisshokinDict: continue
        if symbol not in ordinarySharesDict: continue
        symbolList.append(symbol)

    zandakaHiritsuDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetZandakaHiritsu, symbol, nisshokinDict, ordinarySharesDict) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            zandakaHiritsu = result[1]
            if zandakaHiritsu <= 0: continue
            zandakaHiritsuDict[symbol] = zandakaHiritsu
    nisshokinDict = dict(sorted(nisshokinDict.items(), key=lambda item: item[1], reverse=True))
    print(zandakaHiritsuDict)

    symbolList = list(zandakaHiritsuDict.keys())
    zandakaHiritsuPath = f"{rootPath}/data/ZandakaHiritsu.csv"
    DumpCsv(zandakaHiritsuPath, symbolList)

if __name__ == "__main__":
    main()
