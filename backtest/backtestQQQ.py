import pandas as pd
import numpy as np
import math
import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.slope import GetSlopeUpper, GetSlopeLower, GetSlopeUpperNew, GetSlopeLowerNew
from modules.sharpe import GetMaxDD, GetSharpeRatio
from modules.risk import GetDDDuration
from modules.movingAverage import Sma

def Backtest(df, adrRange=0.07, qqqdf=pd.DataFrame(), spydf=pd.DataFrame(), currency='USD', basicPoint=0.01, period=1, length=365):
    df = df.assign(Close_1_shift = df["Close"].shift(1))
    df["TR"] = np.abs(df.High - df.Low)
    df["TR"] = np.maximum(
        df["TR"],
        np.maximum(
            np.abs(df.Close_1_shift - df.High),
            np.abs(df.Close_1_shift - df.Low),
        ),
    )
    # The N value from Turtle Algorithm
    n_array = np.array(df["TR"].values)
    n_array[period] = np.mean(df["TR"][:period])
    for i in range(period+1, df.shape[0]):
        n_array[i] = (float(period-1) * n_array[i - 1] + df["TR"][i]) / float(period)
    df["N"] = n_array
    
    initialCapital = 2061
    capital = initialCapital  # initial capital
    vol = 0  # the initial amount of vol
    fees = 1  # fees as 0.1%
    risk = 0.006

    positions = []  # list to keep current positions
    success_history = []  # list to keep successful positions
    failure_history = []  # list to keep failed positions

    normalize = 1 / basicPoint

    # print("-" * 50)
    # print("Initial capital", capital)
    # print("-" * 50)
    # the simulation loop
    for i in range(
        1, df.shape[0]
    ):  # we start the loop from 21 day, to have N filled properly
        # Check for open position
        # The previous hour Close value is larger than upper bound and we have 0 positions
        if (
            df["Open"].iloc[i] > df["Close"].iloc[i-1]
            # and len(positions) == 0
        ):
            newdf = df.head(i-1)
            if currency =='USD':
                merge=pd.merge(newdf,qqqdf, how='inner', left_index=True, right_index=True)
                merge = merge[['qqqNextOpen','qqqLowRange']]
                merge.dropna()
                if len(merge) > 1:
                    if merge.iloc[-1].qqqNextOpen < merge.iloc[-1].qqqLowRange: continue
                # merge=pd.merge(newdf,spydf, how='inner', left_index=True, right_index=True)
                # merge = merge[['spyNextOpen','spyLowRange']]
                # if len(merge) > 1:
                #     if merge.iloc[-1].spyNextOpen < merge.iloc[-1].spyLowRange: continue
            if len(newdf) > 6:
                volVal = 0.05
                if (
                    (
                        newdf.iloc[-1].Volume +
                        newdf.iloc[-2].Volume
                    ) >
                    (
                        newdf.iloc[-3].Volume +
                        newdf.iloc[-4].Volume
                    ) * (1-volVal) and
                    (
                        newdf.iloc[-1].Volume +
                        newdf.iloc[-2].Volume
                    ) >
                    (
                        newdf.iloc[-5].Volume +
                        newdf.iloc[-6].Volume
                    ) * (1-volVal) and
                    (
                        newdf.iloc[-1].Volume +
                        newdf.iloc[-2].Volume
                    ) <
                    (
                        newdf.iloc[-3].Volume +
                        newdf.iloc[-4].Volume
                    ) * (1+volVal) and
                    (
                        newdf.iloc[-1].Volume +
                        newdf.iloc[-2].Volume
                    ) <
                    (
                        newdf.iloc[-5].Volume +
                        newdf.iloc[-6].Volume
                    ) * (1+volVal)
                ): continue

            closedf = newdf[['Close']]
            if len(closedf) > 6:
                closedf = closedf.tail(6)
                maxDD = GetMaxDD(closedf)
                if maxDD < -0.14: continue

            if len(closedf) > 4:
                closedf = closedf.tail(4)
                maxDD = GetMaxDD(closedf)
                if maxDD < -0.26: continue

            # We will use average price from the current ticker
            price = math.ceil(df["Open"].iloc[i]*normalize)/normalize
            step = capital * 1.0 - fees
            if step < price: continue
            sl = np.ceil((price - 2.0 * df["N"].iloc[i])*normalize)/normalize  # set stop loss

            # sl = math.ceil(price - adrRange * 0.05)*100/100
            # if adrRange > 0.14:
            #     sl =  math.ceil(price - adrRange * 0.35)*100/100
            if sl < df["Close"].iloc[i-1]: sl = df["Close"].iloc[i-1]

            if price-sl < basicPoint*2: sl = price - basicPoint*2
            newVol = int(min(np.floor(step / price),capital*risk/(price-sl)))
            newVol = int(min(newVol,capital/price))
            if newVol < 1: continue
            vol += newVol
            capital -= newVol * price
            sl = price - 2.0 * df["N"].iloc[i]  # set stop loss
            positions += [{"time": i, "price": price}]

            # print(
            #     "Open position @",
            #     price,
            #     "buy",
            #     vol,
            #     "Stop loss @",
            #     sl,
            # )

        # Check to close position
        elif len(positions) > 0 and (
            df["Low"].iloc[i] < sl  # we are lower than stop loss
            or i
            == df.shape[0] - 1  # the end of simulation and we want to close all positions
        ):

            price = math.floor(df["Low"].iloc[i]*normalize)/normalize
            if vol < 0: continue
            capital += vol * price * 1 - fees
            sl, vol = 0.0, 0.0
            # print("Close position @", price, "capital", capital)
            if positions[-1]["price"] < price:
                for p in positions:
                    success_history += [
                        {
                            "price": [p["price"], price],
                        }
                    ]
            else:
                for p in positions:
                    failure_history += [
                        {
                            "price": [p["price"], price],
                        }
                    ]
            positions = []

    success_rate = 0
    if len(success_history) + len(failure_history) > 0:
        success_rate = len(success_history) / (len(failure_history) + len(success_history))

    # print("-" * 50)
    # print("Success rate", success_rate)
    # print("Capital at the end", np.round(capital, 2))
    return capital-initialCapital
    return capital
    # print("-" * 50)
    # print("Summary of % change in positions")
    # price_changes = []
    # for h in [failure_history, success_history]:
    #     for position in h:
    #         percent_change = np.round(
    #             (position["price"][1] - position["price"][0])
    #             / position["price"][0]
    #             * 100.0,
    #             2,
    #         )
    #         print("Percent change in position", percent_change)

import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.aiztradingview import GetProfit, GetProfitJP, GetADR, GetLastRevenue, GetIncome, GetVol, GetFloat, GetDebtEquity, GetCurrentAssets, GetBeta, GetPB, GetEBITDA, GetGrossMargin, GetGrossProfit, GetNetMargin, GetOpertatingMargin, GetPretaxMargin, GetQuickRatio, GetROE, GetRevenueEmployee, GetYTDPerf, GetVolatilityM, GetVolatilityW, GetVolatilityD, GetSector, GetIndustry, GetAttr, GetZScore, GetFloat
from modules.shortable import GetShortable
from modules.shareholders import GetInsiderPercent, GetInstitutions, GetFloatPercentHeld
from modules.beta import GetBeta
from modules.adr import GetGreenADR, GetRedADR, GetVwapGreenADR, GetVwapRedADR
import os
import yfinance as yf
from modules.vwap import Vwap
from collections import defaultdict

def main(currency='USD'):
    updateData = False
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)
    shortableSymList = GetShortable()
    # revenueDict = GetLastRevenue(currency)
    # marketCapDict = GetMarketCap()
    # currentAssetsDict = GetCurrentAssets(currency)
    # betaDict = GetBeta(currency)
    # ebitdaDict = GetEBITDA(currency)
    # operatingMarginDict = GetOpertatingMargin(currency)
    # ytdPerfDict = GetYTDPerf(currency)
    # volatilitMDict = GetVolatilityM(currency)

    if currency=='USD':
        if os.path.exists('./csv/vwap/USD/QQQ.csv') and not updateData:
            qqqdf = pd.read_csv(r'./csv/vwap/USD/QQQ.csv')
        else:
            stockInfo = yf.Ticker("QQQ")
            hist = stockInfo.history(period="36500d")
            hist.dropna()
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            start_path = 'mainFolder'
            hist.to_csv('./csv/vwap/USD/QQQ.csv')
            qqqdf = hist
        qqqdf = qqqdf.assign(qqqNextOpen = qqqdf.Open.shift(-1))
        # qqqdf = qqqdf.assign(qqqLowRange = (qqqdf.Close+qqqdf.Open)/2)
        # qqqdf = qqqdf.assign(qqqLowRange = qqqdf.Open)
        qqqdf = qqqdf.assign(qqqLowRange = qqqdf.Close.shift(1))
        qqqdf = qqqdf[['qqqNextOpen','qqqLowRange']]

        if os.path.exists('./csv/vwap/USD/SPY.csv') and not updateData:
            spydf = pd.read_csv(r'./csv/vwap/USD/SPY.csv')
        else:
            stockInfo = yf.Ticker("SPY")
            hist = stockInfo.history(period="36500d")
            hist.dropna()
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            start_path = 'mainFolder'
            hist.to_csv('./csv/vwap/USD/SPY.csv')
            spydf = hist
        spydf = spydf.assign(spyNextOpen = spydf.Open.shift(-1))
        spydf = spydf.assign(spyLowRange = (spydf.Close+spydf.Open)/2)
        spydf = spydf[['spyNextOpen','spyLowRange']]
    

    total = 0
    profitSymList = ['QQQ']
    for symbol in profitSymList:
        if symbol in shortableSymList:
            insiderPercent = GetInsiderPercent(symbol)
            if symbol != "QQQ":
                if insiderPercent > 0.0982: continue
        # revenue = revenueDict[symbol]
        # if revenue < 9766622: continue

        # marketCap = marketCapDict[symbol]
        # if marketCap < 1296933000: continue

        # if symbol in currentAssetsDict:
        #     currentAssets = currentAssetsDict[symbol]
        #     if currentAssets < 110000000: continue

        # if symbol in ebitdaDict:
        #     ebitda = ebitdaDict[symbol]
        #     if ebitda < -4556000000: continue

        # operatingMargin = operatingMarginDict[symbol]
        # if operatingMargin < -1393: continue
        # if symbol not in ytdPerfDict: continue
        # ytdPerf = ytdPerfDict[symbol]
        # if ytdPerf < -72.02: continue

        # volatilityM = volatilitMDict[symbol]
        # if volatilityM < 2.21: continue
        # if volatilityM > 13.45: continue
        
        if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)) and not updateData:
            df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
        else:
            if currency != "JPY":
                stockInfo = yf.Ticker(symbol)
            else:
                stockInfo = yf.Ticker(symbol + ".T")
            hist = stockInfo.history(period="36500d")
            hist.dropna()
            if len(hist) < 1: continue
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            start_path = 'mainFolder'
            hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
            df = hist

        df = df[['Open','High','Low','Close','Volume','Vwap']]

        stdVol = df.Volume.std()
        if stdVol < 2313626.2962641073: continue

        newdf = df
        newdf = newdf.assign(h1h2=newdf.High-newdf.High.shift(1))
        avgH1H2 = newdf['h1h2'].mean()
        if avgH1H2 < 0.00043988668679486215: continue

        newdf = df[['Open','High','Low','Close']]
        npArr = newdf.to_numpy()
        upper = GetSlopeUpper(npArr)
        if upper < 0: continue
        
        adrRange = adrDict[symbol]
        capital = Backtest(df, adrRange, qqqdf, spydf, currency)
        total += capital

        print(symbol,total)
        # print(symbol,capital)

main('USD')
# main('JPY')


def test(currency='USD'):
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)
    # shortableSymList = GetShortable()
    # epsDict = GetEPS(currency)
    # revenueDict = GetLastRevenue(currency)
    # roaDict = GetROA(currency)
    # roiDict = GetROI(currency)
    # incomeDict = GetIncome()
    # volDict = GetVol(currency)
    # floatDict = GetFloat(currency)
    # shortableSymList = GetShortable()
    # epsDict = GetEPSttm(currency)
    # currentRatioDict = GetCurrentRatio(currency)
    # debtEquityDict = GetDebtEquity(currency)
    # marketCapDict = GetMarketCap()
    # debtDict = GetNetDebt(currency)
    # currentAssetsDict = GetCurrentAssets(currency)
    # betaDict = GetBeta(currency)
    # pbDict = GetPB(currency)
    # ebitdaDict = GetEBITDA(currency)
    # grossMarginDict = GetGrossMargin(currency)
    # profitDict = GetGrossProfit(currency)
    # netMarginDict = GetNetMargin(currency)
    # operatingMarginDict = GetOpertatingMargin(currency)
    # pretaxMarginDict = GetPretaxMargin(currency)
    # quickRatioDict = GetQuickRatio(currency)
    # roeDict = GetROE(currency)
    # revenueEmployeeDict = GetRevenueEmployee(currency)
    # ytdPerfDict = GetYTDPerf(currency)
    # volatilitMDict = GetVolatilityM(currency)
    # volatilitWDict = GetVolatilityW(currency)
    # volatilitDDict = GetVolatilityD(currency)
    # industryDict = GetIndustry(currency)

    institutionsDict = {}
    for symbol in profitSymList:
        institutions = GetFloatPercentHeld(symbol)
        institutionsDict[symbol] = institutions

    # lossIndustry = []

    # if currency == 'USD':
    #     symbol = 'IWM'
    #     if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
    #         iwmDf = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
    #     else:
    #         stockInfo = yf.Ticker(symbol)
    #         hist = stockInfo.history(period="36500d")
    #         hist = hist.dropna()
    #         v = hist.Volume.values
    #         h = hist.High.values
    #         l = hist.Low.values
    #         hist['Vwap'] = Vwap(v,h,l)
    #         start_path = 'mainFolder'
    #         hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
    #         iwmDf = hist

    # betaDict = {}
    # for symbol in profitSymList:
    #     if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
    #         df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
    #     else:
    #         stockInfo = yf.Ticker(symbol)
    #         hist = stockInfo.history(period="36500d")
    #         hist = hist.dropna()
    #         if len(hist) < 1: continue
    #         v = hist.Volume.values
    #         h = hist.High.values
    #         l = hist.Low.values
    #         hist['Vwap'] = Vwap(v,h,l)
    #         start_path = 'mainFolder'
    #         hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
    #         df = hist

    #     beta = GetBeta(df[['Close']],iwmDf[['Close']])
    #     betaDict[symbol] = beta

    # insiderPercentDict = {}
    capitalDict = {}
    
    maxCapital = 0
    # adjVal = 0.0001
    # while adjVal <= 0.0982:
    # adjVal = -48873000
    # while adjVal <= 365817000:
    # adjVal = -9486.2
    # while adjVal <= 91.2:
    # adjVal = -8284.64
    # while adjVal <= 1753.98:
    # adjVal = -1,000,000,000
    # while adjVal <= 672710000:
    # adjVal = 162
    # while adjVal <= 101843000:
    # adjVal = 8160000000
    # adjVal = 1230000
    # while adjVal >= 0:
    # adjVal = 4891367.37
    # while adjVal >= 0.03:
    # adjVal = -4557000000
    # while adjVal <= 86531000000:
    # adjVal = -6180753.33
    # while adjVal <= 99.54:
    # adjVal = -1157000000
    # while adjVal <= 37435000000:
    # adjVal = -253435700
    # while adjVal <= 5764.82:
    # adjVal = -1400
    # while adjVal <= 199.19:
    # adjVal = -9329.65
    # while adjVal <= 5764.82:
    # adjVal = 0
    # while adjVal <= 7747.79:
    # adjVal = -15511.85
    # while adjVal <= 6160:
    # adjVal = -5719000
    # while adjVal <= 41615000:
    # adjVal = -94.15
    # while adjVal <= 1812.9:
    # adjVal = 0
    # while adjVal <= 116.94:
    # adjVal = 0
    # while adjVal <= 80.29:
    # adjVal = 0
    # while adjVal <= 80.78:
    adjVal = 0.01
    while adjVal <= 1:
        total = 0
        for symbol in profitSymList:
            # if symbol in insiderPercentDict:
            #     insiderPercent = insiderPercentDict[symbol]
            # else:
            #     insiderPercent = GetInsiderPercent(symbol)
            #     insiderPercentDict[symbol] = insiderPercent
            # if insiderPercent > adjVal: continue

            # if symbol in shortableSymList:
            # eps = epsDict[symbol]
            # if eps < adjVal: continue
            # revenue = revenueDict[symbol]
            # if revenue < adjVal: continue
            # roa = roaDict[symbol]
            # if roa < adjVal: continue
            # roi = roiDict[symbol]
            # if roi < adjVal: continue
            # income = incomeDict[symbol]
            # if income < adjVal: continue
            # vol = volDict[symbol]
            # if vol < adjVal: continue
            # stkFloat = floatDict[symbol]
            # if stkFloat > adjVal: continue
            # eps = epsDict[symbol]
            # if eps < adjVal: continue
            # if symbol not in currentRatioDict: 
            # currentRatio = currentRatioDict[symbol]
            # if currentRatio < adjVal: continue
            # debtEquity = debtEquityDict[symbol]
            # if debtEquity > adjVal: continue
            # marketCap = marketCapDict[symbol]
            # if marketCap < adjVal: continue
            # debt = debtDict[symbol]
            # if debt > adjVal: continue
            # if symbol in currentAssetsDict:
            #     currentAssets = currentAssetsDict[symbol]
            #     if currentAssets < adjVal: continue 
            # beta = totalDebtDict[symbol]
            # if beta < -0.87: continue
            # if symbol not in pbDict: continue
            # pb = pbDict[symbol]
            # if pb > adjVal: continue
            # if symbol in ebitdaDict:
            #     ebitda = ebitdaDict[symbol]
            #     if ebitda < adjVal: continue

            # if symbol not in grossMarginDict: continue
            # grossMargin = grossMarginDict[symbol]
            # if grossMargin < adjVal: continue

            # if symbol not in profitDict: continue
            # profit = profitDict[symbol]
            # if profit < adjVal: continue

            # netMargin = netMarginDict[symbol]
            # if netMargin < adjVal: continue

            # operatingMargin = operatingMarginDict[symbol]
            # if operatingMargin < adjVal: continue

            # if symbol not in pretaxMarginDict: continue
            # pretaxMargin = pretaxMarginDict[symbol]
            # if pretaxMargin < adjVal: continue

            # if symbol not in quickRatioDict: continue
            # quickRatio = quickRatioDict[symbol]
            # if quickRatio < adjVal: continue

            # if symbol not in roeDict: continue
            # roe = roeDict[symbol]
            # if roe < adjVal: continue

            # if symbol not in revenueEmployeeDict: continue
            # revenueRmployee = revenueEmployeeDict[symbol]
            # if revenueRmployee < adjVal: continue

            # if symbol not in ytdPerfDict: continue
            # ytdPerf = ytdPerfDict[symbol]
            # if ytdPerf < adjVal: continue

            # volatilityM = volatilitMDict[symbol]
            # if volatilityM > adjVal: continue

            # volatilityW = volatilitWDict[symbol]
            # if volatilityW < adjVal: continue

            # volatilityD = volatilitDDict[symbol]
            # if volatilityD < adjVal: continue

            institutions = institutionsDict[symbol]

            if symbol in capitalDict:
                capital = capitalDict[symbol]
            else:
                if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
                    df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
                else:
                    stockInfo = yf.Ticker(symbol)
                    hist = stockInfo.history(period="36500d")
                    hist = hist.dropna()
                    if len(hist) < 1: continue
                    v = hist.Volume.values
                    h = hist.High.values
                    l = hist.Low.values
                    hist['Vwap'] = Vwap(v,h,l)
                    start_path = 'mainFolder'
                    hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
                    df = hist
                    
                adrRange = adrDict[symbol]
                capital = Backtest(df, adrRange)
                capitalDict[symbol] = capital
            total += capital

        if total > maxCapital:
            maxCapital = total
            print(maxCapital,adjVal)
        # adjVal += 0.0001
        adjVal += 0.01
        # adjVal += 1
        # adjVal -= 1
        # adjVal -= 0.01
        # adjVal += 0.001
        # adjVal += 10
        # adjVal += 100
        # adjVal += 1000
        # adjVal += 1000000

# test()

def testAttr(currency='USD'):
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)

    capitalDict = {}

    attrDict = GetAttr(currency)
    # attrDict = GetZScore(currency)
    attrList = list(attrDict.values())
    attrList.sort()

    maxCapital = 0
    idx = 0
    while idx < len(attrList):
        total = 0
        for symbol in profitSymList:

            attr = attrDict[symbol]
            if attr < attrList[idx]:
                continue

            if symbol in capitalDict:
                capital = capitalDict[symbol]
            else:
                if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
                    df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
                else:
                    stockInfo = yf.Ticker(symbol)
                    hist = stockInfo.history(period="36500d")
                    hist = hist.dropna()
                    if len(hist) < 1: continue
                    v = hist.Volume.values
                    h = hist.High.values
                    l = hist.Low.values
                    hist['Vwap'] = Vwap(v,h,l)
                    start_path = 'mainFolder'
                    hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
                    df = hist
                    
                adrRange = adrDict[symbol]
                capital = Backtest(df, adrRange)
                capitalDict[symbol] = capital
            total += capital

        if total > maxCapital:
            maxCapital = total
            print(maxCapital,attrList[idx])
        idx += 1

# testAttr()

def testSector(currency='USD'):
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)

    capitalDict = {}

    attrDict = GetAttr(currency)

    sectorDict = GetSector(currency)

    sectorListGroup = defaultdict(list)
    for key, val in sorted(sectorDict.items()):
        if key in profitSymList:
            sectorListGroup[val].append(key)

    sectorLeaderBoard = {}

    maxCapital = 0
    adjVal = 0.01
    while adjVal <= 1:
        total = 0
        for symbol in profitSymList:

            attr = GetInsiderPercent(symbol)

            sectorCheck = False
            curSectorGain = attr
            sectorLeader = curSectorGain
            sector = sectorDict[symbol]
            groupList = sectorListGroup[sector]
            if len(groupList) > 1:
                if sector in sectorLeaderBoard:
                    sectorLeader = sectorLeaderBoard[sector]
                else:
                    for sym2 in groupList:
                        sectorGain = attrDict[sym2]
                        if sectorGain > sectorLeader:
                            sectorLeader = sectorGain
                    sectorLeaderBoard[sector] = sectorLeader
            else:
                sectorCheck = True

            if curSectorGain > sectorLeader * adjVal:
                sectorCheck = True
            if not sectorCheck: continue

            if symbol in capitalDict:
                capital = capitalDict[symbol]
            else:
                if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
                    df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
                else:
                    stockInfo = yf.Ticker(symbol)
                    hist = stockInfo.history(period="36500d")
                    hist = hist.dropna()
                    if len(hist) < 1: continue
                    v = hist.Volume.values
                    h = hist.High.values
                    l = hist.Low.values
                    hist['Vwap'] = Vwap(v,h,l)
                    start_path = 'mainFolder'
                    hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
                    df = hist
                    
                adrRange = adrDict[symbol]
                capital = Backtest(df, adrRange)
                capitalDict[symbol] = capital
            total += capital

        if total > maxCapital:
            maxCapital = total
            print(maxCapital,adjVal)
        adjVal += 0.01

# testSector()

# def testIndustry(currency='USD'):
#     profitSymList = []
#     if currency == 'USD':
#         profitSymList = GetProfit()
#     else:
#         profitSymList = GetProfitJP()
#     adrDict = GetADR(currency)

#     capitalDict = {}

#     attrDict = GetAttr(currency)

#     industryDict = GetIndustry(currency)

#     industryListGroup = defaultdict(list)
#     for key, val in sorted(industryDict.items()):
#         if key in profitSymList:
#             industryListGroup[val].append(key)

#     industryLeaderBoard = {}

#     maxCapital = 0
#     adjVal = 0.01
#     while adjVal <= 1:
#         total = 0
#         for symbol in profitSymList:

#             attr = attrDict[symbol]

#             industryCheck = False
#             curIndustryGain = attr
#             industryLeader = curIndustryGain
#             industry = industryDict[symbol]
#             groupList = industryListGroup[industry]
#             if len(groupList) > 1:
#                 if industry in industryLeaderBoard:
#                     industryLeader = industryLeaderBoard[industry]
#                 else:
#                     for sym2 in groupList:
#                         industryGain = attrDict[sym2]
#                         if industryGain > industryLeader:
#                             industryLeader = industryGain
#                     industryLeaderBoard[industry] = industryLeader
#             else:
#                 industryCheck = True

#             if curIndustryGain > industryLeader * adjVal:
#                 industryCheck = True
#             if not industryCheck: continue

#             if symbol in capitalDict:
#                 capital = capitalDict[symbol]
#             else:
#                 if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
#                     df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
#                 else:
#                     stockInfo = yf.Ticker(symbol)
#                     hist = stockInfo.history(period="36500d")
#                     hist = hist.dropna()
#                     if len(hist) < 1: continue
#                     v = hist.Volume.values
#                     h = hist.High.values
#                     l = hist.Low.values
#                     hist['Vwap'] = Vwap(v,h,l)
#                     start_path = 'mainFolder'
#                     hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
#                     df = hist
                    
#                 adrRange = adrDict[symbol]
#                 capital = Backtest(df, adrRange)
#                 capitalDict[symbol] = capital
#             total += capital

#         if total > maxCapital:
#             maxCapital = total
#             print(maxCapital,adjVal)
#         adjVal += 0.01

# testIndustry()

def testCusAttr(currency='USD'):
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)

    sharesDict = GetAttr(currency)

    capitalDict = {}

    attrDict = {}
    for symbol in profitSymList:
        if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
            df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
        else:
            stockInfo = yf.Ticker(symbol)
            hist = stockInfo.history(period="max")
            hist = hist.dropna()
            if len(hist) < 1: continue
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            start_path = 'mainFolder'
            hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
            df = hist

        sharpe = GetSharpeRatioNew(df[['Close']])
        if sharpe < 0.01: sharpe = 0.01
        maxDD = GetDDDuration(df[['Close']])

        if symbol not in attrDict:
            attrDict[symbol] =  sharpe/maxDD
    attrList = list(attrDict.values())
    attrList.sort()

    maxCapital = 0
    idx = 0
    while idx < len(attrList):
        total = 0
        for symbol in profitSymList:
            attr = attrDict[symbol]
            if attr < attrList[idx]: continue

            if symbol in capitalDict:
                capital = capitalDict[symbol]
            else:
                if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)):
                    df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
                else:
                    stockInfo = yf.Ticker(symbol)
                    hist = stockInfo.history(period="36500d")
                    hist = hist.dropna()
                    if len(hist) < 1: continue
                    v = hist.Volume.values
                    h = hist.High.values
                    l = hist.Low.values
                    hist['Vwap'] = Vwap(v,h,l)
                    start_path = 'mainFolder'
                    hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
                    df = hist

                adrRange = adrDict[symbol]
                capital = Backtest(df, adrRange)
                capitalDict[symbol] = capital
            total += capital

        if total > maxCapital:
            maxCapital = total
            print(maxCapital,attrList[idx])
        idx += 1

# testCusAttr()
