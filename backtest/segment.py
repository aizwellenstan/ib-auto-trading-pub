rootPath = "..";import sys;sys.path.append(rootPath)
from modules.irbank import GetChart, GetSegment
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from numba import njit
import numpy as np

def HandleGetSegment(symbol):
    segment = GetSegment(symbol)
    return [symbol, segment]

def HandleGetChart(symbol):
    chart = GetChart(symbol)
    return [symbol, chart]

def main():
    segmentPath = f"{rootPath}/backtest/pickle/pro/compressed/segment.p"

    closeDictJP = GetCloseJP()
    symbolList = list(closeDictJP.keys())

    segmentDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetSegment, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            segment= result[1]
            if len(segment) < 1: continue
            segmentDict[symbol] = segment
    pickle.dump(segmentDict, open(segmentPath, "wb"))
    print("pickle dump finished")

if __name__ == '__main__':
    main()