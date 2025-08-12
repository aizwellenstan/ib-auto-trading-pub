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
ib = ibc.GetIB(14)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def HandleBuy(symbol):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolLargeSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
        return vol
    return 0

def main():
    # optionCost = 259 + 80 + 307 + 102
    # optionCost = 259 + 61 + 5 + 729 + 102
    # total_cash -= optionCost
    # total_cash /= 2

    currency = 'USD'
    # https://www.nasdaq.com/market-activity/dividends
    portfolioPath = f'{rootPath}/data/ExDividend.csv'
    import os
    dividendDict = {}
    if os.path.exists(portfolioPath):
        df = pd.read_csv(portfolioPath)
        dividendDict = df.set_index('Symbol').Divdend.to_dict()

    closeDict = GetClose()
    portfolioDict = {}
    for symbol, div in dividendDict .items():
        if symbol in closeDict:
            portfolioDict[symbol] = closeDict[symbol]

    total = 0
    for i in range(0, len(dividendDict)):
        count = 0
        if total > 0: break
        for k, v in portfolioDict.items():
            count += 1
            if i == count:
                dividendList = take(count,portfolioDict)
                for symbol in dividendList:
                    vol = int(total_cash/count/portfolioDict[symbol])
                    div = dividendDict[symbol] * vol
                    if vol < 1 or div < 2: 
                        total = count-1
    if total < 1: total = len(portfolioDict)

    print(total)
    count = 0
    divPortfolioDict = {}
    for symbol, v in portfolioDict.items():
        vol = int(total_cash/total/v)
        div = dividendDict[symbol] * vol
        if div < 2:
            print(div,"div < 2")
            break
        print(symbol,v,vol)
        divPortfolioDict[symbol] = vol
        count += 1
        if count == total: break
        if vol < 1:
            print(symbol,"vol < 1")
            break
    print(divPortfolioDict)

    divPortfolioPath = f'{rootPath}/data/portfolioExDividend.csv'
    df = pd.DataFrame()
    df['Symbol'] = divPortfolioDict.keys()
    df['DivdendToPrice'] = divPortfolioDict.values()
    df.to_csv(divPortfolioPath)

    positions = ib.positions()
    positionDict = {}
    for position in positions:
        symbol = position.contract.symbol
        position = position.position
        positionDict[symbol] = position
        if symbol not in divPortfolioDict:
            print(symbol, 'SELL')

    openDict = {}    
    for k, v in divPortfolioDict.items():
        if k in positionDict:
            if int(v) > positionDict[k]:
                print(k, 'BUY', v-positionDict[k])
                print(positionDict[k])
        else:
            print(k, 'BUY', v)
            openDict[k] = v

    adrDict = GetADR(currency)
    for symbol, vol in openDict.items():
        print(symbol, vol)
        vol = HandleBuy(symbol)
        if vol > 0: break
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