rootPath = '.'
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
from modules.csvDump import LoadCsv

ibc = ibc.Ib()
ib = ibc.GetIB(2)

def main():
    positions = ibc.GetAllPositions()
    print(positions)

    portfolioJPPath = f'{rootPath}/data/ScannerJP.csv'
    jpSymbolList = LoadCsv(portfolioJPPath)[:4]
    jpSymbolList = [str(i) for i in jpSymbolList]
    print(jpSymbolList)

    # portfolioUSLevergeEtfPath = f'{rootPath}/data/ScannerUSLevergeEtf.csv'
    # usLevergeEtfSymbolList = LoadCsv(portfolioUSLevergeEtfPath)
    # usLevergeEtfSymbolList = usLevergeEtfSymbolList[:10]
    # print(usLevergeEtfSymbolList)

    portfolioUSStockPath = f'{rootPath}/data/ScannerUS.csv'
    usStockSymbolList = LoadCsv(portfolioUSStockPath)
    usStockSymbolList = usStockSymbolList[:21]
    print(usStockSymbolList)

    # portfolioUSEtfPath = f'{rootPath}/data/ScannerUSEtf.csv'
    # usEtfSymbolList = LoadCsv(portfolioUSEtfPath)
    # usEtfSymbolList = usEtfSymbolList[:11]
    # print(usEtfSymbolList)

    for symbol in positions:
        if (
            symbol not in jpSymbolList and
            # symbol not in usLevergeEtfSymbolList and
            symbol not in usStockSymbolList
            # symbol not in usEtfSymbolList
        ): 
            print("SELL", symbol)
    
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