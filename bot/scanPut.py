import pandas as pd
import numpy as np
import math
import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.optionChain import GetAllPut
import datetime as dt
from modules.same_week import same_week
from modules.discord import Alert

initialCapital = 2061
fees = 2  # fees as 0.1%
risk = 0.006

today = dt.datetime.today()
weekday = today.weekday()
date_format = "%Y%m%d"

def GetExpir(expir):
    expirTime = dt.datetime.strptime(expir, date_format)
    daysLeft = (expirTime - today).days + 1
    if  daysLeft > 7:
        daysLeft -= int(daysLeft/7+1)*2
    elif not same_week(today,expirTime):
        daysLeft -= 2
    if daysLeft == -1:
        daysLeft = 0
    print(f"daysLeft {daysLeft}")
    return daysLeft

def BacktestSpread(symbol, npArr, currency='USD', shortable=False,  basicPoint=0.01):
    vol = 0  # the initial amount of vol
    positions = 0
    normalize = 1 / basicPoint

    # combination = GetDIABullPutCreaditSpread(5)
    # combination = GetDIABullCallCreaditSpread(5)
    diaPrice, combination = GetAllPut(symbol)
    print(combination)

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        print(comb)
        expir = comb['Expir']
        daysLeft = GetExpir(expir)
        spreadRange = diaPrice - comb['ShortBE']
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft-1
        ):
            shortBE = npArr[i][0] - spreadRange
            if not npArr[i][6] == weekday: continue
            if npArr[i+daysLeft][3] < shortBE:
                capital += (shortBE - npArr[i+daysLeft][3]) * 100
            else: capital -= comb['loss']
        minLoss = 500
        if capital > maxCapital:
            if comb['loss'] < minLoss:
                minLoss = comb['loss']
                maxCapital = capital
                bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"{symbol} Price {diaPrice} \n BuyPut {bestCreaditSpread}\n"
    Alert(message)

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
    profitSymList = ['AMC', 'AAPL', 'AMZN', 'AMD', 'BBBY', 'F', 'NVDA', 'WBD', 'DKNG', 'PLTR', 'BABA', 'GOOGL', 'CVNA', 'GME', 'SQ', 'MSFT', 'COIN', 'INTC', 'UPST', 'NKLA', 'CHPT', 'VRM', 'DIS', 'DWAC', 'RBLX', 'TAL', 'FDX', 'YETI', 'ITB', 'CVX', 'OXY',
'TGT', 'ARKK', 'NFLX', 'DLTR',
'W', 'UPS', 'MCK', 'XLF', 'ABC', 'DBC', 'FCG', 'GD', 'BMY', 'OKTA', 'GLD', 'HSY', 'FTNT', 'JNPR', 'COST', 'OIH', 'ORLY', 'REGN', 'PANW', 'AVGO', 'MU', 'PAYC', 'SPOT', 'ZS', 'TDOC', 'FOXA', 'AMAT', 'FL', 'FCX', 'CSIQ', 'HPE', 'DLR', 'TLRY', 'TWTR',
'EWG', 'XOM', 'EWU', 'TLT', 'V', 'C', 'FXY', 'NEE', 'UAA', 'CHWY', 'LCID', 'HOOD', 'T', 'ADBE', 'SI', 'NUGT', 'GM', 'KHC', 'ALB', 'MDT', 'X', 'TRV', 'KR',
'CDNS', 'JD', 'MS', 'RIVN', 'BIDU', 'FXC', 'DD', 'IRNT', 'GMBL', 'LIDR']

    blackList = ['BABA','CVNA','DIA']
    delisted = []
    maxCapital = 0
    update = False
    for symbol in profitSymList:
        if symbol in blackList: continue
        if symbol in delisted: continue
        if os.path.exists('../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol)) and not update:
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
            hist.to_csv('../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol))
            print(symbol)
            df = hist
            df['Date'] = df.index

        weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(Weekday=weekday.dt.dayofweek)
        
        df = df[['Open','High','Low','Close','Volume','Vwap', 'Weekday','Rsi']]
    
        npArr = df.to_numpy()

        BacktestSpread(symbol, npArr,currency)

main()