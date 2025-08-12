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

#https://www.nasdaq.com/market-activity/stocks/aapl/earnings
# https://api.nasdaq.com/api/company/HMC/earnings-surprise

def GetEPS(ticker):
    try:
        response = requests.get(
            f'https://api.nasdaq.com/api/company/{ticker}/earnings-surprise',
            headers=headers,params=params).json()
        if response['status']['rCode'] == 200:
            data = response['data']
            keyName = "earningsSurpriseTable"
            df = pd.DataFrame(data[keyName]['rows'])
            df['consensusForecast'] = df['consensusForecast'].str[1:].astype(float)
            df['percentageSurprise'] = df['percentageSurprise'].str[1:].astype(float)
            # df = df[~df.paymentDate.str.contains("N/A")]
            df['dateReported'] = pd.to_datetime(df.dateReported,format='%m/%d/%Y')
            # df['dateReported'] = df['dateReported'].dt.strftime('%Y-%m-%d')
            return df
        else: return []
    except:
        return []