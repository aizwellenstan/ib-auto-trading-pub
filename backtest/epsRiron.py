rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.income import GetEarnings
# from modules.seekingalpha import GetEPS
# from modules.aiztradingview import GetAttrJP
from modules.data import GetDataWithDateTime
# from datetime import datetime

import numpy as np
from modules.eps import GetEPS
from modules.barchart import GetHoldings

# from modules.seekingalpha import GetEPS

import pickle
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
from modules.aiztradingview import GetCloseAll, GetCashUS, GetAttr


def CheckCash(symbol, cashDict):
    if symbol not in cashDict: return [symbol, 0]
    data = cashDict[symbol]
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

perDataDict, dataDict = {},{}
def CheckPer(symbol):
    # eps = GetEarnings(symbol)
    if symbol not in perDataDict: return []
    eps = perDataDict[symbol]
    eps = eps[['dateReported', 'eps']].to_numpy()
    if len(eps) < 1: return []
    # npArr = GetDataWithDateTime(symbol)[-120:]
    npArr = dataDict[symbol][-120:]
    if len(npArr) < 1: return []
    epsIdx = 0
    perList = np.empty(0)
    for i in range(0, len(npArr)):
        for j in range(epsIdx, len(eps)):
            if npArr[i][4] >= eps[j][0]:
                epsIdx = j
        if eps[epsIdx][1] < 0.01: return []
        per = npArr[i][3] / eps[epsIdx][1]
        perList = np.append(perList, per)

    res = split_list_average_high_low(perList)
    return [symbol, perList[-1]/res[1]]

def GetNormalPer(symbol):
    # eps = GetEarnings(symbol)
    if symbol not in perDataDict: return []
    eps = perDataDict[symbol]
    eps = eps[['dateReported', 'eps']].to_numpy()
    if len(eps) < 1: return []
    # npArr = GetDataWithDateTime(symbol)[-120:]
    npArr = dataDict[symbol][-120:]
    if len(npArr) < 1: return []
    epsIdx = 0
    perList = np.empty(0)
    for i in range(0, len(npArr)):
        for j in range(epsIdx, len(eps)):
            if npArr[i][4] >= eps[j][0]:
                epsIdx = j
        if eps[epsIdx][1] < 0.01: return []
        per = npArr[i][3] / eps[epsIdx][1]
        perList = np.append(perList, per)

    res = split_list_average_high_low(perList)
    return [symbol, (res[0]+res[1])/2/perList[-1]]

def main(update=False):
    symbol = "SPY"
    holdings = GetHoldings(symbol)
    print(holdings)
    holdingList = []
    for h in holdings:
        if h[1] == 0: continue
        holdingList.append(h[0])
    
    global perDataDict, dataDict
    closeDict = GetCloseAll()
    symbolListUS = list(closeDict.keys())
    for symbol in holdingList:
        symbolListUS.append(symbol)
    epsPathUS = f"{rootPath}/backtest/pickle/pro/compressed/epsUS.p"
    dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithDateUS.p"
    epsDataDict = {}
    if update:
        perDataDict = ThreadPool(symbolListUS, GetEPS)
        pickle.dump(perDataDict, open(epsPathUS, "wb"))
        print("pickle dump finished")
        dataDict = ThreadPool(symbolListUS, GetDataWithDateTime)
        pickle.dump(dataDict, open(dataPathUS, "wb"))
        print("pickle dump finished")
    else:
        perDataDict = LoadPickle(epsPathUS)
        dataDict = LoadPickle(dataPathUS)

    floatDict = GetAttr("float_shares_outstanding")
    sharesDict = GetAttr("total_shares_outstanding_fundamental")

    etfPrice = 0
    rironEtfPrice = 0
    total = 0
    rironMarcapDict = {}
    for h in holdings:
        if h[1] == 0: continue
        symbol = h[0]
        try:
            price = dataDict[symbol][-1][3]
            shares = 0
            if symbol in floatDict:
                shares = floatDict[symbol]
            elif symbol in sharesDict:
                shares = sharesDict[symbol]

            etfPrice += price * shares *h[1]/100
            total += h[1]
            rironEtfPrice += price * GetNormalPer(symbol)[1] * shares *h[1]/100
        except:
            print("ERR",symbol)
            continue

    # for symbol, percent in holdings.items():
    #     price = dataDict[symbol][-1][3]
    #     etfPrice += price * percent/total
    print(etfPrice)
    print(rironEtfPrice)
    print(rironEtfPrice/etfPrice)
    print(total)

    # https://ycharts.com/indicators/sp_500_divisor#:~:text=S%26P%20500%20Divisor%20(I%3ASP500DIV)&text=S%26P%20500%20Divisor%20is%20at,from%208451.33%20one%20year%20ago.
    print(etfPrice)
    
    sys.exit()
    # print(perDataDict)

    
    
   
    perDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckPer, symbol) for symbol in symbolListUS]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res < 1: continue
            perDict[symbol] = res

    perDict = dict(sorted(perDict.items(), key=lambda item: item[1]))
    print(perDict)

if __name__ == '__main__':
    main()
