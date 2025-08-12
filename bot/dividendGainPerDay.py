rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseAll, GetCloseJP
from modules.data import GetDataWithDividendsLts
from numba import range, njit
from modules.movingAverage import SmaArr
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
import csv
from modules.portfolio import GetDataShort

def GetDividendGainPerDay(npArr):
    if npArr[-1][3] < npArr[0][0]: return 0
    return sum(npArr[:,4])/npArr[0][0]/len(npArr)

def HandleBacktest(symbol, dataDict, cagrDictUS, rironkabukaDict):
    if symbol not in dataDict: return [symbol, 0]
    if symbol in cagrDictUS:
        cagr = cagrDictUS[symbol][3]
        if cagr < 0.01: return [symbol, 0]
    npArr = dataDict[symbol]
    if symbol in rironkabukaDict:
        rironkabuka = rironkabukaDict[symbol]
        if npArr[-1][3] >= rironkabuka - 5:
            return [symbol, 0]
    dividendGainPerDay = GetDividendGainPerDay(npArr)
    return [symbol, dividendGainPerDay]

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'DividendGainPerDay'])
        for symbol, dividendGainPerDay in result_list:
            writer.writerow([symbol, dividendGainPerDay])

def HandleGetDataWithDividends(symbol):
    return[symbol, GetDataWithDividendsLts(symbol)]

def HandleGetCagr(symbol):
    return[symbol, GetDataShort(symbol)]

def main(update=False):
    closeDictUS = GetCloseAll()
    symbolListUS = list(closeDictUS.keys())

    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())

    symbolList = symbolListUS + symbolListJP

    dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithDividendUS.p"
    cagrPathUS = f"{rootPath}/backtest/pickle/pro/compressed/cagrUS.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithDividendJP.p"
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    csvPath = f"{rootPath}/data/DividendGainPerDay.csv"

    dataDictUS, dataDictJP, cagrDictUS, rironkabukaDict = {}, {}, {}, {}
    if update:
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(HandleGetDataWithDividends, symbol) for symbol in symbolListUS]
            for future in as_completed(futures):
                result = future.result()
                if len(result[1]) < 3: continue
                dataDictUS[result[0]] = result[1]
        pickle.dump(dataDictUS, open(dataPathUS, "wb"))
        print("pickle dump finished")

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(HandleGetDataWithDividends, symbol) for symbol in symbolListJP]
            for future in as_completed(futures):
                result = future.result()
                if len(result[1]) < 3: continue
                dataDictJP[result[0]] = result[1]
        pickle.dump(dataDictJP, open(dataPathJP, "wb"))
        print("pickle dump finished")

        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [executor.submit(HandleGetCagr, symbol) for symbol in symbolListUS]
            for future in as_completed(futures):
                result = future.result()
                if len(result[1]) < 1: continue
                cagrDictUS[result[0]] = result[1]
        pickle.dump(cagrDictUS, open(cagrPathUS, "wb"))
        print("pickle dump finished")
    else:
        dataDictUS = LoadPickle(dataPathUS)
        dataDictJP = LoadPickle(dataPathJP)
        cagrDictUS = LoadPickle(cagrPathUS)
        rironkabukaDict = LoadPickle(rironkabukaPath)

    print(cagrDictUS["PBR"])
    dataDict = dataDictUS
    dataDict.update(dataDictJP)


    result_list = []
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleBacktest, symbol, dataDict, cagrDictUS, rironkabukaDict) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 2: continue
            dividendGainPerDay = result[1]
            if dividendGainPerDay == 0: continue
            symbol = result[0]
            print(symbol, dividendGainPerDay)
            result_list.append((symbol, dividendGainPerDay))
    result_list.sort(key=lambda x: x[1], reverse=True)
    dump_result_list_to_csv(result_list, csvPath)

if __name__ == '__main__':
    main(True)
