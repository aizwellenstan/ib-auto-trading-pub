import requests
from bs4 import BeautifulSoup
import pandas as pd
from user_agent import generate_user_agent
import yfinance as yf
from datetime import datetime

headers = {
    'User-Agent': generate_user_agent(),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,em;q=0.5',
    'Origin': 'https://www.nasdaq.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nasdaq.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'smae-site',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers', 
}

params = {
    ('assetclass', 'stocks'),
}

# https://www.nasdaq.com/market-activity/stocks/aapl/dividend-history
def GetDividend(ticker):
    try:
        response = requests.get(
            f'https://api.nasdaq.com/api/quote/{ticker}/dividends',
            headers=headers,params=params).json()
        if response['status']['rCode'] == 200:
            data = response['data']
            df = pd.DataFrame(data['dividends']['rows'])
            df['amount'] = df['amount'].str[1:].astype(float)
            df = df[~df.paymentDate.str.contains("N/A")]
            df['paymentDate'] = pd.to_datetime(df.paymentDate,format='%m/%d/%Y')
            df['paymentDate'] = df['paymentDate'].dt.strftime('%Y-%m-%d')
            return df
        else: return []
    except:
        return []

def GetData(symbol, currency):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        data = stockInfo.history(period="max")
        return data
    except: return []

def GetDividendYf(symbol, currency='USD'):
    df = GetData(symbol, currency)
    if len(df) < 1: return 0
    try:
        return df['Dividends'].values[-1]
    except: return 0

def GetDividendData(symbol, currency):
    try:
        df = GetData(symbol, currency)
        if len(df) < 1: return 0 
        dividend = 0
        dividendKey = "adjusted_amount"
        df = df.loc[df['Dividends'] > 0]
        df = df.assign(date=df.index.date)
        df = df.assign(previousDate=df.date.shift(1))
        df = df.assign(duration = df.index.date-df.previousDate)
        dividendKey = 'Dividends'
        maxDur = df.duration.max().days
        if maxDur > 366: return 0
        avg = df[dividendKey].quantile(0.99)
        df = df[(df.index.date>datetime.strptime('2021-03-18','%Y-%m-%d').date())]
        dfLenBefore = len(df)
        df = df[df[dividendKey] < avg * 1.0593220338983054]
        dividend = df[dividendKey].values
        dividend = sum(dividend)
        dfLenAfter = len(df[dividendKey])
        if dfLenAfter > 0:
            avgDividend = dividend/dfLenAfter
            dividend += (dfLenBefore-dfLenAfter)*avgDividend
        return dividend
    except: return 0
