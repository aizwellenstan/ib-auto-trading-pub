rootPath = '../..'
import sys
sys.path.append(rootPath)
from modules.trade.vol import GetVolSlTp, GetVolLargeSlTp
from modules.dict import take
from modules.aiztradingview import GetClose
import pandas as pd
import math
from typing import NamedTuple
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetADR
from modules.discord import Alert
# import modules.ib as ibc

# ibc = ibc.Ib()
# ib = ibc.GetIB(22)

# total_cash, avalible_cash = ibc.GetTotalCash()
# basicPoint = 0.01
# # total_cash /= 2

total_cash = 25000

def main():
    symbolList = [
        "AMZN", "AMD", "AXP", "AMGN", 
        "ADI", "AAPL", "AMAT", "T", 
        "AVGO", "BA", "BAC", "BBY", "CSCO", 
        "C", "KO", "GLW", "EBAY", "F", "GE",
        "GS", "GOOG", "GOOGL", "HON", "HPQ", 
        "INTC", "JNJ", "JPM", "MCD", "MRK", "MU", 
        "MSFT", "MSI", "NFLX", "NVDA", "ORCL", 
        "PEP", "PFE", "PG", "QCOM", "RTX", "SBUX", 
        "TXN", "TSLA", "UNH", "ADBE", "WMT", 
        "A", "AIG", "APA", "BIIB", "BMY",
        "BSX", "CHKP", "CIEN", "CRUS", "EOG",
        "SCHW", "LLY", "XOM", "FLEX", "GPS", "GM",
        "HAL", "HD", "INTU", "JBL", "JNPR", "KSS",
        "LMT", "MDT", "QRVO", "SLB", "UPS", "VRSN",
        "VZ", "VIAV", "WMB", "XRX", "IP",
        # "BRK-B", "SMH", "EEM", "IWM", "DIA", "XLY", "XLE",
        # "XLF", "XLB", "SPY",
        # "^N225", "^GDAXI", "^GSPC", "^NDX", "^DJI", "^HSI",
        # "^XAU", "SLV",
        # "CL=F", "BZ=F"
    ]
    # optionCost = 259 + 80 + 307 + 102
    # optionCost = 259 + 61 + 5 + 729 + 102
    # total_cash -= optionCost
    # total_cash /= 2

    currency = 'USD'
    # https://www.nasdaq.com/market-activity/dividends
    portfolioPath = f'{rootPath}/data/ScannerUSLargeCap.csv'
    import os
    portfolioDict = {}
    if os.path.exists(portfolioPath):
        df = pd.read_csv(portfolioPath)
        portfolioDict = df.set_index('Symbol').Close.to_dict()

    portfolioCleanDict = {}
    for k, v in portfolioDict.items():
        if k not in symbolList: continue
        portfolioCleanDict[k] = v
    portfolioDict = portfolioCleanDict

    total = 0
    for i in range(0, len(portfolioDict)):
        count = 0
        if total > 0: break
        for k, v in portfolioDict.items():
            count += 1
            if i == count:
                portfolioList = take(count,portfolioDict)
                for symbol in portfolioList:
                    vol = int(total_cash/count/portfolioDict[symbol])
                    if vol < 1: 
                        total = count-1
    if total < 1: total = len(portfolioDict)
    if total > 5: total = 5

    print("TOTAL",total)
    count = 0
    tradePortfolioDict = {}
    for symbol, v in portfolioDict.items():
        vol = int(total_cash/total/v)
        print(symbol,v,vol)
        count += 1
        if count == total: break
        if vol < 1:
            print(symbol,"vol < 1")
            break
        tradePortfolioDict[symbol] = vol
    print(tradePortfolioDict)
    
    tradePortfolioPath = f'{rootPath}/data/portfolioUSLargeCap.csv'
    df = pd.DataFrame()
    df['Symbol'] = tradePortfolioDict.keys()
    df['Vol'] = tradePortfolioDict.values()
    df.to_csv(tradePortfolioPath)
    # positions = ib.positions()
    # positionDict = {}
    # for position in positions:
    #     symbol = position.contract.symbol
    #     position = position.position
    #     positionDict[symbol] = position
    #     if symbol not in tradePortfolioDict:
    #         print(symbol, 'SELL')

    openDict = {}    
    for k, v in tradePortfolioDict.items():
        if k in positionDict:
            if int(v) > positionDict[k]:
                print(k, 'BUY', v-positionDict[k])
                print(positionDict[k])
        else:
            print(k, 'BUY', v)
            openDict[k] = v

    for symbol, vol in openDict.items():
        print(symbol, vol)
        # ibc.HandleBuyLimitTrailUS(symbol,vol)
        # if vol > 0: break
        # HandleBuyMarket(symbol, vol, adrDict, currency)

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()','output.dat')

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()
    
    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()