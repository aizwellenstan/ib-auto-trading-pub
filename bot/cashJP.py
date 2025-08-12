# 1. < rironkabuka
# 2. 買い残＜売り残＋貸付残
# 3. cash > marketcapital

rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironkabuka
from modules.irbank import GetZandaka, GetDividend
from modules.aiztradingview import GetCloseJP, GetCashJP, GetClose
from modules.kabumap import GetExdividend
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
from modules.threadPool import ThreadPool
from modules.irbank import GetPer
from numba import njit
import numpy as np
from modules.data import GetDividendToPrice
from modules.dict import SortDict
from modules.csvDump import dump_result_list_to_csv

def HandleGetRironkabuka(symbol):
    rironkabuka = GetRironkabuka(symbol)
    return [symbol, rironkabuka]

def HandleGetZandaka(symbol):
    zandaka = GetZandaka(symbol)
    return [symbol, zandaka]

def UpdateData(symbolList):
    rironkabukaDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetRironkabuka, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            rironkabukaDict[symbol] = res
    return rironkabukaDict

def CheckCheap(symbol, closeDictJP, rironkabukaDict):
    close = closeDictJP[symbol]
    if symbol not in rironkabukaDict: return [symbol, 0]
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka - 5: return [symbol, 0]
    return [symbol, 1]

def CheckCash(symbol, cashDictJP):
    if symbol not in cashDictJP: return [symbol, 0]
    data = cashDictJP[symbol]
    market_cap_basic = data[0]
    cash_n_short_term_invest_fy = data[1]
    cash_n_short_term_invest_fq = data[2]
    cash_n_equivalents_fy = data[3]
    cash_n_equivalents_fq = data[4]
    price_book_ratio = data[5]
    price_book_fq = data[6]
    if price_book_ratio is not None:
        if price_book_ratio > 1: return [symbol, 0]
    if price_book_fq is not None:
        if price_book_fq > 1: return [symbol, 0]  
    values = [cash_n_short_term_invest_fy, cash_n_short_term_invest_fq, cash_n_equivalents_fy, cash_n_equivalents_fq]
    filtered_values = list(filter(lambda x: x is not None and x != 0, values))
    if len(filtered_values) < 1: return [symbol, 0]
    cash = min(filtered_values)
    return [symbol, cash / market_cap_basic]

def main(update=False):
    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    rironkabukaDict = {}
    if update:
        rironkabukaDict = UpdateData(symbolListJP)
        pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
        print("pickle dump finished")
    else:
        rironkabukaDict = LoadPickle(rironkabukaPath)

    cheapList = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckCheap, symbol, closeDictJP, rironkabukaDict) for symbol in symbolListJP]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res < 1: continue
            cheapList.append(symbol)

    cashDictJP = GetCashJP()
    cashDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckCash, symbol, cashDictJP) for symbol in cheapList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res < 1: continue
            if res <= 1.363457006947963: continue
            cashDict[symbol] = res
    cashDict = SortDict(cashDict)
    res = []
    for k, v in cashDict.items():
        res.append([k,v])
    cashPath = f"{rootPath}/data/CashJP.csv"
    header = ["Symbol","CashHiritsu"]
    dump_result_list_to_csv(res,cashPath,header)

if __name__ == '__main__':
    main()