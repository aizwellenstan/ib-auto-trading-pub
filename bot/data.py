rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseAll, GetCloseJP
from modules.data import GetDataWithVolumeDate
from numba import range, njit
from modules.movingAverage import SmaArr
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
import csv

# @njit
def Backtest(npArr, smaArr, period):
    position = 0
    balance = 1
    maxGain = 1
    for i in range(period, len(npArr)):
        if (
            position == 0 and
            npArr[i-2][3] < smaArr[i-2] and
            npArr[i-1][3] > smaArr[i-1]
        ):
            op = npArr[i][0]
            position = balance/op
            balcne = 0
        elif(
            position > 0 and
            npArr[i-1][3] < smaArr[i-1]
        ):
            close = npArr[i][0]
            gain = close / op
            balance += position * close
            position = 0
            if gain > maxGain:
                maxGain = gain
    if position > 0:
        balance += position * npArr[-1][3]
        close = npArr[-1][3]
        gain = close / op
        if gain > maxGain:
            maxGain = gain
    if balance <= 1: return 0
    return maxGain

# @njit
def BacktestToTrades(npArr, smaArr, period):
    position = 0
    balance = 1
    trades = 0
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
        elif(
            position > 0 and
            npArr[i-1][3] < smaArr[i-1]
        ):
            close = npArr[i][0]
            gain = close / op
            balance += position * close
            position = 0
            trades += 1
    if position > 0:
        balance += position * npArr[-1][3]
    return balance/trades

def BacktestPeriod(npArr):
    maxBalance = 1
    maxPeriod = 2
    secondMaxBalance = 1
    closeArr = npArr[:,3]
    for period in range(2, len(npArr)-1):
        smaArr = SmaArr(closeArr, period)
        balance = Backtest(npArr, smaArr, period)
        if balance > maxBalance:
            secondMaxBalance = maxBalance
            maxBalance = balance
            maxPeriod = period
    if secondMaxBalance <= 1: return 0, maxPeriod
    # smaArr = SmaArr(closeArr, maxPeriod)
    # balance = BacktestToTrades(npArr, smaArr, maxPeriod)
    return secondMaxBalance, maxPeriod

def HandleBacktest(symbol, dataDict):
    if symbol not in dataDict: return [symbol, 0, 0]
    npArr = dataDict[symbol]
    maxBalance, maxPeriod = BacktestPeriod(npArr)
    return [symbol, maxBalance, maxPeriod]

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'Balabce', 'Period'])
        for symbol, best_rr, best_pl in result_list:
            writer.writerow([symbol, best_rr, best_pl])

def HandleGetDataWithVolumeDate(symbol):
    return[symbol, GetDataWithVolumeDate(symbol, "2018-01-01")]

def main(update=False):
    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())

    symbolList = symbolListJP

    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeLongJP.p"
    csvPath = f"{rootPath}/data/movingAverage.csv"

    symbolListJP.append("^N225")
    symbolListJP.append("1475")
    symbolListJP.append("1591")
    symbolListJP.append("1306")
    symbolListJP.append("^TNX")

    dataDictUS, dataDictJP = {}, {}
    if update:
        # dataDictUS = {}
        # with ThreadPoolExecutor(max_workers=100) as executor:
        #     futures = [executor.submit(HandleGetDataWithVolumeDate, symbol) for symbol in symbolListUS]
        #     for future in as_completed(futures):
        #         result = future.result()
        #         if len(result[1]) < 3: continue
        #         dataDictUS[result[0]] = result[1]
        # pickle.dump(dataDictUS, open(dataPathUS, "wb"))
        # print("pickle dump finished")

        dataDictJP = {}
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(HandleGetDataWithVolumeDate, symbol) for symbol in symbolListJP]
            for future in as_completed(futures):
                result = future.result()
                if len(result[1]) < 3: continue
                dataDictJP[result[0]] = result[1]
        pickle.dump(dataDictJP, open(dataPathJP, "wb"))
        print("pickle dump finished")

if __name__ == '__main__':
    main(True)