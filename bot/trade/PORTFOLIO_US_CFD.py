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
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(34)

avalible_cash = ibc.GetBalance()
avalible_price = int(avalible_cash)/100
print(avalible_price)
# total_cash = (avalible_cash - 611) / 2
# total_cash = avalible_cash * 0.12
total_cash = avalible_cash * 0.19
# total_cash = avalible_cash * 0.06
# total_cash = avalible_cash * 0.1
# total_cash = avalible_cash * 0.04
basicPoint = 0.01

def main():
    # optionCost = 259 + 80 + 307 + 102
    # optionCost = 259 + 61 + 5 + 729 + 102
    # total_cash -= optionCost
    # total_cash /= 2

    currency = 'USD'
    # https://www.nasdaq.com/market-activity/dividends
    portfolioPath = f'{rootPath}/data/ScannerUS.csv'
    import os
    portfolioDict = {}
    if os.path.exists(portfolioPath):
        df = pd.read_csv(portfolioPath)
        portfolioDict = df.set_index('Symbol').Close.to_dict()
        portfolioDict = {key: portfolioDict[key] for key in list(portfolioDict)}

    # total = 0
    # for i in range(0, len(portfolioDict)):
    #     count = 0
    #     if total > 0: break
    #     for k, v in portfolioDict.items():
    #         count += 1
    #         if i == count:
    #             portfolioList = take(count,portfolioDict)
    #             for symbol in portfolioList:
    #                 vol = int(total_cash/portfolioDict[symbol])
    #                 if vol < 1: 
    #                     total = count-1
    # if total < 1: total = len(portfolioDict)
    # if total > 21: total = 21

    # print("TOTAL",total)
    count = 0
    tradePortfolioDict = {}
    for symbol, v in portfolioDict.items():
        vol = int(total_cash/v)
        print(symbol,v,vol)
        if vol < 1:
            print(symbol,"vol < 1")
            continue
        if vol < 3:
            if v < 73:
                print(symbol,"vol < 3")
                continue
            # break
        tradePortfolioDict[symbol] = vol
        count += 1
        # if count == total: break
    print(tradePortfolioDict)
    
    tradePortfolioPath = f'{rootPath}/data/portfolioUS.csv'
    df = pd.DataFrame()
    df['Symbol'] = tradePortfolioDict.keys()
    df['Vol'] = tradePortfolioDict.values()
    df.to_csv(tradePortfolioPath)
    # sys.exit()
    positions = ib.positions()
    positionDict = {}
    for position in positions:
        symbol = position.contract.symbol
        position = position.position
        positionDict[symbol] = position
        if symbol not in tradePortfolioDict:
            print(symbol, 'SELL')

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
        ibc.HandleBuyLimitCFD(symbol, vol, 'USD')
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