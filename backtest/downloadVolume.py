# from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
from datetime import datetime as dt, timedelta
import json
import pickle
import numpy as np
import gc
import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.movingAverage import Sma
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetProfit, GetProfitJP, GetROI, GetFloat,GetPE,GetADR,GetIndustry,GetSector,GetVol,GetMarketCap
from modules.vwap import Vwap
import requests
import yfinance as yf

def main():
    currency = 'USD'
    # currency = 'JPY'

    trades = []

    tradeCsvPath = 'trades_8M.csv'
    if currency == 'JPY':
        tradeCsvPath = 'trades_8M_JP.csv'

    df = pd.read_csv (r'./csv/%s'%(tradeCsvPath), index_col=0)
    df.drop
    trades = json.loads(df.to_json(orient = 'records'))

    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()

    csvPath = "8M"

    industryCsvPath = 'industry.csv'
    df = pd.read_csv (r'./csv/%s'%(industryCsvPath), index_col=0)
    df.drop
    symbols = json.loads(df.to_json(orient = 'records'))

    
    try:
        # symbolArr = ["QQQ","SPY","^N225","^NDX","^GSPC","^FTSE","^GDAXI"]
        symbolArr = ["^GSPC"]

        for symbol in symbols:
            if symbol not in profitSymList: continue
            if symbol not in symbolArr:
                symbolArr.append(symbol)

        # for trade in trades:
        #     symbol = str(trade['symbol'])
        #     if symbol not in profitSymList: continue
        #     if symbol not in symbolArr:
        #         symbolArr.append(symbol)

        for symbol in symbolArr:
            stockInfo = yf.Ticker(symbol)
            hist = stockInfo.history(period="36500d")
            
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            hist.to_csv('./csv/vwap/{}/{}.csv'.format(csvPath,symbol))
            
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