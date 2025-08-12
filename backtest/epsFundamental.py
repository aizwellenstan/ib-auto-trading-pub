# 1. < rironkabuka
# 2. 買い残＜売り残＋貸付残
# 3. cash > marketcapital

rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.rironkabuka import GetRironkabuka
from modules.irbank import GetZandaka, GetDividend
from modules.aiztradingview import GetCloseJP, GetCashJP, GetClose, GetAttrJP
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

import modules.ib as ibc

# today = datetime.now().date()

ibc = ibc.Ib()
ib = ibc.GetIB(2)

avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

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
    zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
    picklePathPerJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictPerJP.p"
    
    shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
    shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
    gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
    financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
    financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
    shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
    haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
    inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
    netIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeQJP.p"
    treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
    ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"

    rironkabukaDict, zandakaDict = {}, {}
    if update:
        rironkabukaDict, zandakaDict = UpdateData(symbolListJP)
        pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
        # pickle.dump(zandakaDict, open(zandakaPath, "wb"))
        perDataDict = ThreadPool(symbolListJP, GetPer)
        pickle.dump(perDataDict, open(picklePathPerJP, "wb"))
        print("pickle dump finished")
    else:
        rironkabukaDict = LoadPickle(rironkabukaPath)
        zandakaDict = LoadPickle(zandakaPath)
        perDataDict = LoadPickle(picklePathPerJP)

        shisannkachiDict = LoadPickle(shisannkachiPath)
        shijouDict = LoadPickle(shijouPath)
        gyoushuDict = LoadPickle(gyoushuPath)
        financialScoreDict = LoadPickle(financialScorePath)
        financialDetailDict = LoadPickle(financialDetailPath)
        shuuekiDict = LoadPickle(shuuekiPath)
        haitourimawariDict = LoadPickle(haitourimawariPath)
        treasurySharesDict = LoadPickle(treasurySharesPath)
        inventoryDict = LoadPickle(inventoryPath)
        netIncomeDict = LoadPickle(netIncomePath)
        ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
        dataDictJP = LoadPickle(dataPathJP)

    closeDict = GetCloseJP()
    industryDict = GetAttrJP("industry")
    assetDict = GetAttrJP("total_current_assets")
    liabilitiesDict = GetAttrJP("total_liabilities_fy")
    ignoreList = [
        "Electronic Production Equipment", 
        "Telecommunications Equipment", 
        "Environmental Services",
        "Computer Peripherals",
        "Biotechnology",
        "Commercial Printing/Forms",
        "Trucks/Construction/Farm Machinery",
        "Auto Parts: OEM",
        "Tools & Hardware",
        "Recreational Products",
        "Metal Fabrication",
        "Forest Products",
        "Industrial Specialties",
        "Other Consumer Specialties",
        "Movies/Entertainment",
        "Medical Specialties",
        "Office Equipment/Supplies",
        "Electronics/Appliances",
        "Pulp & Paper",
        "Electrical Products",
        "Alternative Power Generation"
    ]
    ignoreSector = ["輸送用機器","情報通信",
            "鉱業","繊維",
            "空運","保険","鉄鋼",
            "銀行"]
    ignoreSectorFirst = [
        "紙・パルプ",
        "鉱業","繊維",
        "空運","鉄鋼",
        "保険"]

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
    shift = 0
    for symbol, res in results.items():
        if res[0] >= 1: continue
        if symbol not in cheapList: continue

        if symbol not in gyoushuDict: continue
        if gyoushuDict[symbol] in ignoreSectorFirst: continue
        if symbol not in dataDictJP: continue
        if symbol not in treasurySharesDict: continue
        treasuryShares = treasurySharesDict[symbol]
        if len(treasuryShares) < 2: continue
        if symbol not in shisannkachiDict: continue
        if symbol not in shuuekiDict: continue
        if symbol not in shijouDict: continue
        if symbol not in haitourimawariDict: continue
        if haitourimawariDict[symbol] > 0.033: continue
        if symbol not in assetDict: continue
        if symbol not in liabilitiesDict: continue
        if assetDict[symbol] < liabilitiesDict[symbol]/30: continue
        npArr = dataDictJP[symbol]
        
        if npArr[-1-shift][3] / shisannkachiDict[symbol] > 7.8: continue
        if symbol not in zandakaDict: continue
        zandaka = zandakaDict[symbol]
        if len(zandaka) < 1: continue
        if zandaka[0-shift][1] < 900: continue
        if npArr[-1-shift][4] >= npArr[-2-shift][4]: continue
        # treasuryShares = treasurySharesDict[symbol]
        # if treasuryShares[0] < treasuryShares[1]: continue
        # if shijouDict[symbol] == "東証プライム": continue
        if symbol not in gyoushuDict: continue
        if gyoushuDict[symbol] in ignoreSector: continue
        if npArr[-1-shift][3] >= rironkabukaDict[symbol] - 5: continue
        if symbol not in financialDetailDict: continue
        # if shuuekiDict[symbol] < 0.02: continue
        if financialDetailDict[symbol][0] != 0:
            if financialDetailDict[symbol][0] < 3:
                continue
        if (
            symbol in netIncomeDict and
            symbol in inventoryDict
        ):
            netIncome = netIncomeDict[symbol]
            inventory = inventoryDict[symbol]
            if (
                len(inventory) > 2 and
                len(netIncome) > 2 and
                inventory[0] > inventory[1] and
                inventory[1] > inventory[2] and
                netIncome[0] < netIncome[1] and
                netIncome[1] < netIncome[2]
            ): continue

        if symbol not in rironkabukaDict: continue
        if closeDict[symbol] >= rironkabukaDict[symbol] - 5: continue
        if closeDict[symbol] > avalible_price: continue
        
        if symbol not in ryuudoumeyasuDict: continue
        if ryuudoumeyasuDict[symbol][0] <= 100: continue

        perDict[symbol] = res[0]

    perDict = dict(sorted(perDict.items(), key=lambda item: item[1]))
    print(perDict)

    for symbol, v in perDict.items():
        print(symbol, closeDictJP[symbol])

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
    main()