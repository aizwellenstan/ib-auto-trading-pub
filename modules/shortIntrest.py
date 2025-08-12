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

# https://api.nasdaq.com/api/quote/TSLA/short-interest?assetClass=stocks
def GetShortIntrest(ticker):
    try:
        response = requests.get(
            f'https://api.nasdaq.com/api/quote/{ticker}/short-interest',
            headers=headers,params=params).json()
        if response['status']['rCode'] == 200:
            data = response['data']
            df = pd.DataFrame(data['shortInterestTable']['rows'])
            dateKey = 'settlementDate'
            df[dateKey] = pd.to_datetime(df[dateKey],format='%m/%d/%Y')
            df[dateKey] = df[dateKey].dt.strftime('%Y-%m-%d')
            df['interest'] = df['interest'].str.replace(',','').astype(int)
            df['avgDailyShareVolume'] = df['avgDailyShareVolume'].str.replace(',','').astype(int)
            return df.to_numpy()
        else: return []
    except:
        return []
