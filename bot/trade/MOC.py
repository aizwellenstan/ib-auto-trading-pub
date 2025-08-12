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
ib = ibc.GetIB(35)

avalible_cash = ibc.GetBalance()
avalible_price = int(avalible_cash)/100
print(avalible_price)
# total_cash = (avalible_cash - 611) / 2
# total_cash = avalible_cash * 0.4
# total_cash = avalible_cash * 0.39
total_cash = avalible_cash * 0.04
basicPoint = 0.01

def main():
    # optionCost = 259 + 80 + 307 + 102
    # optionCost = 259 + 61 + 5 + 729 + 102
    # total_cash -= optionCost
    # total_cash /= 2

    currency = 'USD'
    # https://www.nasdaq.com/market-activity/dividends
    portfolioPath = f'{rootPath}/data/ScannerUSOption.csv'
    import os
    portfolioDict = {}
    if os.path.exists(portfolioPath):
        df = pd.read_csv(portfolioPath)
        portfolioDict = df.set_index('Symbol').Close.to_dict()
        portfolioDict = {key: portfolioDict[key] for key in list(portfolioDict)}

    positions = ib.positions()
    positionDict = {}
    for position in positions:
        contract = position.contract
        symbol = contract.symbol
        if symbol not in portfolioDict: continue
        position = position.position
        print(symbol, position)
        ibc.HandleStopMOC(contract, position, 'SELL')
        # break
        # ibc.HandleMOC(contract, position, 'SELL')

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