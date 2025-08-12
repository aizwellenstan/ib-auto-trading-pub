# 1. < rironkabuka
# 2. 買い残＜売り残＋貸付残
# 3. cash > marketcapital

rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironkabuka
from modules.irbank import GetZandaka
from modules.aiztradingview import GetCloseJP, GetCashJP
from modules.kabumap import GetExdividend
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv

def HandleGetRironkabuka(symbol):
    rironkabuka = GetRironkabuka(symbol)
    return [symbol, rironkabuka]

def HandleGetZandaka(symbol):
    zandaka = GetZandaka(symbol)
    return [symbol, zandaka]

def UpdateData(symbolList):
    rironkabukaDict, zandakaDict = {}, {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetRironkabuka, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            rironkabukaDict[symbol] = res
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetZandaka, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            zandakaDict[symbol] = res
    return rironkabukaDict, zandakaDict

def CheckCheap(symbol, closeDictJP, rironkabukaDict, zandakaDict):
    close = closeDictJP[symbol]
    if symbol not in zandakaDict: return [symbol, 0]
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka: return [symbol, 0]
    if symbol not in zandakaDict: return [symbol, 0]
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: return [symbol, 0]
    if zandaka[0][1] > zandaka[0][7]: return [symbol, 0]
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
    if market_cap_basic > cash: return [symbol, 0]
    return [symbol, 1]

def main(update=False):
    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
    rironkabukaDict, zandakaDict = {}, {}
    if update:
        rironkabukaDict, zandakaDict = UpdateData(symbolListJP)
        pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
        # pickle.dump(zandakaDict, open(zandakaPath, "wb"))
    else:
        rironkabukaDict = LoadPickle(rironkabukaPath)
        zandakaDict = LoadPickle(zandakaPath)

    cheapList = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckCheap, symbol, closeDictJP, rironkabukaDict, zandakaDict) for symbol in symbolListJP]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res < 1: continue
            cheapList.append(symbol)

    cashDictJP = GetCashJP()
    passedList = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckCash, symbol, cashDictJP) for symbol in cheapList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res < 1: continue
            passedList.append(symbol)
    print(passedList)

    exdividendDict = GetExdividend()
    
    # passedList = cheapList

    nextDividend = {}
    for date, exDividendList in exdividendDict.items():
        found = False
        for symbol in passedList:
            if symbol in exDividendList:
                found = True
                break
        if found:
            buyList = []
            for symbol in exDividendList:
                if symbol in passedList:
                    buyList.append(symbol)
            nextDividend[date] = buyList
    
    print(nextDividend)
    # buyList = []
    # for symbol in nextDividend:
    #     if symbol in passedList:
    #         buyList.append(symbol)
    # print(buyList)

    # print(passedList)
    # tradableJPPath = f"{rootPath}/data/TradableJP.csv"
    # DumpCsv(tradableJPPath,passedList)
    



if __name__ == '__main__':
    main()