rootPath = "..";import sys;sys.path.append(rootPath)
from modules.data import GetDataWithVolumeDate
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

def HandleGetDataWithVolumeDate(symbol):
    npArr = GetDataWithVolumeDate(symbol)
    return [symbol, npArr]

def main():
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeDateJP.p"
    closeDictJP = GetCloseJP()
    symbolList = list(closeDictJP.keys())
    dataDictJP = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetDataWithVolumeDate, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            npArr = result[1]
            if len(npArr) < 1: continue
            dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(dataPathJP, "wb"))

if __name__ == "__main__":
    main()
