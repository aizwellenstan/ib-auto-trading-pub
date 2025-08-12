rootPath = "..";import sys;sys.path.append(rootPath)
from modules.irbank import GetChartHistory
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from numba import njit
import numpy as np

def HandleGetChartHistory(symbol):
    print(symbol)
    chart = GetChartHistory(symbol)
    return [symbol, chart]

def main():
    print("GETCLOSE")
    closeDictJP = GetCloseJP()
    print(closeDictJP)
    symbolList = list(closeDictJP.keys())
    chartHistoryPath = f"{rootPath}/backtest/pickle/pro/compressed/chartHistory2.p"

    chartDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetChartHistory, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            chart = result[1]
            if len(chart) < 1: continue
            chartDict[symbol] = chart
            print(symbol, len(chart))
    pickle.dump(chartDict, open(chartHistoryPath, "wb"))
    print("pickle dump finished")

if __name__ == '__main__':
    main()