rootPath = "..";import sys;sys.path.append(rootPath)
from modules.rironkabuka import GetRR
from modules.aiztradingview import GetCloseJP
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from numba import njit
import numpy as np

def HandleGetRR(symbol):
    rr = GetRR(symbol)
    return [symbol, rr]

def main():
    rrPath = f"{rootPath}/backtest/pickle/pro/compressed/rr.p"

    closeDictJP = GetCloseJP()
    symbolList = list(closeDictJP.keys())

    rrDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetRR, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            rr = result[1]
            if len(rr) < 1: continue
            rrDict[symbol] = rr
    pickle.dump(rrDict, open(rrPath, "wb"))
    print("pickle dump finished")

    

if __name__ == '__main__':
    main()