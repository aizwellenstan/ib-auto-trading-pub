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
from modules.predict import RbfPredict, SvrLinearPredict, LinearPredict, DecitionTreePredict
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
from modules.shareholders import GetInsiderPercent, GetFloatPercentHeld
from modules.sharpe import GetSharpe, GetStd, GetMaxDD
from modules.slope import GetSlopeUpper, GetSlopeLower, GetSlopeUpperNew, GetSlopeLowerNew
from modules.volatility import GetOverBoughtSold
from modules.turtle import GetTurtle, GetTurtleOrigin
# from gluonts.dataset.common import ListDataset
# from gluonts.model.deepar import DeepAREstimator
# from gluonts.mx.trainer import Trainer
# from sklearn.model_selection import train_test_split
# from gluonts.evaluation.backtest import make_evaluation_predictions

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]


shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

# df=pd.DataFrame(shortableSymList)
# df.to_csv('./csv/shortableSymList.csv')

# print(shortableSymList)

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

            output = open("./pickle/pro/compressed/UVXY8MD1arr.p", "rb")
            gc.disable()
            UVXYD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load UVXYD1arr finished")

            output = open("./pickle/pro/compressed/IWM8MD1arr.p", "rb")
            gc.disable()
            IWMD1arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load IWMD1arr finished")

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
            output = open("./pickle/pro/compressed/jp/hisBarsStocks8MH1Dict.p", "rb")
            gc.disable()
            hisBarsH2Dict = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsH2Dict finished")

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

        industryCsvPath = 'industry.csv'
        df = pd.read_csv (r'./csv/%s'%(industryCsvPath), index_col=0)
        df.drop
        symbols = json.loads(df.to_json(orient = 'records'))

        if currency == "USD":
            symbolArr = ["QQQ","SQQQ","SPY","IAU","IWM",
            "^N225",
            "VTI","DIA"]

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

        insiderPercentDict = {}
        for trade in trades:
            symbol = str(trade['symbol'])
            if symbol in insiderPercentDict: continue
            insiderPercent = GetInsiderPercent(symbol)
            insiderPercentDict[symbol] = insiderPercent

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
            sectorLeaderBoard = {}
            sectorAvgBoard = {}
            symbol = str(trade['symbol'])
            if symbol not in profitSymList: continue
            # if symbol in shortableSymList:
            #     insiderPercent = insiderPercentDict[symbol]
            #     if insiderPercent > 0.0982: continue
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

            # dataD1 = hisBarsD1Dict[symbol]
            # if(len(dataD1) < 16):continue
            # hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            # if len(hisBarsD1) < 16: continue
            # hisBarsD1 = hisBarsD1[::-1]

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
            
            symDf = vwapDfDict[symbol]
            mask = symDf.Date <= str(backtestTime.date())
            symDf = symDf.loc[mask]

            if symDf.iloc[-1].Open < symDf.iloc[-2].Close * 1.02: 
                continue

            # if hisBarsD1[0].open < hisBarsD1[1].close * 1.02: 
            #     continue

            # mask = symDf.Date < str(backtestTime.date())
            # symDf = symDf.loc[mask]

            # if (
            #     symbol in shortableSymList or
            #     currency != "USD"
            # ):

            #     df = symDf
            #     df = df[['Open','High','Low','Close']]
            #     npArr = df.to_numpy()
            #     lower = GetSlopeLower(npArr)
            #     upper = GetSlopeUpper(npArr)
            ##     if lower < -0.1: continue
            #     if upper < 0: continue

            #     volVal = 0.05
            #     if (
            #         (
            #             df.iloc[-1].Volume +
            #             df.iloc[-2].Volume
            #         ) >
            #         (
            #             df.iloc[-3].Volume +
            #             df.iloc[-4].Volume
            #         ) * (1-volVal) and
            #         (
            #             df.iloc[-1].Volume +
            #             df.iloc[-2].Volume
            #         ) >
            #         (
            #             df.iloc[-5].Volume +
            #             df.iloc[-6].Volume
            #         ) * (1-volVal) and
            #         (
            #             df.iloc[-1].Volume +
            #             df.iloc[-2].Volume
            #         ) <
            #         (
            #             df.iloc[-3].Volume +
            #             df.iloc[-4].Volume
            #         ) * (1+volVal) and
            #         (
            #             df.iloc[-1].Volume +
            #             df.iloc[-2].Volume
            #         ) <
            #         (
            #             df.iloc[-5].Volume +
            #             df.iloc[-6].Volume
            #         ) * (1+volVal)
            #     ): continue

            #     df = symDf[['Close']]
            #     df = df.tail(4)
            #     maxDD = GetMaxDD(df)
            #     if maxDD < -0.26: continue

            #     df = symDf[['Close']]
            #     df = df.tail(6)
            #     maxDD = GetMaxDD(df)
            #     if maxDD < -0.14: continue

            #     df = symDf[['Close']]
            #     df = df.tail(7)
            #     maxDD = GetMaxDD(df)
            #     if maxDD < -0.14: continue
            # if currency == 'USD':
            #     hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),QQQD1arr))
            #     hisBarsSPYD1 = list(filter(lambda x:x.date <= backtestTime.date(),SPYD1arr))
            #     hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
            #     hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
            #     hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))

            #     hisBarsQQQD1 = hisBarsQQQD1[::-1]
            #     hisBarsSPYD1 = hisBarsSPYD1[::-1]
            #     hisBarsVTID1 = hisBarsVTID1[::-1]
            #     hisBarsDIAD1 = hisBarsDIAD1[::-1]
            #     hisBarsIWMD1 = hisBarsIWMD1[::-1]

            #     if symbol in shortableSymList:
            #         upper, lower = PlotLines(hisBarsDIAD1)
            #         if lower < -0.61: continue

            #         iwmDf = vwapDfDict["IWM"]
            #         mask = iwmDf.Date < str(backtestTime.date())
            #         iwmDf = iwmDf.loc[mask]

            #         # df = vwapDf
            #         # df = df[['Open','High','Low','Close']]
            #         # npArr = df.to_numpy()
            #         # lower = GetSlopeLower(npArr)
            #         # upper = GetSlopeUpper(npArr)

            #         # if lower < -0.34: continue
            #         # if upper < 0: continue

            #         df = iwmDf
            #         df = df[['Open','High','Low','Close']]
            #         df = df.tail(49)
            #         npArr = df.to_numpy()
            #         lower = GetSlopeUpperNew(npArr)
            #         if upper < 0: continue

            #         iauDf = vwapDfDict["IAU"]
            #         mask = iauDf.Date < str(backtestTime.date())
            #         iauDf = iauDf.loc[mask]

            #         df = iauDf
            #         df = df[['Open','High','Low','Close']]
            #         npArr = df.to_numpy()
            #         upper = GetSlopeUpper(npArr)
            #         if upper > 0.12: continue

            #         # n225Df = vwapDfDict["^N225"]
            #         # mask =  n225Df.Date < str(backtestTime.date())
            #         # n225Df =  n225Df.loc[mask]

            #         # df =  n225Df
            #         # df = df[['Open','High','Low','Close']]
            #         # npArr = df.to_numpy()
            #         # lower = GetSlopeLower(npArr)
            #         # if lower < 0: continue


            #     df = vwapDfDict[symbol]
            #     mask = df.Date <= str(backtestTime.date())
            #     df = df.loc[mask]

            #     qqqDf = vwapDfDict["QQQ"]
            #     mask = qqqDf.Date <= str(backtestTime.date())
            #     qqqDf = qqqDf.loc[mask]

            #     spyDf = vwapDfDict["SPY"]
            #     mask = spyDf.Date <= str(backtestTime.date())
            #     spyDf = spyDf.loc[mask]

            #     iwmDf = vwapDfDict["IWM"]
            #     mask = iwmDf.Date <= str(backtestTime.date())
            #     iwmDf = iwmDf.loc[mask]

            #     diaDf = vwapDfDict["DIA"]
            #     mask = diaDf.Date <= str(backtestTime.date())
            #     diaDf = diaDf.loc[mask]

            #     vtiDf = vwapDfDict["VTI"]
            #     mask = vtiDf.Date <= str(backtestTime.date())
            #     vtiDf = vtiDf.loc[mask]

            #     if (
            #         hisBarsQQQD1[1].close > hisBarsQQQD1[1].open * 1.0003 and
            #         hisBarsSPYD1[1].close > hisBarsSPYD1[1].open * 1.0003 and
            #         hisBarsVTID1[1].close > hisBarsVTID1[1].open * 1.0003 and
            #         hisBarsDIAD1[1].close > hisBarsDIAD1[1].open * 1.0003 and
            #         hisBarsIWMD1[1].close > hisBarsIWMD1[1].open * 1.0003 and
            #         hisBarsD1[1].close < hisBarsD1[1].open * 0.98
            #     ): continue

            # # if sl < hisBarsD1[1].close: sl = hisBarsD1[1].close

            # if symbol in shortableSymList:
            #     if hisBarsD1[1].close / hisBarsD1[3].close > 1.08: continue

            # if symbol in shortableSymList:
            #         industryCheck = False
            #         industryCheckPeriod = 4

            #         vwapDf = vwapDfDict[symbol]
            #         mask = vwapDf.Date < str(backtestTime.date())
            #         vwapDf = vwapDf.loc[mask]
            #         df = vwapDf[['Vwap']]
            #         sharpe = GetSharpe(df)
            #         curIndustryGain = sharpe

            #         industryLeader = curIndustryGain
            #         if symbol not in industryDict: continue
            #         industry = industryDict[symbol]
            #         groupList = industryListGroup[industry]
            #         if len(groupList) > 1:
            #             if industry in industryLeaderBoard:
            #                 industryLeader = industryLeaderBoard[industry]
            #             else:
            #                 for sym2 in groupList:
            #                     if sym2 not in hisBarsD1Dict: continue
            #                     sym2Vol = volDict[sym2]
            #                     if sym2Vol < 210187: continue

            #                     if sym2 not in profitSymList: continue
            #                     if sym2 not in vwapDfDict: continue
            #                     vwapDf = vwapDfDict[sym2]
            #                     mask = vwapDf.Date < str(backtestTime.date())
            #                     vwapDf = vwapDf.loc[mask]
            #                     if len(vwapDf) < 2: continue 
            #                     if vwapDf.iloc[-2].Volume < 1: continue 
            #                     df = vwapDf[['Vwap']]
            #                     sharpe = GetSharpe(df)

            #                     industryGain = sharpe
            #                     if industryGain > industryLeader:
            #                         industryLeader = industryGain
            #                 industryLeaderBoard[industry] = industryLeader
            #         else:
            #             industryCheck = True

            #         if (
            #             curIndustryGain > industryLeader * 0.54
            #         ):  
            #             industryCheck = True
            #         if not industryCheck: continue

            # # Industry
            # if symbol in shortableSymList:
            #     industryCheck = False
            #     industryCheckPeriod = 4

            #     vwapDf = vwapDfDict[symbol]
            #     mask = vwapDf.Date < str(backtestTime.date())
            #     vwapDf = vwapDf.loc[mask]
            #     v1v2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume
            #     curIndustryGain = v1v2

            #     # industryLeader = curIndustryGain
            #     # if symbol not in industryDict: continue
            #     # industry = industryDict[symbol]
            #     # groupList = industryListGroup[industry]
            #     # if len(groupList) > 1:
            #     #     if industry in industryLeaderBoard:
            #     #         industryLeader = industryLeaderBoard[industry]
            #     #     else:
            #     #         for sym2 in groupList:
            #     #             if sym2 not in hisBarsD1Dict: continue
            #     #             sym2Vol = volDict[sym2]
            #     #             if sym2Vol < 210187: continue

            #     #             sym2dataD1 = hisBarsD1Dict[sym2]
                            
            #     #             sym2hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),sym2dataD1))
            #     #             if len(sym2hisBarsD1) < 5:continue
            #     #             sym2hisBarsD1 = sym2hisBarsD1[::-1]

            #     #             if sym2 not in profitSymList: continue
            #     #             if sym2 not in vwapDfDict: continue
            #     #             vwapDf = vwapDfDict[sym2]
            #     #             mask = vwapDf.Date < str(backtestTime.date())
            #     #             vwapDf = vwapDf.loc[mask]
            #     #             if len(vwapDf) < 2: continue 
            #     #             if vwapDf.iloc[-2].Volume < 1: continue 
            #     #             v1v2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume

            #     #             industryGain = v1v2
            #     #             if industryGain > industryLeader:
            #     #                 industryLeader = industryGain
            #     #         industryLeaderBoard[industry] = industryLeader
            #     # else:
            #     #     industryCheck = True
                        
            #     # # qqqGain = hisBarsQQQD1[1].close / hisBarsQQQD1[industryCheckPeriod].open
            #     # # spyGain = hisBarsSPYD1[1].close / hisBarsSPYD1[industryCheckPeriod].open
            #     # # vtiGain = hisBarsVTID1[1].close / hisBarsVTID1[industryCheckPeriod].open
            #     # # diaGain = hisBarsDIAD1[1].close / hisBarsDIAD1[industryCheckPeriod].open
            #     # # iwmGain = hisBarsIWMD1[1].close / hisBarsIWMD1[industryCheckPeriod].open

            #     # # if (
            #     # #     # industryLeader > qqqGain * 0.95
            #     # #     industryLeader > spyGain * 0.96 
            #     # #     # industryLeader > diaGain * 0.94
            #     # #     # industryLeader > iwmGain * 0.94
            #     # #     # industryLeader > vtiGain * 0.96
            #     # # ):
            #     # if (
            #     #     curIndustryGain > industryLeader * 0.03
            #     # ):  
            #     #     industryCheck = True
            #     # if not industryCheck: continue

            # # # Industry
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
            #     if (
            #         curIndustryGain > industryLeader * 0.45
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
            
            dataH2 = hisBarsH2Dict[symbol]
            if(len(dataH2) < 6):
                continue

            testhisBarsH1 = list(filter(lambda x:x.date >= backtestTime,dataH2))
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