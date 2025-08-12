rootPath = "..";import sys;sys.path.append(rootPath)
from modules.irbank import GetShortBase
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from numba import njit
import numpy as np

def HandleGetShortBase(symbol):
    short = GetShortBase(symbol)
    return [symbol, short]

def main():
    shortBasePath = f"{rootPath}/backtest/pickle/pro/compressed/shortBase.p"

    closeDictJP = GetCloseJP()
    symbolList = list(closeDictJP.keys())

    shortBaseDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetShortBase, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            short = result[1]
            if len(short) < 1: continue
            shortBaseDict[symbol] = short
    pickle.dump(shortBaseDict, open(shortBasePath, "wb"))
    print("pickle dump finished")

if __name__ == '__main__':
    main()