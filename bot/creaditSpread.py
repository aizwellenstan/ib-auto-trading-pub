import pandas as pd
import numpy as np
import math
import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.yf_option_chain import GetSPXCreaditSpread
from modules.yf_option_chain import GetSPXPrice
import datetime as dt
from modules.same_week import same_week
from modules.discord import Alert

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]
shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

initialCapital = 2061
fees = 2  # fees as 0.1%
risk = 0.006

from numba import jit
@jit(nopython=True)
def Backtest(npArr, currency='USD', shortable=False,  basicPoint=0.01):
    capital = 0
    vol = 0  # the initial amount of vol
    positions = 0
    normalize = 1 / basicPoint
    
    for i in range(
        1, len(npArr-1)
    ):
        if not npArr[i][6] == 1: continue

        # if npArr[i+1][3] > npArr[i][0]: capital += 1
        # else: capital -= 1

        # 1d expir BULL PUT 5 spread
        # if npArr[i+1][3] < npArr[i][0] - 0: capital -= 350
        # else: capital += 150
        # if npArr[i+1][3] < npArr[i][0] - 5: capital -= 310
        # else: capital += 190
        # if npArr[i+1][3] < npArr[i][0] - 10: capital -= 340
        # else: capital += 160
        # if npArr[i+1][3] < npArr[i][0] - 15: capital -= 430
        # else: capital += 70
        if npArr[i+1][3] < npArr[i][0] - 20: capital -= 390
        else: capital += 110
        # if npArr[i+1][3] < npArr[i][0] - 25: capital -= 450
        # else: capital += 50
        # if npArr[i+1][3] < npArr[i][0] - 30: capital -= 460
        # else: capital += 40
        # if npArr[i+1][3] < npArr[i][0] - 35: capital -= 470
        # else: capital += 30
        # if npArr[i+1][3] < npArr[i][0] - 40: capital -= 480
        # else: capital += 20

        # 3d expir BULL PUT 5 spread
        # if npArr[i+3][3] < npArr[i][0] - 55: capital -= 480
        # else: capital += 20

        # 1d expir BULL PUT 10 spread
        # if npArr[i+1][3] < npArr[i][0] - 0: capital -= 620
        # else: capital += 380
        # if npArr[i+1][3] < npArr[i][0] - 5: capital -= 710
        # else: capital += 290
        # if npArr[i+1][3] < npArr[i][0] - 10: capital -= 760
        # else: capital += 240
        # if npArr[i+1][3] < npArr[i][0] - 15: capital -= 800
        # else: capital += 200
        # if npArr[i+1][3] < npArr[i][0] - 20: capital -= 800
        # else: capital += 200
        # if npArr[i+1][3] < npArr[i][0] - 25: capital -= 830
        # else: capital += 170
        # if npArr[i+1][3] < npArr[i][0] - 30: capital -= 850
        # else: capital += 150
        # if npArr[i+1][3] < npArr[i][0] - 35: capital -= 860
        # else: capital += 140
        # if npArr[i+1][3] < npArr[i][0] - 40: capital -= 900
        # else: capital += 100

        # if npArr[i+1][3] < npArr[i][0] - 0: capital -= 990
        # else: capital += 510

        # 1d expir BEAR CALL 10 spread
        # if npArr[i+1][3] > npArr[i][0] + 0: capital -= 670
        # else: capital += 330
        # if npArr[i+1][3] > npArr[i][0] + 5: capital -= 710
        # else: capital += 290
        # if npArr[i+1][3] > npArr[i][0] + 10: capital -= 750
        # else: capital += 250
        # if npArr[i+1][3] > npArr[i][0] + 15: capital -= 770
        # else: capital += 230

        # if npArr[i+3][3] < npArr[i][0] - 50: capital -= 450
        # else: capital += 50
        # if npArr[i+3][3] < npArr[i][0] - 65: capital -= 470
        # else: capital += 30
        
    return capital

def BacktestSpread(npArr, currency='USD', shortable=False,  basicPoint=0.01):
    vol = 0  # the initial amount of vol
    positions = 0
    normalize = 1 / basicPoint

    expir = "04/14/2022"
    combination = GetSPXCreaditSpread(expir,5)
    print(combination)
    spxPrice = GetSPXPrice()

    today = dt.datetime.today()
    weekday = today.weekday()
    date_format = "%m/%d/%Y"
    expirTime = dt.datetime.strptime(expir, date_format)
    daysLeft = (expirTime - today).days + 1
    if not same_week(today,expirTime):
        daysLeft -= 2
    print(f"daysLeft {daysLeft}")

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        spreadRange = spxPrice - comb['SellStrike']
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft
        ):
            if not npArr[i][6] == weekday: continue
            if npArr[i+daysLeft][3] < npArr[i][0] - spreadRange: capital -= comb['loss']
            else: capital += comb['profit']
        if capital > maxCapital:
            maxCapital = capital
            bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"bestCreaditSpread {bestCreaditSpread}"
    # Alert(message)

import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.shortable import GetShortable
from modules.shareholders import GetZScore, GetInsiderPercent, GetInstitutions, GetFloatPercentHeld, GetPercentHeld, GetShareholders, GetAuditRisk
from modules.beta import GetBeta
from modules.adr import GetGreenADR, GetRedADR, GetVwapGreenADR, GetVwapRedADR
import os
import yfinance as yf
from modules.vwap import Vwap
from collections import defaultdict
import csv
from modules.rsi import Rsi
from modules.adx import Adx

def main(currency='USD'):
    profitSymList = ['^GSPC']

    delisted = []
    maxCapital = 0
    for symbol in profitSymList:
        if symbol in delisted: continue
        if os.path.exists('../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol)):
            df = pd.read_csv(r'../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol))
        else:
            stockInfo = yf.Ticker(symbol)
            hist = stockInfo.history(period="max")
            hist = hist.dropna()
            if len(hist) < 1: 
                delisted.append(symbol)
                continue
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            hist['Rsi'] = Rsi(hist.Close.values.tolist())
            hist['Adx'] = Adx(hist)
            start_path = 'mainFolder'
            hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
            print(symbol)
            df = hist
            df['Date'] = df.index

        weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(Weekday=weekday.dt.dayofweek)
        
        df = df[['Open','High','Low','Close','Volume','Vwap', 'Weekday','Rsi']]
    
        npArr = df.to_numpy()

        BacktestSpread(npArr,currency)

main()