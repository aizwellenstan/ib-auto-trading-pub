# 1. < rironkabuka
# 2. 買い残＜売り残＋貸付残
# 3. cash > marketcapital

rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironFinancial
from modules.irbank import GetZandaka, GetDividend, GetSeichou
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

def HandleGetHaitourimawari(symbol):
    seichou = GetSeichou(symbol)
    return [symbol, seichou]

def HandleGetRironFinancial(symbol):
    rironkabuka, financialScore, financialDetail = GetRironFinancial(symbol)
    return [symbol, rironkabuka, financialScore, financialDetail]

def HandleGetZandaka(symbol):
    zandaka = GetZandaka(symbol)
    return [symbol, zandaka]

def UpdateData(symbolList):
    rironkabukaDict, financialScoreDict, financialDetailDict, plDict, zandakaDict = {}, {}, {}, {}, {}
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(HandleGetRironFinancial, symbol) for symbol in symbolList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 1: continue
    #         symbol = result[0]
    #         rironkabuka = result[1]
    #         financialScore = result[2]
    #         financialDetail = result[3]
    #         if rironkabuka < 6: continue
    #         if financialScore < 1: continue
    #         if len(financialDetail) < 5: continue
    #         rironkabukaDict[symbol] = rironkabuka
    #         financialScoreDict[symbol] = financialScore
    #         financialDetailDict[symbol] = financialDetail
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetHaitourimawari, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            seichou = result[1]
            if len(seichou) < 1: continue
            plDict[symbol] = seichou
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(HandleGetZandaka, symbol) for symbol in symbolList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 1: continue
    #         symbol = result[0]
    #         res = result[1]
    #         zandakaDict[symbol] = res
    return plDict

def CheckCheap(symbol, closeDictJP, rironkabukaDict, zandakaDict):
    close = closeDictJP[symbol]
    # if symbol not in zandakaDict: return [symbol, 0]
    if symbol not in rironkabukaDict: return [symbol, 0]
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka: return [symbol, 0]
    # if symbol not in zandakaDict: return [symbol, 0]
    # zandaka = zandakaDict[symbol]
    # if len(zandaka) < 1: return [symbol, 0]
    # if zandaka[0][1] > zandaka[0][7]: return [symbol, 0]
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


# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    average_high = np.mean(high_values)
    
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    average_low = np.mean(low_values)
    
    return np.array([average_high, average_low])

perDataDict = {}
def CheckPer(symbol):
    try:
        if symbol not in perDataDict: return[]
        npArr = perDataDict[symbol]
        if len(npArr[0]) < 10: return[]
        perList = npArr[:,9].astype(np.float64)
        avgHigh, avgLow = split_list_average_high_low(perList)
        return [perList[0] / avgLow]
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def HandleDividendToPrice(symbol):
    dividendToPrice = GetDividendToPrice(symbol, 'JPY')
    return [dividendToPrice]

def main(update=False):
    global perDataDict
    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
    financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
    seichouPath = f"{rootPath}/backtest/pickle/pro/compressed/seichou.p"
    zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
    picklePathPerJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictPerJP.p"
    rironkabukaDict, zandakaDict = {}, {}
    if update:
#         symbolListJP = [
# "7686",
# "4485",
# "5258",
# "8031",
# "8058",
# "6526",
# "7203",
# "3561",
# "3099",
# "3399",
# "4911",
# "6080",
# "7014",
# "3697",
# "8002",
# "6857",
# "8766",
# "6027",
# "7373",
# "8001",
# "4005",
# "4063",
# "4185",
# "4186",
# "8316",
# "8424",
# "4046",
# "6723",
# "9432",
# "8411",
# "8306",
# "6890",
# "5533",
# "3498",
# "5401",
# "5406",
# "9107",
# "8750",
# "8411",
# "4487",
# "3083",
# "6104",
# "7388",
# "2222",
# "3498",
# "5137",
# "4413",
# "4176",
# "4570",
# "2884",
# "7373",
# "7369",
# "2651",
# "6146",
# "9158",
# "6305",
# "3758",
# "4617",
# "9552",
# "3496",
# "4739",
# "8136",
# "6418",
# "6457",
# "8002",
# "7011",
# "5344",
# "5122",
# "3186",
# "4886",
# "7687",
# "4933",
# "7267",
# "7246",
# "5310",
# "5202",
# "2340",
# "4691",
# "7048",
# "9346",
# "7214",
# "3452",
# "7532",
# "7611",
# "6857",
# "8306",
# "7130",
# "7011",
# "3097"
# ]
#         symbolListJP = ['7686', '6526', '3561', '3561', '3561', '3561', '9107', '8136', '3496', '4487', '7014', '4487', '4570', '4487', '6526', '7388', '4570', '3083', '4176', '3697', '7369', '7369', '7369',
# '7369', '3561', '6027', '4570', '7369', '8750', '4487', '6526', '4739', '7369', '7687', '4570', '4570', '2222', '4046', '4570', '7214', '7214', '7014', '6526', '4570', '7369', '4570', '3561', '3399']
        plDict = UpdateData(symbolListJP)
        # pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
        # pickle.dump(financialScoreDict, open(financialScorePath, "wb"))
        # pickle.dump(financialDetailDict, open(financialDetailPath, "wb"))
        pickle.dump(plDict, open(seichouPath, "wb"))
        # pickle.dump(zandakaDict, open(zandakaPath, "wb"))
        # perDataDict = ThreadPool(symbolListJP, GetPer)
        # pickle.dump(perDataDict, open(picklePathPerJP, "wb"))
        print("pickle dump finished")
    else:
        rironkabukaDict = LoadPickle(rironkabukaPath)
        zandakaDict = LoadPickle(zandakaPath)
        perDataDict = LoadPickle(picklePathPerJP)

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

    # cashDictJP = GetCashJP()
    # cashList = []
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(CheckCash, symbol, cashDictJP) for symbol in cheapList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 1: continue
    #         symbol = result[0]
    #         res = result[1]
    #         if res < 1: continue
    #         cashList.append(symbol)

    symbolList = list(perDataDict.keys())
    results = ThreadPool(symbolList, CheckPer)
    perDict = {}
    for symbol, res in results.items():
        if res[0] >= 1: continue
        if symbol not in cheapList: continue
        perDict[symbol] = res[0]

    perDict = dict(sorted(perDict.items(), key=lambda item: item[1]))
    print(perDict)

    # exdividendDict = GetExdividend()
    
    # nextDividend = {}
    # for date, exDividendList in exdividendDict.items():
    #     found = False
    #     for symbol in passedList:
    #         if symbol in exDividendList:
    #             found = True
    #             # break
    #     if found:
    #         buyList = []
    #         for symbol in exDividendList:
    #             if symbol in passedList:
    #                 buyList.append(symbol)
    #         nextDividend[date] = buyList
    
    # print(nextDividend)

    # firstPriority = []
    # for date, symbolList in nextDividend.items():
    #     for symbol in symbolList:
    #         firstPriority.append(symbol)
    
    # print(firstPriority)

    # dividendDict = ThreadPool(passedList,GetDividend)
    # print(dividendDict)
    # sorted_data = sorted(dividendDict.items(), key=lambda x: (x[1][0], -x[1][1]))

    # sorted_dict = {k: v for k, v in sorted_data}
    # print(sorted_dict)

if __name__ == '__main__':
    main(True)