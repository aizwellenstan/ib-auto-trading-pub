# 1. < rironkabuka
# 2. 買い残＜売り残＋貸付残
# 3. cash > marketcapital

rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.irbank import GetNewsUp
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
from modules.threadPool import ThreadPool
from numba import njit
import numpy as np
from modules.dict import SortDict


def HandleGetProductivity(symbol):
    productivity = GetProductivity(symbol)
    return [symbol, productivity]

def HandleGetRironFinancial(symbol):
    rironkabuka, financialScore, financialDetail = GetRironFinancial(symbol)
    return [symbol, rironkabuka, financialScore, financialDetail]

def HandleGetZandaka(symbol):
    zandaka = GetZandaka(symbol)
    return [symbol, zandaka]

def UpdateData(symbolList):
    rironkabukaDict, financialScoreDict, financialDetailDict, productivityDict, zandakaDict = {}, {}, {}, {}, {}
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
        futures = [executor.submit(HandleGetProductivity, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            productivity = result[1]
            if len(productivity) < 2: continue
            productivityDict[symbol] = productivity
    # with ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = [executor.submit(HandleGetZandaka, symbol) for symbol in symbolList]
    #     for future in as_completed(futures):
    #         result = future.result()
    #         if len(result) < 1: continue
    #         symbol = result[0]
    #         res = result[1]
    #         zandakaDict[symbol] = res
    return rironkabukaDict, financialScoreDict, financialDetailDict, productivityDict, zandakaDict

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

def HandleGetNews(date):
    news = GetNewsUp(date)
    return [date, news]

def main(update=False):
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    newsPath = f"{rootPath}/backtest/pickle/pro/compressed/news.p"
    dataDict = LoadPickle(dataPathJP)
    
    dateArr = dataDict["9101"][:,5]
    print(dateArr)

    newsDict = {}
    # for date in dateArr[0:3]:
    #     newsDict[date] = GetNewsUp(date)

    # print(newsDict)
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetNews, date) for date in dateArr]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            date = result[0]
            res = result[1]
            if len(res) < 1: continue
            newsDict[date] = res

    pickle.dump(newsDict, open(newsPath, "wb"))

    # newsDict = LoadPickle(newsPath)
    # print(newsDict)

if __name__ == '__main__':
    main(True)