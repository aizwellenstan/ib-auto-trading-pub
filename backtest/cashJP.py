rootPath = "..";import sys;sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP, GetCashJP
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.loadPickle import LoadPickle
from modules.csvDump import DumpCsv

cashDictJP = GetCashJP()

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
    return [symbol, market_cap_basic / cash]

def main(update=False):
    closeDictJP = GetCloseJP()
    symbolListJP = list(closeDictJP.keys())
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    rironkabukaDict = LoadPickle(rironkabukaPath)

    cashResDict = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(CheckCash, symbol, cashDictJP) for symbol in list(closeDictJP.keys())]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            res = result[1]
            if res == 0: continue
            if symbol not in rironkabukaDict: continue
            if res >= 1: continue
            if closeDictJP[symbol] >= rironkabukaDict[symbol] - 5: continue
            cashResDict[symbol] = res

    cashResDict = dict(sorted(cashResDict.items(), key=lambda item:item[1]))
    print(cashResDict)

    for k, v in cashResDict.items():
        print(k, v)

    tradableJPPath = f"{rootPath}/data/CashJP.csv"
    DumpCsv(tradableJPPath,list(cashResDict.keys()))

if __name__ == "__main__":
    main()