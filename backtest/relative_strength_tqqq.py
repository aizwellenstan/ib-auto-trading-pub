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
from sklearn.svm import SVR
from modules.movingAverage import Sma
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetProfit, GetProfitJP, GetROI, GetFloat,GetPE,GetADR,GetIndustry,GetSector,GetVol,GetMarketCap, GetDebtEquity, GetNetDebt, GetEPS
from modules.vwap import Vwap
from modules.technicalAnalysis import PlotLines
# from modules.trend import GetTrend
import requests
from scipy.signal import lfilter
from modules.riskOfRuin import calcRisk
from collections import defaultdict
from modules.trend import GetTrend
import talib

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]


shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

print(shortableSymList)

cash = 2061
risk = 0.00613800895 #0.06

# fillterDf = pd.read_csv (r'./csv/symbolLst.csv', index_col=0)
# fillterDf.drop
# filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
# filter_sym_list = []
# for i in filter_symbols:
#     filter_sym_list.append(i['symbol'])

# vix_df = pd.read_csv (r'./csv/VIX_History.csv')
# vix_df.drop
# vix_list = json.loads(vix_df.to_json(orient = 'records'))

# arkfund_df = pd.read_csv (r'./csv/ark-fund.csv', index_col=0)
# arkfund_df.drop
# arkfund_list = json.loads(arkfund_df.to_json(orient = 'records'))

# sectorDf = pd.read_csv (r'./csv/sector.csv', index_col=0)
# sectorDf.drop
# secLst = json.loads(sectorDf.to_json(orient = 'records'))
# sectorLst = sectorDf.groupby('sector')['symbol'].apply(list)

def main():
    currency = 'USD'
    # currency = 'JPY'

    trades = []

    tradeCsvPath = 'trades_7MTQQQ.csv'
    if currency == 'JPY':
        tradeCsvPath = 'trades_7M_JP.csv'

    df = pd.read_csv (r'./csv/%s'%(tradeCsvPath), index_col=0)
    df.drop
    trades = json.loads(df.to_json(orient = 'records'))

    basicPoint = 0.01
    if currency == 'JPY':
        basicPoint = 1

    try:
        QQQD1arr = []
        SPYD1arr = []
        VTID1arr = []
        DIAD1arr = []
        IWMD1arr = []
        if currency == 'USD':
            output = open("./pickle/pro/compressed/QQQ7MD1arr.p", "rb")
            gc.disable()
            QQQD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load QQQD1arr finished")
        
            output = open("./pickle/pro/compressed/SPY7MD1arr.p", "rb")
            gc.disable()
            SPYD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load SPYD1arr finished")
        
            output = open("./pickle/pro/compressed/VTI7MD1arr.p", "rb")
            gc.disable()
            VTID1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load VTID1arr finished")
       
            output = open("./pickle/pro/compressed/DIA7MD1arr.p", "rb")
            gc.disable()
            DIAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load DIAD1arr finished")
        
            output = open("./pickle/pro/compressed/IWM7MD1arr.p", "rb")
            gc.disable()
            IWMD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IWMD1arr finished")

            # output = open("./pickle/pro/compressed/XLF7MD1arr.p", "rb")
            # gc.disable()
            # XLFD1arr = pickle.load(output)
            # output.close()
            # gc.enable()
            # print("load XLFD1arr finished")

            # output = open("./pickle/pro/compressed/EEM7MD1arr.p", "rb")
            # gc.disable()
            # EEMD1arr = pickle.load(output)
            # output.close()
            # gc.enable()
            # print("load EEMD1arr finished")

            output = open("./pickle/pro/compressed/UVXY7MD1arr.p", "rb")
            gc.disable()
            UVXYD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load UVXYD1arr finished")

            # output = open("./pickle/pro/compressed/XLE7MD1arr.p", "rb")
            # gc.disable()
            # XLED1arr = pickle.load(output)
            # output.close()
            # gc.enable()
            # print("load XLED1arr finished")

            output = open("./pickle/pro/compressed/IWM7MD1arr.p", "rb")
            gc.disable()
            IWMD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IWMD1arr finished")

            output = open("./pickle/pro/compressed/EWZ7MD1arr.p", "rb")
            gc.disable()
            EWZD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load EWZD1arr finished")

            output = open("./pickle/pro/compressed/EFA7MD1arr.p", "rb")
            gc.disable()
            EFAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load EFAD1arr finished")

            output = open("./pickle/pro/compressed/TLT7MD1arr.p", "rb")
            gc.disable()
            TLTD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load TLTD1arr finished")

            output = open("./pickle/pro/compressed/XLU7MD1arr.p", "rb")
            gc.disable()
            XLUD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLUD1arr finished")

            output = open("./pickle/pro/compressed/SOXL7MD1arr.p", "rb")
            gc.disable()
            SOXLD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load SOXLD1arr finished")

            output = open("./pickle/pro/compressed/XLI7MD1arr.p", "rb")
            gc.disable()
            XLID1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLID1arr finished")

            output = open("./pickle/pro/compressed/SOXS7MD1arr.p", "rb")
            gc.disable()
            SOXSD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load SOXSD1arr finished")

            output = open("./pickle/pro/compressed/XLV7MD1arr.p", "rb")
            gc.disable()
            XLVD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLVD1arr finished")

            output = open("./pickle/pro/compressed/TZA7MD1arr.p", "rb")
            gc.disable()
            TZAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load TZAD1arr finished")

            output = open("./pickle/pro/compressed/XLP7MD1arr.p", "rb")
            gc.disable()
            XLPD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLPD1arr finished")

            output = open("./pickle/pro/compressed/TNA7MD1arr.p", "rb")
            gc.disable()
            TNAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load TNAD1arr finished")

            output = open("./pickle/pro/compressed/IAU7MD1arr.p", "rb")
            gc.disable()
            IAUD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IAUD1arr finished")

            output = open("./pickle/pro/compressed/KRE7MD1arr.p", "rb")
            gc.disable()
            KRED1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load KRED1arr finished")

            output = open("./pickle/pro/compressed/XLK7MD1arr.p", "rb")
            gc.disable()
            XLKD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLKD1arr finished")

            output = open("./pickle/pro/compressed/IEF7MD1arr.p", "rb")
            gc.disable()
            IEFD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IEFD1arr finished")

            output = open("./pickle/pro/compressed/XOP7MD1arr.p", "rb")
            gc.disable()
            XOPD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XOPD1arr finished")

            output = open("./pickle/pro/compressed/IEFA7MD1arr.p", "rb")
            gc.disable()
            IEFAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IEFAD1arr finished")

        hisBarsD1Dict = {}
        hisBarsH1Dict = {}
        profitSymList = []

        if currency == 'USD':
            output = open("./pickle/pro/compressed/hisBarsStocks7MTQQQD1Dict.p", "rb")
            gc.disable()
            hisBarsD1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsD1Dict finished")

            output = open("./pickle/pro/compressed/hisBarsStocks7MTQQQH1Dict.p", "rb")
            gc.disable()
            hisBarsH1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsH1Dict finished")

            profitSymList = GetProfit()
        else:
            output = open("./pickle/pro/compressed/jp/hisBarsStocks7MD1Dict.p", "rb")
            gc.disable()
            hisBarsD1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsD1Dict finished")

            hisBarsH1Dict = {}
            output = open("./pickle/pro/compressed/jp/hisBarsStocks7MH1Dict.p", "rb")
            gc.disable()
            hisBarsH1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsH1Dict finished")

            profitSymList = GetProfitJP()
        
        adrDict = GetADR(currency)
        floatDict = GetFloat(currency)
        industryDict = GetIndustry(currency)
        # roiDict = GetROI(currency)
        volDict = GetVol(currency)
        marketcapDict = GetMarketCap()
        debtEquityDict = GetDebtEquity(currency)
        netDebtDict = GetNetDebt(currency)
        epsDict = GetEPS(currency)
        # sectorDict = GetSector()

        # payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        # first_table = payload[0]
        # second_table = payload[1]
        # df = first_table
        # sp500symbols = df['Symbol'].values.tolist()

        industryListGroup = defaultdict(list)
        for key, val in sorted(industryDict.items()):
            industryListGroup[val].append(key)

        # sectorListGroup = defaultdict(list)
        # for key, val in sorted(sectorDict.items()):
        #     sectorListGroup[val].append(key)

        if currency == 'USD':
            symbolArr = ['TQQQ']
            # for trade in trades:
            #     symbol = str(trade['symbol'])
            #     if symbol not in profitSymList: continue
            #     if symbol not in symbolArr:
            #         symbolArr.append(symbol)

            vwapDfDict = {}
            csvPath = "7M"
            for symbol in symbolArr:
                df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(csvPath,symbol))
                vwapDfDict[symbol] = df

        fee = 1.001392062 * 2
        tpVal = 1.15137614678 #3.69 #2 #5 #2 #3.19148936 #2 #15.42857143 #5.7#5.7#35.2#23.5 #25.8
        maxProfit = 0
        maxTpVal = 6.766666667
        maxSlVal = 0
        maxMarCapLimit = 0
        maxVolavgLimit = 0

        hisBarsD1arr = []

        total = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        for trade in trades:
            industryLeaderBoard = {}
            epsLeaderBoard = {}
            industryAvgBoard = {}
            sectorLeaderBoard = {}
            # roiLeaderBoard = {}
            # roiLastBoard = {}
            sectorLeaderBoard = {}
            sectorAvgBoard = {}
            symbol = str(trade['symbol'])
            # if symbol not in profitSymList: continue
            # if currency == 'USD':
            #     if symbol in shortableSymList: continue
            adrRange = adrDict[symbol]
            
            backtestTime = trade['time']
            op = trade['op']
            sl = trade['sl']
            sl = op - 0.14
            
            sl = NormalizeFloat(op - adrRange * 0.05, basicPoint)
            if adrRange > 0.14:
                sl = NormalizeFloat(op - adrRange * 0.35, basicPoint)

            trade['sl'] = sl
            tp = op + adrRange * 5.57 #1.58
            tp = NormalizeFloat(tp, basicPoint)

            if op - sl < basicPoint * 2: continue
                
            vol = 6#int((1000)/(op-sl))
            # vol = int((cash*risk)/(op-sl))
            trade['vol'] = vol
            trade['result'] = ''
            trade['total'] = 0
            if(vol<2): continue
            
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d')
            
            if currency == 'USD':
                backtestTime = backtestTime + timedelta(hours = 22) +timedelta(minutes = 30)
            else:
                backtestTime = backtestTime + timedelta(hours = 9) + timedelta(minutes = 0) 

            dataD1 = hisBarsD1Dict[symbol]
            if(len(dataD1) < 16):continue
            hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            
            if len(hisBarsD1) < 16: continue
            hisBarsD1 = hisBarsD1[::-1]

            if (
                hisBarsD1[4].high-hisBarsD1[4].low < 0.01 or
                hisBarsD1[3].high-hisBarsD1[3].low < 0.01 or
                hisBarsD1[2].high-hisBarsD1[2].low < 0.01 or
                hisBarsD1[1].high-hisBarsD1[1].low < 0.01
            ): continue

            if len(hisBarsD1) > 41:
                if (
                    abs(hisBarsD1[1].close - hisBarsD1[20].open) < 0.01 or
                    abs(hisBarsD1[21].close - hisBarsD1[40].open) < 0.01
                ): continue
            
            # if hisBarsD1[0].open < hisBarsD1[1].close * 1.007: 
            #     continue
            
            if hisBarsD1[0].open < hisBarsD1[1].close * 1.02: 
                continue

            # if symbol in shortableSymList:
            #     upper, lower = PlotLines(hisBarsD1)
            #     if lower < -0.17: continue
            #     if upper < -0.45: continue

            # if currency == 'USD':
            #     vwapDf = vwapDfDict[symbol]
            #     mask = vwapDf.Date < str(backtestTime.date())
            #     vwapDf = vwapDf.loc[mask]

            #     # machineLearn
            #     days = list()
            #     vwapPrices = list()
            #     dfVwap = vwapDf.loc[:, 'Vwap']
            #     for i in range(len(dfVwap)):
            #         days.append([i])
            #     for vwap in dfVwap:
            #         vwapPrices.append(vwap)
            #     rbfSvr = SVR(kernel='rbf', C=1000.0, gamma=0.85)
            #     rbfSvr.fit(days, vwapPrices)
            #     predictNum = [[len(dfVwap)+1]]
            #     predictPrice = rbfSvr.predict(predictNum)
               
            #     if predictPrice < hisBarsD1[1].close * 0.32:
            #         continue

            #     # polySvr = SVR(kernel='poly', C=1000.0, degree=2)
            #     # polySvr.fit(days, vwapPrices)

            #     # predictPrice = polySvr.predict(predictNum)

            #     vwap = vwapDf.iloc[-1].Vwap

            #     # if symbol in shortableSymList:
            #     #     bias = (predictPrice-vwap)/vwap
            #     #     if bias < -0.42: continue

            #     # volume = (
            #     #     vwapDf.iloc[-4].Volume +
            #     #     vwapDf.iloc[-3].Volume +
            #     #     vwapDf.iloc[-2].Volume +
            #     #     vwapDf.iloc[-1].Volume
            #     # ) / 2
            #     # marketcap = marketcapDict[symbol]

            #     # if volume/marketcap < 0.00018: continue

            #     if len(hisBarsD1) > 5:
            #         # mfi
            #         typicalPrice = (
            #             vwapDf['Close']+vwapDf['High']
            #             +vwapDf['Low']
            #         ) / 3

            #         moneyFlow = typicalPrice * vwapDf['Volume']

            #         negativeFlow = []
            #         positiveFlow = []

            #         period = 5
            #         for i in range(1, period+1):
            #             if typicalPrice[i] > typicalPrice[i-1]:
            #                 positiveFlow.append(moneyFlow[i-1])
            #                 negativeFlow.append(0)
            #             elif typicalPrice[i] < typicalPrice[i-1]:
            #                 positiveFlow.append(0)
            #                 negativeFlow.append(moneyFlow[i-1])
            #             else:
            #                 positiveFlow.append(0)
            #                 negativeFlow.append(0)

            #         positiveMf = []
            #         negativeMf = []

                
            #         for i in range(period-1, len(positiveFlow)):
            #             positiveMf.append(sum(positiveFlow[i+1-period:i+1]))
            #         for i in range(period-1, len(negativeFlow)):
            #             negativeMf.append(sum(negativeFlow[i+1-period:i+1]))

            #         mfi = 100*(np.array(positiveMf))/(np.array(positiveMf)+np.array(negativeMf))
            #         if mfi[-1] > 87: continue

            #         negativeFlow = []
            #         positiveFlow = []

            #         # period = 21
            #         # for i in range(1, period+1):
            #         #     if typicalPrice[i] > typicalPrice[i-1]:
            #         #         positiveFlow.append(moneyFlow[i-1])
            #         #         negativeFlow.append(0)
            #         #     elif typicalPrice[i] < typicalPrice[i-1]:
            #         #         positiveFlow.append(0)
            #         #         negativeFlow.append(moneyFlow[i-1])
            #         #     else:
            #         #         positiveFlow.append(0)
            #         #         negativeFlow.append(0)

            #         # positiveMf = []
            #         # negativeMf = []

                
            #         # for i in range(period-1, len(positiveFlow)):
            #         #     positiveMf.append(sum(positiveFlow[i+1-period:i+1]))
            #         # for i in range(period-1, len(negativeFlow)):
            #         #     negativeMf.append(sum(negativeFlow[i+1-period:i+1]))

            #         # mfi = 100*(np.array(positiveMf))/(np.array(positiveMf)+np.array(negativeMf))
            #         # if mfi[-1] > 73: continue

            #     # period = 9
            #     # for i in range(1, period+1):
            #     #     if typicalPrice[i] > typicalPrice[i-1]:
            #     #         positiveFlow.append(moneyFlow[i-1])
            #     #         negativeFlow.append(0)
            #     #     elif typicalPrice[i] < typicalPrice[i-1]:
            #     #         positiveFlow.append(0)
            #     #         negativeFlow.append(moneyFlow[i-1])
            #     #     else:
            #     #         positiveFlow.append(0)
            #     #         negativeFlow.append(0)

            #     # positiveMf = []
            #     # negativeMf = []

               
            #     # for i in range(period-1, len(positiveFlow)):
            #     #     positiveMf.append(sum(positiveFlow[i+1-period:i+1]))
            #     # for i in range(period-1, len(negativeFlow)):
            #     #     negativeMf.append(sum(negativeFlow[i+1-period:i+1]))

            #     # mfi = 100*(np.array(positiveMf))/(np.array(positiveMf)+np.array(negativeMf))
            #     # if mfi[-1] > 82: continue
                
            #     # obv = []
            #     # obv.append(0)
            #     # for i in range(1, len(vwapDf.Close)):
            #     #     if vwapDf.Close[i] > vwapDf.Close[i-1]:
            #     #         obv.append(obv[-1] + vwapDf.Volume[i])
            #     #     elif vwapDf.Close[i] < vwapDf.Close[i-1]:
            #     #         obv.append(obv[-1] - vwapDf.Volume[i])
            #     #     else obv.append(obv[-1])

            #     # obv = obv[::-1]
            #     # SmaObvD1 = Sma(obv[1:26], 25)
            #     # bias = (obv[-1]-SmaObvD1)/SmaObvD1
            #     # if bias < adjVal: continue 


            #     bias = (hisBarsD1[1].close-vwap)/vwap
            #     if bias > 1.07: continue
            #     if symbol in shortableSymList:
            #         if bias > 0.7: continue

            #     bias = (hisBarsD1[1].low-vwap)/vwap
            #     if bias > 1.31: continue
            #     if symbol in shortableSymList:
            #         if bias > 0.71: continue

            #     volList = []
            #     volPeriod = 2
            #     for i in range(1,volPeriod+1):
            #         volList.append(vwapDf.iloc[-i].Volume)
            #     SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #     bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #     if bias < -0.53: continue

            #     volPeriod = 3
            #     volList.append(vwapDf.iloc[-volPeriod].Volume)
            #     SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #     bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #     if bias < -0.69: continue

            #     volPeriod = 4
            #     volList.append(vwapDf.iloc[-volPeriod].Volume)
            #     SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #     bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #     if bias < -0.79: continue

            #     if len(hisBarsD1) > 8:
            #         volList = []
            #         volPeriod = 8
            #         for i in range(1,volPeriod+1):
            #             volList.append(vwapDf.iloc[-i].Volume)
            #         SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #         bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #         if bias < -0.67: continue

            #         volPeriod = 10
            #         volList.append(vwapDf.iloc[-volPeriod].Volume)
            #         SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #         bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #         if bias < -0.77: continue

            #         volList = []
            #         volPeriod = 14
            #         for i in range(1,volPeriod+1):
            #             volList.append(vwapDf.iloc[-i].Volume)
            #         SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #         bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #         if bias < -0.69: continue

            #         if len(hisBarsD1) > 17:
            #             volList = []
            #             volPeriod = 17
            #             for i in range(1,volPeriod+1):
            #                 volList.append(vwapDf.iloc[-i].Volume)
            #             SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #             bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #             if bias < -0.64: continue

            #             # volList = []
            #             # volPeriod = 27
            #             # for i in range(1,volPeriod+1):
            #             #     volList.append(vwapDf.iloc[-i].Volume)
            #             # SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            #             # bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            #             # if bias < -0.76: continue

            #     # if symbol in shortableSymList:
            #     #     bias = ((hisBarsD1[1].high+hisBarsD1[1].low)/2-vwap)/vwap
            #     #     if bias > 0.74: continue

            #     # if symbol in shortableSymList:
            #     #     if (
            #     #         hisBarsD1[1].close < hisBarsD1[1].open and
            #     #         vwapDf.iloc[-1].Volume > vwapDf.iloc[-2].Volume
            #     #     ): continue

            # if symbol in shortableSymList:
            #     if len(hisBarsD1) > 121:
            #         if hisBarsD1[1].close / hisBarsD1[120].close < 0.44:
            #             continue
            #     if len(hisBarsD1) > 181:
            #         if hisBarsD1[1].close / hisBarsD1[180].close < 0.64:
            #             continue

            # if currency == 'USD':
            #     hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),QQQD1arr))
            #     hisBarsSPYD1 = list(filter(lambda x:x.date <= backtestTime.date(),SPYD1arr))
            #     hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
            #     hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
            #     hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
            #     # hisBarsXLFD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLFD1arr))
            #     # hisBarsEEMD1 = list(filter(lambda x:x.date <= backtestTime.date(),EEMD1arr))
            #     hisBarsUVXYD1 = list(filter(lambda x:x.date <= backtestTime.date(),UVXYD1arr))
            #     # hisBarsXLED1 = list(filter(lambda x:x.date <= backtestTime.date(),XLED1arr))
            #     hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
            #     # hisBarsEWZD1 = list(filter(lambda x:x.date <= backtestTime.date(),EWZD1arr))
            #     # hisBarsEFAD1 = list(filter(lambda x:x.date <= backtestTime.date(),EFAD1arr))
            #     hisBarsTLTD1 = list(filter(lambda x:x.date <= backtestTime.date(),TLTD1arr))
            #     hisBarsXLUD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLUD1arr))
            #     hisBarsSOXLD1 = list(filter(lambda x:x.date <= backtestTime.date(),SOXLD1arr))
            #     hisBarsXLID1 = list(filter(lambda x:x.date <= backtestTime.date(),XLID1arr))
            #     # hisBarsSOXSD1 = list(filter(lambda x:x.date <= backtestTime.date(),SOXSD1arr))
            #     # hisBarsXLVD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLVD1arr))
            #     # hisBarsTZAD1 = list(filter(lambda x:x.date <= backtestTime.date(),TZAD1arr))
            #     # hisBarsXLPD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLPD1arr))
            #     # hisBarsTNAD1 = list(filter(lambda x:x.date <= backtestTime.date(),TNAD1arr))
            #     # hisBarsIAUD1 = list(filter(lambda x:x.date <= backtestTime.date(),IAUD1arr))
            #     # hisBarsKRED1 = list(filter(lambda x:x.date <= backtestTime.date(),KRED1arr))
            #     # hisBarsXLKD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLKD1arr))
            #     # hisBarsIEFD1 = list(filter(lambda x:x.date <= backtestTime.date(),IEFD1arr))
            #     # hisBarsXOPD1 = list(filter(lambda x:x.date <= backtestTime.date(),XOPD1arr))
            #     # hisBarsIEFAD1 = list(filter(lambda x:x.date <= backtestTime.date(),IEFAD1arr))

            #     hisBarsQQQD1 = hisBarsQQQD1[::-1]
            #     hisBarsSPYD1 = hisBarsSPYD1[::-1]
            #     hisBarsVTID1 = hisBarsVTID1[::-1]
            #     hisBarsDIAD1 = hisBarsDIAD1[::-1]
            #     hisBarsIWMD1 = hisBarsIWMD1[::-1]
            #     # hisBarsXLFD1 = hisBarsXLFD1[::-1]
            #     # hisBarsEEMD1 = hisBarsEEMD1[::-1]
            #     hisBarsUVXYD1 = hisBarsUVXYD1[::-1]
            #     # hisBarsXLED1 = hisBarsXLED1[::-1]
            #     # hisBarsEWZD1 = hisBarsEWZD1[::-1]
            #     # hisBarsEFAD1 = hisBarsEFAD1[::-1]
            #     hisBarsTLTD1 = hisBarsTLTD1[::-1]
            #     hisBarsXLUD1 = hisBarsXLUD1[::-1]
            #     hisBarsSOXLD1 = hisBarsSOXLD1[::-1]
            #     hisBarsXLID1 = hisBarsXLID1[::-1]
            #     # hisBarsSOXSD1 = hisBarsSOXSD1[::-1] #bear
            #     # hisBarsXLVD1 = hisBarsXLVD1[::-1]
            #     # hisBarsTZAD1 = hisBarsTZAD1[::-1] #bear
            #     # hisBarsXLPD1 = hisBarsXLPD1[::-1]
            #     # hisBarsTNAD1 = hisBarsTNAD1[::-1]
            #     # hisBarsIAUD1 = hisBarsIAUD1[::-1]
            #     # hisBarsKRED1 = hisBarsKRED1[::-1]
            #     # hisBarsXLKD1 = hisBarsXLKD1[::-1]
            #     # hisBarsIEFD1 = hisBarsIEFD1[::-1] #tresury
            #     # hisBarsXOPD1 = hisBarsXOPD1[::-1]
            #     # hisBarsIEFAD1 = hisBarsIEFAD1[::-1]

            #     if symbol in shortableSymList:
            #         upper, lower = PlotLines(hisBarsVTID1)
            #         if lower < -0.4: continue
            #         if upper < -0.23: continue

            #         upper, lower = PlotLines(hisBarsDIAD1)
            #         if lower < -0.61: continue
            #         if upper < -0.34: continue

            #         upper, lower = PlotLines(hisBarsIWMD1)
            #         if lower < -0.42: continue

            #         upper, lower = PlotLines(hisBarsUVXYD1)
            #         if lower > 0.11: continue

            #         upper, lower = PlotLines(hisBarsTLTD1)
            #         if upper < -0.12: continue

            #         upper, lower = PlotLines(hisBarsXLUD1)
            #         if lower < -0.26: continue

            #         upper, lower = PlotLines(hisBarsXLID1)
            #         if lower < -0.29: continue
                    
            #     gapRange = hisBarsD1[0].open/hisBarsD1[1].high
            #     qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].high
            #     iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].high
                
            #     if (
            #         gapRange < qqqGapRange * 0.937 or
            #         gapRange < iwmGapRange * 0.937
            #     ): continue

            #     gapRange = hisBarsD1[0].open/hisBarsD1[1].close
            #     qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].close
            #     spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].close
            #     vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].close
            #     diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].close
            #     iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].close
                
            #     if (
            #         gapRange < qqqGapRange * 1.013 or
            #         gapRange < spyGapRange * 1.013 or
            #         gapRange < vtiGapRange * 1.013 or
            #         gapRange < diaGapRange * 1.013 or
            #         gapRange < iwmGapRange * 1.013
            #     ): continue

            #     if (
            #         hisBarsQQQD1[1].close > hisBarsQQQD1[1].open * 1.0003 and
            #         hisBarsSPYD1[1].close > hisBarsSPYD1[1].open * 1.0003 and
            #         hisBarsVTID1[1].close > hisBarsVTID1[1].open * 1.0003 and
            #         hisBarsDIAD1[1].close > hisBarsDIAD1[1].open * 1.0003 and
            #         hisBarsIWMD1[1].close > hisBarsIWMD1[1].open * 1.0003 and
            #         hisBarsD1[1].close < hisBarsD1[1].open * 0.98
            #     ): continue

            #     if (
            #         hisBarsQQQD1[2].close > hisBarsQQQD1[2].open and
            #         hisBarsQQQD1[1].close > hisBarsQQQD1[1].open and
            #         hisBarsSPYD1[2].close > hisBarsSPYD1[2].open and
            #         hisBarsSPYD1[1].close > hisBarsSPYD1[1].open and
            #         hisBarsD1[2].close < hisBarsD1[2].open * 0.97 and
            #         hisBarsD1[1].close < hisBarsD1[1].open * 0.97
            #     ): continue

            #     # if (
            #     #     hisBarsQQQD1[2].close > hisBarsQQQD1[2].open and
            #     #     hisBarsQQQD1[1].close > hisBarsQQQD1[1].open and
            #     #     hisBarsSPYD1[2].close > hisBarsSPYD1[2].open and
            #     #     hisBarsSPYD1[1].close > hisBarsSPYD1[1].open and
            #     #     hisBarsVTID1[2].close > hisBarsVTID1[2].open and
            #     #     hisBarsVTID1[1].close > hisBarsVTID1[1].open and
            #     #     hisBarsDIAD1[2].close > hisBarsDIAD1[2].open and
            #     #     hisBarsDIAD1[1].close > hisBarsDIAD1[1].open and
            #     #     hisBarsD1[2].close < hisBarsD1[2].open * 0.98 and
            #     #     hisBarsD1[1].close < hisBarsD1[1].open * 0.98
            #     # ): continue

            # if sl < hisBarsD1[1].close: sl = hisBarsD1[1].close

            # maxHigh = hisBarsD1[1].high
            # for i in range(2,3):
            #     if hisBarsD1[i].high > maxHigh:
            #         maxHigh = hisBarsD1[i].high

            # minLow = hisBarsD1[1].low
            # for i in range(2,3):
            #     if hisBarsD1[i].low < minLow:
            #         minLow = hisBarsD1[i].low

            # if hisBarsD1[1].close-minLow > 0:
            #     if not (
            #         (maxHigh-hisBarsD1[1].close) /
            #         (hisBarsD1[1].close-minLow) > 0.03
            #     ): continue

            # hisBarsD1avgPriceArr = []
            # hisBarsD1closeArr = []
            # for d in hisBarsD1:
            #     avgPrice = (d.high+d.low) / 2
            #     hisBarsD1avgPriceArr.append(avgPrice)
            #     hisBarsD1closeArr.append(d.close)

            # if symbol in shortableSymList:
            #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:4], 3)
            #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            #     if bias < -0.17: continue

            #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:5], 4)
            #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            #     if bias < -0.07: continue
                
            #     # SmaD1 = Sma(hisBarsD1avgPriceArr[1:23], 22)
            #     # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            #     # if bias < -0.43: continue

            # if not (
            #     hisBarsD1[1].close <= hisBarsD1[1].open or
            #     (
            #         hisBarsD1[1].close > hisBarsD1[4].high and
            #         hisBarsD1[1].close > hisBarsD1[3].high and
            #         hisBarsD1[1].close > hisBarsD1[2].high
            #     )
            # ):
            #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:29], 28)
            #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            #     if bias < -0.17: continue

            # if symbol in shortableSymList:
            #     if hisBarsD1[1].close / hisBarsD1[1].open > 1.08: continue
            #     if hisBarsD1[1].close / hisBarsD1[2].close > 1.12: continue
            #     if hisBarsD1[1].close / hisBarsD1[3].close > 1.08: continue
            #     if hisBarsD1[1].close / hisBarsD1[3].open > 1.47: continue
            #     if hisBarsD1[1].close / hisBarsD1[4].close > 1.15: continue

            # if (
            #     hisBarsD1[4].close >= hisBarsD1[4].open and
            #     hisBarsD1[2].close >= hisBarsD1[2].open and
            #     hisBarsD1[1].close >= hisBarsD1[1].open
            # ):
            #     if hisBarsD1[1].close / hisBarsD1[5].open > 1.08:
            #         continue

            # if not (
            #     (
            #         hisBarsD1[2].close < hisBarsD1[2].open and
            #         hisBarsD1[1].close > hisBarsD1[1].open
            #     ) or
            #     (
            #         hisBarsD1[4].close < hisBarsD1[4].open and
            #         hisBarsD1[3].close > hisBarsD1[3].open and
            #         hisBarsD1[2].close > hisBarsD1[2].open and
            #         hisBarsD1[1].close < hisBarsD1[1].open
            #     ) or
            #     hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673 or
            #     (
            #         hisBarsD1[2].close > hisBarsD1[2].open and
            #         hisBarsD1[1].close > hisBarsD1[1].open
            #     )
            # ):
            #     if hisBarsD1[1].close / hisBarsD1[5].open > 1.18: continue

            # if symbol in shortableSymList: 
            #     SmaD1 = Sma(hisBarsD1closeArr[1:51], 50)
            #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            # if bias > 0.55: continue
            # if symbol in shortableSymList:
            #     if bias < -0.31: continue

            # if not (
            #     (
            #         hisBarsD1[2].close > hisBarsD1[2].open and
            #         hisBarsD1[1].close < hisBarsD1[1].open
            #     ) or
            #     (
            #         ((hisBarsD1[4].high-hisBarsD1[4].close) / (hisBarsD1[4].high-hisBarsD1[4].low) > 0.76) and
            #         ((hisBarsD1[3].high-hisBarsD1[3].close) / (hisBarsD1[3].high-hisBarsD1[3].low) > 0.76) and
            #         ((hisBarsD1[2].high-hisBarsD1[2].close) / (hisBarsD1[2].high-hisBarsD1[2].low) > 0.76) and
            #         ((hisBarsD1[1].high-hisBarsD1[1].close) / (hisBarsD1[1].high-hisBarsD1[1].low) > 0.76)
            #     )
            # ):
            #     SmaD1 = Sma(hisBarsD1closeArr[1:9], 8)
            #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            #     if bias < -0.09: continue

            # SmaD1 = Sma(hisBarsD1closeArr[1:26], 25)
            # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            # if bias < -0.2: continue

            # SmaD1 = Sma(hisBarsD1closeArr[1:101], 100)
            # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
            # if bias < -0.54: continue

            # days = list()
            # vwapPrices = list()
            # dfVwap = dfVwap.tail(15)
            # for i in range(len(dfVwap)):
            #     days.append([i])
            # for vwap in dfVwap:
            #     vwapPrices.append(vwap)
            # linSvr = SVR(kernel='linear', C=1000.0)
            # linSvr.fit(days, vwapPrices)
            # predictNum = [[len(dfVwap)+1]]
            # predictPrice = linSvr.predict(predictNum)

            # if predictPrice < hisBarsD1[1].close * 0.58:
            #     continue

            # # Industry
            # if symbol in shortableSymList:
            #     industryCheck = False
            #     industryCheckPeriod = 4
            #     curIndustryGain = hisBarsD1[1].close / hisBarsD1[industryCheckPeriod].open
            #     industryLeader = curIndustryGain
            #     if symbol not in industryDict: continue
            #     industry = industryDict[symbol]
            #     groupList = industryListGroup[industry]
            #     symVol = volDict[symbol]
            #     if symbol not in epsDict: continue
            #     curEps = epsDict[symbol]
            #     epsLeader = curEps
            #     if len(groupList) > 1:
            #         if industry in industryLeaderBoard:
            #             industryLeader = industryLeaderBoard[industry]
            #         else:
            #             for sym2 in groupList:
            #                 if sym2 not in hisBarsD1Dict: continue
            #                 sym2Vol = volDict[sym2]
            #                 if sym2Vol < 210187: continue

            #                 sym2dataD1 = hisBarsD1Dict[sym2]
                            
            #                 sym2hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),sym2dataD1))
            #                 if len(sym2hisBarsD1) < 5:continue
            #                 sym2hisBarsD1 = sym2hisBarsD1[::-1]
            #                 industryGain = sym2hisBarsD1[1].close / sym2hisBarsD1[industryCheckPeriod].open
            #                 if industryGain > industryLeader:
            #                     industryLeader = industryGain
            #                 if sym2 not in epsDict: continue
            #                 eps = epsDict[sym2]
            #                 if eps > epsLeader:
            #                     epsLeader = eps
            #             industryLeaderBoard[industry] = industryLeader
            #             # epsLeaderBoard[industry] = epsLeader
            #     else:
            #         industryCheck = True
                        
            #     qqqGain = hisBarsQQQD1[1].close / hisBarsQQQD1[industryCheckPeriod].open
            #     spyGain = hisBarsSPYD1[1].close / hisBarsSPYD1[industryCheckPeriod].open
            #     # vtiGain = hisBarsVTID1[1].close / hisBarsVTID1[industryCheckPeriod].open
            #     # diaGain = hisBarsDIAD1[1].close / hisBarsDIAD1[industryCheckPeriod].open
            #     # iwmGain = hisBarsIWMD1[1].close / hisBarsIWMD1[industryCheckPeriod].open

            #     if (
            #         industryLeader > qqqGain * 0.95 and
            #         industryLeader > spyGain * 0.96 
            #         # industryLeader > diaGain * 0.94
            #         # industryLeader > iwmGain * 0.94
            #         # industryLeader > vtiGain * 0.96
            #     ):
            #         if (
            #             curIndustryGain > industryLeader * 0.47
            #         ):  industryCheck = True
            #     if not industryCheck: continue

            # # Sector
            # sectorCheck = False
            # sectorCheckPeriod = 4
            # curSectorGain = hisBarsD1[1].close / hisBarsD1[sectorCheckPeriod].open
            # sectorLeader = curSectorGain
            # sector = sectorDict[symbol]
            # groupList = sectorListGroup[sector]
            # if len(groupList) > 1:
            #     if sector in sectorLeaderBoard:
            #         sectorLeader = sectorLeaderBoard[sector]
            #     else:
            #         for sym2 in groupList:
            #             if sym2 not in hisBarsD1Dict: continue
            #             sym2dataD1 = hisBarsD1Dict[sym2]
                        
            #             sym2hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),sym2dataD1))
            #             if len(sym2hisBarsD1) < 5:continue
            #             sym2hisBarsD1 = sym2hisBarsD1[::-1]
            #             sectorGain = sym2hisBarsD1[1].close / sym2hisBarsD1[sectorCheckPeriod].open
            #             if sectorGain > sectorLeader:
            #                 sectorLeader = sectorGain
            #         sectorLeaderBoard[sector] = sectorLeader
            # else:
            #     sectorCheck = True
                        
            # if (
            #     curSectorGain > sectorLeader * adjVal
            # ):  sectorCheck = True
            # if not sectorCheck: continue

            # if (
            #     hisBarsD1[9].close < hisBarsD1[9].open and
            #     hisBarsD1[8].close < hisBarsD1[8].open and
            #     hisBarsD1[7].close < hisBarsD1[7].open and
            #     hisBarsD1[6].close < hisBarsD1[6].open and
            #     hisBarsD1[5].close < hisBarsD1[5].open and
            #     hisBarsD1[4].close < hisBarsD1[4].open and
            #     hisBarsD1[3].close < hisBarsD1[3].open and
            #     hisBarsD1[2].close < hisBarsD1[2].open and
            #     hisBarsD1[1].close < hisBarsD1[1].open
            # ):  continue

            # trend = GetTrend(hisBarsD1closeArr[1:226])

            # if (
            #     hisBarsD1[26].close > hisBarsD1[26].open and
            #     hisBarsD1[22].close < hisBarsD1[22].open and
            #     hisBarsD1[20].close > hisBarsD1[20].open and
            #     hisBarsD1[7].close > hisBarsD1[7].open and
            #     hisBarsD1[6].close > hisBarsD1[6].open and
            #     hisBarsD1[1].close > hisBarsD1[1].open and
            #     trend < 0
            # ): continue

            # df = df.assign(nextOpen=df.open.shift(-1))
            # df = df.assign(nextClose=df.close.shift(-1))
            # bearCandle = df['nextClose'] < df['nextOpen']

            # if op > 100:
            #     df = df.assign(h1l1=df.high/df.low)
            #     avgH1L1 = df.loc[bearCandle, 'h1l1'].mean()

            #     H1L1 = hisBarsD1[1].high / hisBarsD1[1].low
            #     if (
            #         H1L1 > avgH1L1
            #     ): continue

                # 8b dwn
                # if(
                #     hisBarsD1[9].close < hisBarsD1[9].open
                #     and hisBarsD1[8].close < hisBarsD1[8].open
                #     and hisBarsD1[7].close < hisBarsD1[7].open
                #     and hisBarsD1[6].close < hisBarsD1[6].open
                #     and hisBarsD1[5].close < hisBarsD1[5].open
                #     and hisBarsD1[4].close < hisBarsD1[4].open
                #     and hisBarsD1[3].close < hisBarsD1[3].open
                #     and hisBarsD1[2].close < hisBarsD1[2].open
                # ):  continue

                # if (
                #     hisBarsD1[3].close > hisBarsD1[3].open
                #     and hisBarsD1[2].close < hisBarsD1[2].open
                #     and hisBarsD1[1].close > hisBarsD1[1].open
                #     and hisBarsD1[2].high > hisBarsD1[3].high
                #     and hisBarsD1[1].high < hisBarsD1[2].high
                #     and hisBarsD1[1].close < hisBarsD1[2].close
                # ): continue

                # Topping Tails
                # ohlcDf = df[:-1]
                # ohlcDf = ohlcDf.assign(
                #     hchl = (
                #                 (ohlcDf.high - ohlcDf.close)/
                #                 (ohlcDf.high - ohlcDf.low)
                #     )
                # )
                # ohlcDf = ohlcDf.assign(nextOpen=ohlcDf.open.shift(-1))
                # ohlcDf = ohlcDf.assign(nextClose=ohlcDf.close.shift(-1))
                # bearCandle = ohlcDf['nextClose'] < ohlcDf['nextOpen']
                # avgHCHL = ohlcDf.loc[bearCandle, 'hchl'].mean()
                # HCHL = (
                #             (hisBarsD1[1].high - hisBarsD1[1].close)
                #             / (hisBarsD1[1].high - hisBarsD1[1].low)
                # )

                # if (
                #     HCHL > avgHCHL * 0.84
                # ): continue 

                # period = 11
                # df['Sma'] = df['close'].rolling(window=period).mean()
                # df['bias'] = (df['close']-df['Sma'])/df['Sma']
                # bearBias = df['bias'] < 0
                # avgBearBias = df.loc[bearBias, 'bias'].mean()

                # if (
                #     df.iloc[-2]['bias'] > avgBearBias
                # ): continue

                # momentumPeriod = 62
                # momentumDf = momentumDf.assign(c30=momentumDf.close.shift(momentumPeriod))
                # momentumDf = momentumDf.assign(momentum=momentumDf.close/momentumDf.c30)
                # momentumDf = momentumDf.assign(nextOpen=momentumDf.open.shift(-1))
                # momentumDf = momentumDf.assign(nextClose=momentumDf.close.shift(-1))

                # bullCandle = momentumDf['nextClose'] > momentumDf['nextOpen']

                # avgMomentum= momentumDf.loc[bullCandle, 'momentum'].mean()

                # momentumDf = momentumDf.iloc[momentumPeriod:, :]

                # if (
                #     hisBarsD1[1].close/hisBarsD1[momentumPeriod].close > avgMomentum
                # ): continue

                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # df['Sma'] = df['close'].rolling(window=20).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=20).mean()
                # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=20).std()
                # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 15
                # df['Sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 14
                # df['Sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 4
                # df['Sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue
            
                # Ark-fund
                # ark_fund = False
                # ark_fund_sell = False

                # TRADE_STATUS_URL = "http://127.0.0.1:8000/api/v1/stock/trades?symbol="+symbol
                # res = requests.get(TRADE_STATUS_URL, timeout=10)
                # html = res.text
                # if res.status_code == 200 and "no trades listed" not in html:
                #     r = res.json()['trades']
                #     for i in r:
                #         date = dt.strptime(i['date'], '%Y-%m-%d')
                #         date_end = date + timedelta(days=1)
                #         if date_end.isoweekday()==5:
                #             date_end += timedelta(days=3)
                #         direction = i['direction']
                #         if date >= backtestTime and backtestTime <= date_end:
                #             if direction == 'Sell':
                #                 ark_fund_sell = True
            
                # if ark_fund_sell:   continue

                # hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),hisBarsQQQD1arr))
                # hisBarsQQQD1 = hisBarsQQQD1[::-1]

                # hisBarsQQQD1closeArr = []
                # for d in hisBarsQQQD1:
                #     hisBarsQQQD1closeArr.append(d.close)

            # lowestBar = 1
            # minLow = hisBarsD1[1].low
            # for i in range(2,16):
            #     if hisBarsD1[i].low < minLow:
            #         minLow = hisBarsD1[i].low
            #         lowestBar = i

            # tp = op + adrRange / lowestBar * 91.91
            # tp = NormalizeFloat(tp, 0.01)

            # lowestBar = 1
            # minLow = hisBarsD1[1].low
            # for i in range(2,16):
            #     if hisBarsD1[i].low < minLow:
            #         minLow = hisBarsD1[i].low
            #         lowestBar = i

            # tp = hisBarsD1[1].close + adrRange / lowestBar * 127.44
            # tp = NormalizeFloat(tp, 0.01)

            # if currency == 'USD' and symbol not in shortableSymList:
            #     tp = hisBarsD1[1].close + adrRange * 28.4
            # else:
            #     tp = hisBarsD1[1].close + adrRange * 17.8

            eod = True
            
            dataH1 = hisBarsH1Dict[symbol]
            if(len(dataH1) < 6):
                continue

            testhisBarsH1 = list(filter(lambda x:x.date >= backtestTime,dataH1))
            trade['status'] = ''
            
            cancelTime = backtestTime+timedelta(minutes=38)
            for i in testhisBarsH1:
                if i.high >= op:
                    if i.date >= cancelTime: continue
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                endTime = backtestTime+timedelta(minutes=255)
                for i in testhisBarsH1:
                    if i.date >= triggeredTime:
                        if i.date == triggeredTime:
                            if i.high >= tp:
                                net = (tp-op)*vol - fee
                                trade['total'] = net
                                if(net > 0):
                                    trade['result'] = 'profit'
                                    totalNetProfit += net
                                    win += 1
                                else:
                                    trade['result'] = 'loss'
                                    totalNetLoss += net
                                    loss += 1
                                total += net
                                break
                        else:
                            if i.low <= sl:
                                net = (sl-op)*vol - fee
                                trade['total'] = net
                                trade['result'] = 'loss'
                                totalNetLoss += net
                                loss += 1
                                total += net
                                break

                            if i.high >= tp:
                                net = (tp-op)*vol - fee
                                trade['total'] = net
                                if(net > 0):
                                    trade['result'] = 'profit'
                                    totalNetProfit += net
                                    win += 1
                                else:
                                    trade['result'] = 'loss'
                                    totalNetLoss += net
                                    loss += 1
                                total += net
                                break

                            if eod:
                                if i.date >= endTime:
                                    # # print(symbol," close ",i.date)
                                    # if(i.open > (op-sl)*2 and sl < op):
                                    #     newSl = op + (op-sl)
                                    #     # newSl = op + 0.01
                                    #     if(i.open > newSl and newSl > sl):
                                    #         sl = newSl
                                    #     # newSl = NormalizeFloat((i.low + op) / 2,op,sl)
                                    #     # if newSl > sl:
                                    #     #     sl = newSl
                                    # print(i.date)
                                    if(i.open > op):
                                        net = (i.open-op)*vol - fee
                                        trade['total'] = net
                                        if(net > 0):
                                            trade['result'] = 'profit close'
                                            totalNetProfit += net
                                            win += 1
                                        else:
                                            trade['result'] = 'loss close'
                                            totalNetLoss += net
                                            loss += 1
                                        total += net
                                    else:
                                        net = (i.open-op)*vol - fee
                                        trade['total'] = net
                                        trade['result'] = 'loss close'
                                        totalNetLoss += net
                                        loss += 1
                                        total += net
                                    break
        winrate = 0
        if(win+loss>0):
            winrate = win/(win+loss)
        profitfactor =0
        if(abs(totalNetLoss)>0):
            profitfactor = totalNetProfit/abs(totalNetLoss)
        elif(totalNetProfit>0):
            profitfactor = 99.99
        print("total",str(total),
                "wr",winrate*100,"%",
                "profitfactor",str(profitfactor))
        if(total > maxProfit + 1): # and winrate>0.067
            print("total",total,"maxProfit",maxProfit)
            maxProfit = total
            maxTpVal = tpVal
        print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
        riskOfRuin = calcRisk(tpVal,winrate,100)
        print("riskOfRuin",riskOfRuin)

        # singleTrade = sorted(singleTrade, key=lambda x:x['profit'], reverse=True)
        # df = pd.DataFrame(trades)
        # df.to_csv('./csv/result/trades_status.csv')

        # singleTradeDf = pd.DataFrame(singleTrade)
        # singleTradeDf.to_csv('./csv/result/single_trade.csv')
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