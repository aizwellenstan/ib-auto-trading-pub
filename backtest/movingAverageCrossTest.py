rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseAll, GetCloseJP
from modules.data import GetDataWithDate
from numba import range, njit
from modules.movingAverage import SmaArr
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
import csv

# # @njit
def Backtest(npArr, smaArr, period):
    position = 0
    balance = 1
    trades = 0
    maxGain = 1
    inDate = ""
    maxInDate = ""
    maxOutDate = ""
    inIdx = 0
    print(npArr[406])
    for i in range(period, len(npArr)):
        if (
            position == 0 and
            npArr[i-2][3] < smaArr[i-2] and
            npArr[i-1][3] > smaArr[i-1]
        ):
            op = npArr[i][0]
            position = balance/op
            balcne = 0
            trades += 1
            inDate = npArr[i][4]
            inIdx = i
        elif(
            position > 0 and
            npArr[i-1][3] < smaArr[i-1]
        ):
            close = npArr[i][0]
            gain = close / op
            balance += position * close
            position = 0
            if gain > 14:
                print(close,op,"HERE",inDate, inIdx)
            if gain > maxGain:
                maxGain = gain
                maxInDate = inDate
                maxOutDate = npArr[i][4]
    if position > 0:
        balance += position * npArr[-1][3]
        close = npArr[-1][3]
        gain = close / op
        if gain > maxGain:
            maxGain = gain
            maxInDate = inDate
            maxOutDate = npArr[-1][4]
    if balance <= 1: return 0, "", ""
    return maxGain, maxInDate, maxOutDate

def BacktestPeriod(npArr):
    maxBalance = 1
    maxPeriod = 2
    closeArr = npArr[:,3]
    for period in range(2, len(npArr)-1):
        smaArr = SmaArr(closeArr, period)
        balance, inDate, outDate = Backtest(npArr, smaArr, period)
        if balance > maxBalance:
            maxBalance = balance
            maxPeriod = period
            maxInDate = inDate
            maxOutDate = outDate
    return maxBalance, maxPeriod, maxInDate, maxOutDate

def HandleBacktest(symbol, dataDict):
    if symbol not in dataDict: return [symbol, 0, 0]
    npArr = dataDict[symbol]
    maxBalance, maxPeriod, maxInDate, maxOutDate = BacktestPeriod(npArr)
    return [symbol, maxBalance, maxPeriod, maxInDate, maxOutDate]

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'Balabce', 'Period'])
        for symbol, best_rr, best_pl in result_list:
            writer.writerow([symbol, best_rr, best_pl])

def HandleGetDataWithDate(symbol):
    return[symbol, GetDataWithDate(symbol)]

def main(update=False):
    closeDictUS = GetCloseAll()
    symbolListUS = list(closeDictUS.keys())

    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())

    symbolList = symbolListUS + symbolListJP

    dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    csvPath = f"{rootPath}/data/movingAverage3.csv"

    # dataDictUS, dataDictJP = {}, {}
    # if update:
    #     dataDictUS = {}
    #     with ThreadPoolExecutor(max_workers=100) as executor:
    #         futures = [executor.submit(HandleGetDataWithDate, symbol) for symbol in symbolListUS]
    #         for future in as_completed(futures):
    #             result = future.result()
    #             if len(result[1]) < 3: continue
    #             dataDictUS[result[0]] = result[1]
    #     pickle.dump(dataDictUS, open(dataPathUS, "wb"))
    #     print("pickle dump finished")

    #     dataDictJP = {}
    #     with ThreadPoolExecutor(max_workers=100) as executor:
    #         futures = [executor.submit(HandleGetDataWithDate, symbol) for symbol in symbolListJP]
    #         for future in as_completed(futures):
    #             result = future.result()
    #             if len(result[1]) < 3: continue
    #             dataDictJP[result[0]] = result[1]
    #     pickle.dump(dataDictJP, open(dataPathJP, "wb"))
    #     print("pickle dump finished")
    # else:
    #     dataDictUS = LoadPickle(dataPathUS)
    #     dataDictJP = LoadPickle(dataPathJP)

    dataDict = {}
    symbol = "GDXU"
    dataDict[symbol] = GetDataWithDate(symbol)
    symbol, maxBalance, maxPeriod, maxInDate, maxOutDate = HandleBacktest(symbol, dataDict)
    print(maxBalance, maxPeriod, maxInDate, maxOutDate)
    
    # dataDict.update(dataDictJP)

    # result_list = []
    
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(HandleBacktest, symbol, dataDict) for symbol in symbolList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 3: continue
    #         maxBalance = result[1]
    #         if maxBalance <= 1: continue
    #         symbol = result[0]
    #         maxPeriod = result[2]
    #         print(symbol, maxBalance, maxPeriod)
    #         result_list.append((symbol, maxBalance, maxPeriod))
    # result_list.sort(key=lambda x: x[1], reverse=True)
    # dump_result_list_to_csv(result_list, csvPath)

if __name__ == '__main__':
    main()