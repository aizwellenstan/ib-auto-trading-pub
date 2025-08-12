import pandas as pd
import numpy as np
import math

def Backtest(df, adrRange=0.07, basicPoint=0.01, period=1, length=365):
    df["Close_1_shift"] = df["Close"].shift(1)
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
            df["Open"].iloc[i] > df["Close"].iloc[i-1] * 1.02
            # and len(positions) == 0
        ):
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
from modules.aiztradingview import GetProfit, GetProfitJP, GetADR, GetLastRevenue, GetIncome, GetVol, GetFloat
from modules.shortable import GetShortable
from modules.shareholders import GetInsiderPercent
import os
import yfinance as yf
from modules.vwap import Vwap

def main(currency='USD'):
    updateData = True
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)
    shortableSymList = GetShortable()
    # revenueDict = GetLastRevenue(currency)

    total = 0
    for symbol in profitSymList:
        if symbol in shortableSymList:
            insiderPercent = GetInsiderPercent(symbol)
            if insiderPercent > 0.0982: continue
        # revenue = revenueDict[symbol]
        # if revenue < 9766622: continue
        
        if os.path.exists('./csv/vwap/{}/{}.csv'.format(currency,symbol)) and not updateData:
            df = pd.read_csv(r'./csv/vwap/{}/{}.csv'.format(currency,symbol))
        else:
            if currency != 'JPY':
                stockInfo = yf.Ticker(symbol)
            else:
                stockInfo = yf.Ticker(symbol+'.T')
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
        total += capital

        print(symbol,total)
        # print(symbol,capital)

# main('USD')
# main('JPY')


def test(currency='USD'):
    profitSymList = []
    if currency == 'USD':
        profitSymList = GetProfit()
    else:
        profitSymList = GetProfitJP()
    adrDict = GetADR(currency)
    # epsDict = GetEPS(currency)
    # revenueDict = GetLastRevenue(currency)
    # roaDict = GetROA(currency)
    # roiDict = GetROI(currency)
    # incomeDict = GetIncome()
    # volDict = GetVol(currency)
    floatDict = GetFloat(currency)
    shortableSymList = GetShortable()

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
    # adjVal = -224400000
    # while adjVal <= 672710000:
    # adjVal = 162
    # while adjVal <= 101843000:
    adjVal = 81600000
    while adjVal >= 0:
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
            print(adjVal)
            stkFloat = floatDict[symbol]
            if stkFloat > adjVal: continue
            
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
        # adjVal += 0.01
        # adjVal += 1
        adjVal -= 1

test()
