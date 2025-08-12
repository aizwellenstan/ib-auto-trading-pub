# from ib_insync import *
import pandas as pd
from typing import NamedTuple
from datetime import datetime as dt, timedelta
import json
import pickle
import numpy as np
import gc
import sys
mainFolder = '../'
sys.path.append(mainFolder)
from prophet import Prophet
from modules.predict import RbfPredict, SvrLinearPredict, LinearPredict, DecitionTreePredict
from modules.movingAverage import Sma
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetProfit, GetProfitJP, GetFloat,GetPE,GetADR,GetIndustry,GetSector,GetVol,GetMarketCap, GetEPS
from modules.technicalAnalysis import PlotLines
from modules.trend import GetTrend
import requests
from scipy.signal import lfilter
from modules.riskOfRuin import calcRisk
from collections import defaultdict
from modules.trend import GetTrend
from modules.shareholders import GetInsiderPercent, GetFloatPercentHeld
# from modules.predict import LinearPredict, DecitionTreePredict
# import talib

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

    tradeCsvPath = 'trades_8M.csv'
    if currency == 'JPY':
        tradeCsvPath = 'trades_8M_JP.csv'

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
            output = open("./pickle/pro/compressed/QQQ8MD1arr.p", "rb")
            gc.disable()
            QQQD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load QQQD1arr finished")
        
            output = open("./pickle/pro/compressed/SPY8MD1arr.p", "rb")
            gc.disable()
            SPYD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load SPYD1arr finished")
        
            output = open("./pickle/pro/compressed/VTI8MD1arr.p", "rb")
            gc.disable()
            VTID1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load VTID1arr finished")
       
            output = open("./pickle/pro/compressed/DIA8MD1arr.p", "rb")
            gc.disable()
            DIAD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load DIAD1arr finished")

            output = open("./pickle/pro/compressed/IWM8MD1arr.p", "rb")
            gc.disable()
            IWMD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IWMD1arr finished")

            output = open("./pickle/pro/compressed/TLT8MD1arr.p", "rb")
            gc.disable()
            TLTD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load TLTD1arr finished")

            output = open("./pickle/pro/compressed/XLU8MD1arr.p", "rb")
            gc.disable()
            XLUD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLUD1arr finished")

            output = open("./pickle/pro/compressed/XLI8MD1arr.p", "rb")
            gc.disable()
            XLID1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load XLID1arr finished")

        hisBarsD1Dict = {}
        hisBarsH2Dict = {}
        profitSymList = []

        if currency == 'USD':
            output = open("./pickle/pro/compressed/hisBarsStocks8MD1Dict.p", "rb")
            gc.disable()
            hisBarsD1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsD1Dict finished")

            output = open("./pickle/pro/compressed/hisBarsStocks8MH2Dict.p", "rb")
            gc.disable()
            hisBarsH2Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsH2Dict finished")

            profitSymList = GetProfit()
        else:
            output = open("./pickle/pro/compressed/jp/hisBarsStocks8MD1Dict.p", "rb")
            gc.disable()
            hisBarsD1Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsD1Dict finished")

            hisBarsH2Dict = {}
            output = open("./pickle/pro/compressed/jp/hisBarsStocks8MH2Dict.p", "rb")
            gc.disable()
            hisBarsH2Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsH2Dict finished")

            profitSymList = GetProfitJP()
        
        adrDict = GetADR(currency)
        floatDict = GetFloat(currency)
        industryDict = GetIndustry(currency)
        volDict = GetVol(currency)
        marketcapDict = GetMarketCap()
        epsDict = GetEPS(currency)
        # debtEquityDict = GetDebtEquity(currency)
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

        # industryCsvPath = 'industry.csv'
        # df = pd.read_csv (r'./csv/%s'%(industryCsvPath), index_col=0)
        # df.drop
        # symbols = json.loads(df.to_json(orient = 'records'))

        if currency == "USD":
            symbolArr = ["QQQ","SQQQ","SPY","SPXU"]

            for trade in trades:
                symbol = str(trade['symbol'])
                if symbol not in profitSymList: continue
                if symbol not in symbolArr:
                    symbolArr.append(symbol)

            vwapDfDict = {}
            csvPath = "8M"
            for symbol in symbolArr:
                df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(csvPath,symbol))
                vwapDfDict[symbol] = df

        # insiderPercentDict = {}
        # # institutionsDict = {}
        # for trade in trades:
        #     symbol = str(trade['symbol'])
        #     if symbol in insiderPercentDict: continue
        #     # if symbol in institutionsDict: continue
        #     insiderPercent = GetInsiderPercent(symbol)
        #     # institutions = GetFloatPercentHeld(symbol)
        #     insiderPercentDict[symbol] = insiderPercent
        #     # institutionsDict[symbol] = institutions

        fee = 1.001392062 * 2
        tpVal = 1.15137614678 #3.69 #2 #5 #2 #3.19148936 #2 #15.42857143 #5.7#5.7#35.2#23.5 #25.8
        maxProfit = 0
        maxTpVal = 6.766666667
        maxSlVal = 0
        maxMarCapLimit = 0
        maxVolavgLimit = 0
        maxAdjVal = 0
        minRiskOfRuin = 1

        hisBarsD1arr = []

        adjVal = 1
        while adjVal >= 0.01:
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
                sectorAvgBoard = {}
                symbol = str(trade['symbol'])
                if symbol not in profitSymList: continue

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
                    
                vol = int((1000)/(op-sl))
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

                # if (
                #     hisBarsD1[4].high-hisBarsD1[4].low < 0.01 or
                #     hisBarsD1[3].high-hisBarsD1[3].low < 0.01 or
                #     hisBarsD1[2].high-hisBarsD1[2].low < 0.01 or
                #     hisBarsD1[1].high-hisBarsD1[1].low < 0.01
                # ): continue

                # if len(hisBarsD1) > 41:
                #     if (
                #         abs(hisBarsD1[1].close - hisBarsD1[20].open) < 0.01 or
                #         abs(hisBarsD1[21].close - hisBarsD1[40].open) < 0.01
                #     ): continue
                
                # # if hisBarsD1[0].open < hisBarsD1[1].close * 1.007: 
                # #     continue
                if hisBarsD1[0].open < hisBarsD1[1].close * 1.02: 
                    continue
                if symbol in shortableSymList:
                    vwapDf = vwapDfDict[symbol]
                    mask = vwapDf.Date < str(backtestTime.date())
                    vwapDf = vwapDf.loc[mask]

                    vwapDf = vwapDfDict[symbol]
                    mask = vwapDf.Date < str(backtestTime.date())
                    vwapDf = vwapDf.loc[mask]

                    dfTrain = vwapDf[['Date', 'Close']]
                    dfTrain = dfTrain.rename(columns={"Date": "ds", "Close": "y"})
                    m = Prophet()
                    m.fit(dfTrain)
                    future = m.make_future_dataframe(periods=1)
                    forcast = m.predict(future)
                    forcast = forcast.iloc[-1].trend
                    if forcast < vwapDf.iloc[-1].Close * adjVal: continue

                        # df = df.assign(O2=df.Open.shift(1))
                        # df = df.assign(C2=df.Close.shift(1))
                        # df = df.assign(ocRange=abs(df.Close-df.Open)/abs(df.C2-df.O2+0.01))
                        # avgOCRange = df.loc[bearCandle, 'ocRange'].mean()

                        # ocRange = (
                        #     abs(vwapDf.iloc[-1].Close-vwapDf.iloc[-1].Open) /
                        #     abs(vwapDf.iloc[-2].Close-vwapDf.iloc[-2].Open+0.01)
                        # )

                        # if ocRange > avgOCRange * adjVal: continue

                        # df = df.assign(H3=df.High.shift(2))
                        # df = df.assign(L3=df.Low.shift(2))
                        # df = df.assign(minH=min(df.H2,df.H3))
                        # df = df.assign(maxL=max(df.L2,df.L3))
                        # df = df.assign(hlRange=(df.High-df.Low)/(df.minH-df.maxL)+0.01)
                        # avgHLRange = df.loc[bearCandle, 'hlRange'].mean()

                        # minH = min(vwapDf.iloc[-2].High,vwapDf.iloc[-3].High)
                        # maxL = max(vwapDf.iloc[-2].Low,vwapDf.iloc[-3].Low)
                        # hlRange = (
                        #     (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low) /
                        #     (minH - maxL + 0.01)
                        # )
                        # if hlRange > avgHLRange * adjVal: continue

                    # df = vwapDf
                    # columnName = 'Volume'
                    # df = df[[columnName]]
                    # predict = DecitionTreePredict(df, columnName)

                    # qqqVolChange = predict / vwapDf.iloc[-1].Volume

                    # vwapDf = vwapDfDict["SQQQ"]
                    # vwapDf = vwapDf.loc[mask]
                    # df = vwapDf
                    # columnName = 'Volume'
                    # df = df[[columnName]]
                    # predict = DecitionTreePredict(df, columnName)

                    # sqqqVolChange = predict / vwapDf.iloc[-1].Volume

                    # if qqqVolChange < sqqqVolChange * adjVal:
                    #     continue

                #     insiderPercent = insiderPercentDict[symbol]
                #     if insiderPercent > adjVal: continue
                    # institutions = institutionsDict[symbol]
                    # if institutions > adjVal: continue
                    # vwapDf = vwapDfDict[symbol]
                    # mask = vwapDf.Date < str(backtestTime.date())
                    # vwapDf = vwapDf.loc[mask]



                    # columnName = 'Vwap'
                    # df = df[[columnName]]
                    # predict = DecitionTreePredict(df, columnName)

                    # if predict < vwapDf.iloc[-1].Vwap * adjVal: continue

                    # df = vwapDf
                    # df = df.assign(nextOpen=df.Open.shift(-1))
                    # df = df.assign(nextClose=df.Close.shift(-1))
                    # bearCandle = df['nextClose'] < df['nextOpen']

                    # df = df.assign(HLV=(df.High+df.Low+df.Vwap)/3)
                    # avgHLV = df.loc[bearCandle, 'HLV'].mean()

                    # hlv = (
                    #     df.iloc[-1].High 
                    #     + df.iloc[-1].Low
                    #     + df.iloc[-1].Vwap
                    # ) / 3
                    # bias = (hlv-avgHLV) / avgHLV
                    # if  bias < adjVal: continue

                    # if (
                    #     vwapDf.iloc[-1].Volume > 
                    #     vwapDf.iloc[-2].Volume and
                    #     (
                    #         vwapDf.iloc[-1].High -
                    #         vwapDf.iloc[-1].Low
                    #     ) >
                    #     (
                    #         vwapDf.iloc[-2].High -
                    #         vwapDf.iloc[-2].Low
                    #     ) * adjVal
                    # ): continue
                    

                #     # df = vwapDf
                #     # df = df.assign(nextOpen=df.Open.shift(-1))
                #     # df = df.assign(nextClose=df.Close.shift(-1))
                #     # bearCandle = df['nextClose'] < df['nextOpen']

                #     # df = df.assign(h1c1=df.High/df.Close)
                #     # avgH1C1 = df.loc[bearCandle, 'h1c1'].mean()

                #     # h1c1 = df.iloc[-1].High / df.iloc[-1].Close
                #     # if (
                #     #     h1c1 < avgH1C1 * adjVal
                #     # ): continue

                #     df = vwapDf
                #     df = df.assign(nextOpen=df.Open.shift(-1))
                #     df = df.assign(nextClose=df.Close.shift(-1))
                #     bearCandle = df['nextClose'] < df['nextOpen']

                #     df = df.assign(V2=df.Volume.shift(1))

                #     df = df.assign(v1v2=df.Volume/df.V2)
                #     avgV1V2 = df.loc[bearCandle, 'v1v2'].mean()

                #     v1v2 = df.iloc[-1].Volume / df.iloc[-2].Volume
                #     if (
                #         v1v2 < avgV1V2 * adjVal
                #     ): continue

                    # if vwapDf.iloc[-1].Vwap < vwapDf.iloc[-4].Vwap * adjVal:
                    #     continue
                    # vwapDf = vwapDfDict["SPY"]
                    # mask = vwapDf.Date < str(backtestTime.date())
                    # vwapDf = vwapDf.loc[mask]
                    # # qqqVolChange = vwapDf.iloc[-1].Volume/vwapDf.iloc[-2].Volume
                    # qqqChange = vwapDf.iloc[-1].Close/vwapDf.iloc[-1].Open

                    # vwapDf = vwapDfDict["SQQQ"]
                    # vwapDf = vwapDf.loc[mask]
                    # # sqqqVolChange = vwapDf.iloc[-1].Volume/vwapDf.iloc[-2].Volume
                    # sqqqChange = vwapDf.iloc[-1].Close/vwapDf.iloc[-1].Open

                    # if (qqqChange + sqqqChange) / 2 < adjVal: continue

                    # if qqqVolChange < sqqqVolChange * adjVal:
                    #     continue

                # if currency == 'USD':
                #     if symbol in shortableSymList:

                # # #         # if symbol in shortableSymList:
                # # #         #     if symbol not in debtEquityDict:continue
                # # #         #     debtEquity = debtEquityDict[symbol]
                # # #         #     if debtEquity > adjVal: continue #3.48 - 4.2

                # # #         # if symbol not in sp500symbols: continue

                        

                    # # machineLearn
                    # days = list()
                    # vwapPrices = list()
                    # dfVwap = vwapDf.loc[:, 'Close']
                    # for i in range(len(dfVwap)):
                    #     days.append([i])
                    # for vwap in dfVwap:
                    #     vwapPrices.append(vwap)
                    # rbfSvr = SVR(kernel='rbf', C=1000.0, gamma=0.85)
                    # rbfSvr.fit(days, vwapPrices)
                    # predictNum = [[len(dfVwap)+1]]
                    # predictClose = rbfSvr.predict(predictNum)

                    # days = list()
                    # vwapPrices = list()
                    # dfVwap = vwapDf.loc[:, 'High']
                    # for i in range(len(dfVwap)):
                    #     days.append([i])
                    # for vwap in dfVwap:
                    #     vwapPrices.append(vwap)
                    # rbfSvr = SVR(kernel='rbf', C=1000.0, gamma=0.85)
                    # rbfSvr.fit(days, vwapPrices)
                    # predictNum = [[len(dfVwap)+1]]
                    # predictHigh = rbfSvr.predict(predictNum)

                    # days = list()
                    # vwapPrices = list()
                    # dfVwap = vwapDf.loc[:, 'Low']
                    # for i in range(len(dfVwap)):
                    #     days.append([i])
                    # for vwap in dfVwap:
                    #     vwapPrices.append(vwap)
                    # rbfSvr = SVR(kernel='rbf', C=1000.0, gamma=0.85)
                    # rbfSvr.fit(days, vwapPrices)
                    # predictNum = [[len(dfVwap)+1]]
                    # predictLow = rbfSvr.predict(predictNum)

                    # if predictClose > predictHigh:
                    #     predictClose = predictHigh
                    # if predictClose < predictLow:
                    #     predictClose = predictLow

                    # if predictClose < vwapDf.iloc[-1].Close * adjVal:
                    #     continue
                    

                        # vwap = vwapDf.iloc[-1].Vwap

                        # bias = (predictPrice-vwap)/vwap
                        # if bias < adjVal: continue

                        # volume = (
                        #     vwapDf.iloc[-4].Volume +
                        #     vwapDf.iloc[-3].Volume +
                        #     vwapDf.iloc[-2].Volume +
                        #     vwapDf.iloc[-1].Volume
                        # ) / 4
                        # marketcap = marketcapDict[symbol]

                        # if volume/marketcap < adjVal: continue

                        # typicalPrice = (
                        #     vwapDf['Close']+vwapDf['High']
                        #     +vwapDf['Low']
                        # ) / 3

                        # moneyFlow = typicalPrice * vwapDf['Volume']

                        # negativeFlow = []
                        # positiveFlow = []

                        # period = 22
                        # for i in range(1, period+1):
                        #     if typicalPrice[i] > typicalPrice[i-1]:
                        #         positiveFlow.append(moneyFlow[i-1])
                        #         negativeFlow.append(0)
                        #     elif typicalPrice[i] < typicalPrice[i-1]:
                        #         positiveFlow.append(0)
                        #         negativeFlow.append(moneyFlow[i-1])
                        #     else:
                        #         positiveFlow.append(0)
                        #         negativeFlow.append(0)

                        # positiveMf = []
                        # negativeMf = []

                    
                        # for i in range(period-1, len(positiveFlow)):
                        #     positiveMf.append(sum(positiveFlow[i+1-period:i+1]))
                        # for i in range(period-1, len(negativeFlow)):
                        #     negativeMf.append(sum(negativeFlow[i+1-period:i+1]))

                        # mfi = 100*(np.array(positiveMf))/(np.array(positiveMf)+np.array(negativeMf))
                        # if mfi[-1] > adjVal: continue

                        # obv = []
                        # obv.append(0)
                        # for i in range(1, len(vwapDf.Close)):
                        #     if vwapDf.Close[i] > vwapDf.Close[i-1]:
                        #         obv.append(obv[-1] + vwapDf.Volume[i])
                        #     elif vwapDf.Close[i] < vwapDf.Close[i-1]:
                        #         obv.append(obv[-1] - vwapDf.Volume[i])
                        #     else: obv.append(obv[-1])

                        # obv = obv[::-1]
                        # SmaObvD1 = Sma(obv[0:3], 2)
                        # bias = (obv[-1]-SmaObvD1)/SmaObvD1
                        # if bias < adjVal: continue 

                        # volList = []
                        # volPeriod = 27
                        # for i in range(1,volPeriod+1):
                        #     volList.append(vwapDf.iloc[-i].Volume)
                        # SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

                        # bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
                        # if bias < adjVal: continue

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
                #     # hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
                #     # hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
                #     # hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
                #     # hisBarsXLFD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLFD1arr))
                #     # hisBarsEEMD1 = list(filter(lambda x:x.date <= backtestTime.date(),EEMD1arr))
                #     # hisBarsEWZD1 = list(filter(lambda x:x.date <= backtestTime.date(),EWZD1arr))
                #     # hisBarsEFAD1 = list(filter(lambda x:x.date <= backtestTime.date(),EFAD1arr))
                #     # hisBarsTLTD1 = list(filter(lambda x:x.date <= backtestTime.date(),TLTD1arr))
                #     # hisBarsXLUD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLUD1arr))
                #     # hisBarsSOXLD1 = list(filter(lambda x:x.date <= backtestTime.date(),SOXLD1arr))
                #     # hisBarsXLID1 = list(filter(lambda x:x.date <= backtestTime.date(),XLID1arr))
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
                #     # hisBarsVEAD1 = list(filter(lambda x:x.date <= backtestTime.date(),VEAD1arr))
                #     # hisBarsIYRD1 = list(filter(lambda x:x.date <= backtestTime.date(),IYRD1arr))
                #     hisBarsXLBD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLBD1arr))

                    # hisBarsQQQD1 = hisBarsQQQD1[::-1]
                    # hisBarsSPYD1 = hisBarsSPYD1[::-1]
                #     # hisBarsVTID1 = hisBarsVTID1[::-1]
                #     # hisBarsDIAD1 = hisBarsDIAD1[::-1]
                #     # hisBarsIWMD1 = hisBarsIWMD1[::-1]
                #     # hisBarsEEMD1 = hisBarsEEMD1[::-1]
                #     # hisBarsEWZD1 = hisBarsEWZD1[::-1]
                #     # hisBarsEFAD1 = hisBarsEFAD1[::-1]
                #     # hisBarsTLTD1 = hisBarsTLTD1[::-1]
                #     # hisBarsXLUD1 = hisBarsXLUD1[::-1]
                #     # hisBarsSOXLD1 = hisBarsSOXLD1[::-1]
                #     # hisBarsXLID1 = hisBarsXLID1[::-1]
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
                #     # hisBarsVEAD1 = hisBarsVEAD1[::-1]
                #     # hisBarsIYRD1 = hisBarsIYRD1[::-1]
                #     hisBarsXLBD1 = hisBarsXLBD1[::-1]

                #     if symbol in shortableSymList:
                #         upper, lower = PlotLines(hisBarsXLBD1)
                #         if upper < adjVal: continue
                #     # if symbol in shortableSymList:
                #     #     qqqGap = hisBarsQQQD1[0].open / hisBarsQQQD1[1].close
                #     #     spyGap = hisBarsSPYD1[0].open / hisBarsSPYD1[1].close
                #     #     curGap = hisBarsD1[0].open / hisBarsD1[1].close

                #     #     if (
                #     #         curGap < qqqGap and
                #     #         curGap < spyGap
                #     #     ): continue

                #     gapRange = hisBarsD1[0].open/hisBarsD1[1].high
                #     qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].high
                #     iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].high
                    
                #     # if (
                #     #     gapRange < qqqGapRange * 0.981 or
                #     #     gapRange < iwmGapRange * 0.981
                #     # ): continue
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
                #         hisBarsQQQD1[1].close > hisBarsQQQD1[1].open and
                #         hisBarsSPYD1[1].close > hisBarsSPYD1[1].open and
                #         hisBarsVTID1[1].close > hisBarsVTID1[1].open and
                #         hisBarsDIAD1[1].close > hisBarsDIAD1[1].open and
                #         hisBarsIWMD1[1].close > hisBarsIWMD1[1].open and
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

                # if symbol in shortableSymList:
                #     vwapDf = vwapDfDict[symbol]
                #     mask = vwapDf.Date < str(backtestTime.date())
                #     vwapDf = vwapDf.loc[mask]
                #     vwap = vwapDf.iloc[-1].Vwap
                #     maxHigh = hisBarsD1[1].high
                #     for i in range(2,3):
                #         if hisBarsD1[i].high > maxHigh:
                #             maxHigh = hisBarsD1[i].high

                #     minLow = hisBarsD1[1].low
                #     for i in range(2,3):
                #         if hisBarsD1[i].low < minLow:
                #             minLow = hisBarsD1[i].low

                #     if vwap-minLow > 0:
                #         if not (
                #             (maxHigh-vwap) /
                #             (vwap-minLow) > 0.03
                #         ): continue

                # if symbol in shortableSymList:
                #     if len(hisBarsD1) > 26:
                #         if hisBarsD1[1].close / hisBarsD1[25].close < adjVal:
                #             continue

                #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:23], 22)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     if bias < adjVal: continue

                # if symbol in shortableSymList:
                #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:4], 3)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     if bias < -0.17: continue

                #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:5], 4)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     if bias < -0.07: continue
                    
                #     # SmaD1 = Sma(hisBarsD1avgPriceArr[1:15], 14)
                #     # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     # if bias < -0.2: continue

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

                # # Industry
                # if symbol in shortableSymList:
                #     industryCheck = False
                #     industryCheckPeriod = 4

                #     vwapDf = vwapDfDict[symbol]
                #     mask = vwapDf.Date < str(backtestTime.date())
                #     vwapDf = vwapDf.loc[mask]
                #     v1v2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume
                #     curIndustryGain = v1v2

                #     industryLeader = curIndustryGain
                #     if symbol not in industryDict: continue
                #     industry = industryDict[symbol]
                #     groupList = industryListGroup[industry]
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

                #                 if sym2 not in profitSymList: continue
                #                 if sym2 not in vwapDfDict: continue
                #                 vwapDf = vwapDfDict[sym2]
                #                 mask = vwapDf.Date < str(backtestTime.date())
                #                 vwapDf = vwapDf.loc[mask]
                #                 if len(vwapDf) < 2: continue 
                #                 if vwapDf.iloc[-2].Volume < 1: continue 
                #                 v1v2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume

                #                 industryGain = v1v2
                #                 if industryGain > industryLeader:
                #                     industryLeader = industryGain
                #             industryLeaderBoard[industry] = industryLeader
                #     else:
                #         industryCheck = True
                            
                #     # qqqGain = hisBarsQQQD1[1].close / hisBarsQQQD1[industryCheckPeriod].open
                #     # spyGain = hisBarsSPYD1[1].close / hisBarsSPYD1[industryCheckPeriod].open
                #     # vtiGain = hisBarsVTID1[1].close / hisBarsVTID1[industryCheckPeriod].open
                #     # diaGain = hisBarsDIAD1[1].close / hisBarsDIAD1[industryCheckPeriod].open
                #     # iwmGain = hisBarsIWMD1[1].close / hisBarsIWMD1[industryCheckPeriod].open

                #     # if (
                #     #     # industryLeader > qqqGain * 0.95
                #     #     industryLeader > spyGain * 0.96 
                #     #     # industryLeader > diaGain * 0.94
                #     #     # industryLeader > iwmGain * 0.94
                #     #     # industryLeader > vtiGain * 0.96
                #     # ):
                #     if (
                #         curIndustryGain > industryLeader * adjVal
                #     ):  
                #         industryCheck = True
                #     if not industryCheck: continue

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

                # gap = hisBarsD1[0].open/hisBarsD1[1].close
                # tp = hisBarsD1[1].high + adrRange * adjVal
                # maxTp = hisBarsD1[1].close * 12
                # tp = min(tp,maxTp)
                # tp = NormalizeFloat(tp, basicPoint)

                eod = True
                
                dataH2 = hisBarsH2Dict[symbol]
                if(len(dataH2) < 6):
                    continue

                testhisBarsH1 = list(filter(lambda x:x.date >= backtestTime,dataH2))
                trade['status'] = ''
                
                cancelTime = backtestTime+timedelta(minutes=15)
                for i in testhisBarsH1:
                    if i.high >= op:
                        if i.date >= cancelTime: continue
                        trade['status'] = i.date
                        break

                trade['result'] = ''
                if trade['status'] != '':
                    triggeredTime = trade['status']
                    endTime = backtestTime+timedelta(minutes=256)
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
            # print("total",str(total),
            #         "wr",winrate*100,"%",
            #         "profitfactor",str(profitfactor))
            if(total > maxProfit + 1): # and winrate>0.067
                print("total",total,"maxProfit",maxProfit)
                maxProfit = total
                maxTpVal = tpVal
                maxAdjVal = '{0:.10f}'.format(adjVal)
            print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
            # riskOfRuin = calcRisk(tpVal,winrate,100)
            # if riskOfRuin < minRiskOfRuin:
            #     minRiskOfRuin = riskOfRuin
            # print("riskOfRuin",riskOfRuin)
            print("maxAdjVal",maxAdjVal)
            adjVal -= 0.01

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