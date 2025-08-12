import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from modules.aiztradingview import GetProfit, GetProfitJP
from modules.vwap import Vwap
import yfinance as yf

ignoreList = ['CSCO']
scanner = GetProfitJP()

filter_sym_list = []
for s in scanner:
    if s not in ignoreList:
        filter_sym_list.append(s)

def main():
    # currency = 'USD'
    currency = 'JPY'

    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()

    csvPath = "8M"

    try:
        symbolArr = []

        for symbol in profitSymList:
            if symbol not in symbolArr:
                symbolArr.append(symbol)

        for symbol in symbolArr:
            stockInfo = yf.Ticker(symbol)
            hist = stockInfo.history(period="365d")
            
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            hist.to_csv('./csv/vwap/{}/jp/{}.csv'.format(csvPath,symbol))
    
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

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