import requests
from bs4 import BeautifulSoup
import pandas as pd
from user_agent import generate_user_agent
import yfinance as yf
import sys
import json
from datetime import datetime, timedelta

headers = {
    'User-Agent': generate_user_agent()
}

params = {
}

# https://storage.googleapis.com/iexcloud-hl37opg/api/logos/NPNYY.png
# https://seekingalpha.com/api/v3/symbols/npnyy/dividend_history?years=1000

# id
# https://seekingalpha.com/api/v3/symbols/aapl
# aapl
# https://finance-api.seekingalpha.com/real_time_quotes?sa_ids=146
# https://seekingalpha.com/api/v3/symbols/aapl/sec-filings
def GetDividend(ticker):
    try:
        response = requests.get(
            f'https://seekingalpha.com/api/v3/symbols/{ticker}/dividend_history?years=1000',
            headers=headers,params=params).json()
        data = response['data']
        dividendHistory = []
        for d in data:
            dividendHistory.append(d['attributes'])
        df = pd.DataFrame(dividendHistory)
        #     # df = pd.DataFrame(data['dividends']['rows'])
        df['amount'] = df['amount'].astype(float)
        #     # df = df[~df.paymentDate.str.contains("N/A")]
        #     # df['paymentDate'] = pd.to_datetime(df.paymentDate,format='%m/%d/%Y')
        #     # df['paymentDate'] = df['paymentDate'].dt.strftime('%Y-%m-%d')
        #     # return df
        return df
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetRealTimeData(ticker):
    try:
        response = requests.get(
            f'https://seekingalpha.com/api/v3/symbols/{ticker}',
            headers=headers,params=params).json()
        sa_id = response["data"]["id"]
        return sa_id
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return ""

def ConvertDate(input_datetime_str):
    input_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
    
    # # Add one day to the datetime
    # next_day_datetime = input_datetime + timedelta(days=1)

    # # Format the next day datetime as "YYYY-MM-DD"
    # next_day_str = next_day_datetime.strftime('%Y-%m-%d')

    return input_datetime

# https://seekingalpha.com/api/v3/symbol_data/estimates?estimates_data_items=eps_primary&group_by_month=true&period_type=quarterly&relative_periods=0%2C-1%2C-2%2C-3%2C-4%2C-5%2C-6%2C-7&return_window=120&ticker_ids=146
# https://seekingalpha.com/api/v3/symbol_data/estimates?estimates_data_items=eps_primary&group_by_month=true&period_type=quarterly&relative_periods=0%2C-1%2C-2%2C-3%2C-4%2C-5%2C-6%2C-7&return_window=120&ticker_ids=146
# https://seekingalpha.com/api/v3/symbol_data/estimates?estimates_data_items=eps_primary&group_by_month=true&period_type=quarterly&relative_periods=0%2C-1%2C-2%2C-3%2C-4%2C-5%2C-6%2C-7%2C-8%2C-9%2C-10%2C-11%2C-12%2C-13%2C-14%2C-15&return_window=120&ticker_ids=146
def GetEPS(ticker):
    try:
        # sa_id = GetRealTimeData(ticker)
        # if sa_id == "": return []
        s = requests.Session()
        print(s)
        r1 = s.get(
            f'https://seekingalpha.com/api/v3/symbols/{ticker}',
            headers=headers,params=params)
        sa_id = r1.json()["data"]["id"]
        print(dir(r1))
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        
        print(ticker, sa_id)
        response = s.get(
            # f'https://seekingalpha.com/api/v3/symbol_data/estimates?estimates_data_items=eps_primary&group_by_month=true&period_type=quarterly&relative_periods=0%2C-1%2C-2%2C-3%2C-4%2C-5%2C-6%2C-7%2C-8%2C-9%2C-10%2C-11%2C-12%2C-13%2C-14%2C-15&return_window=120&ticker_ids={sa_id}',
            f'https://seekingalpha.com/api/v3/symbol_data/estimates?estimates_data_items=eps_primary&group_by_month=true&period_type=quarterly&relative_periods=0%2C-1%2C-2%2C-3%2C-4%2C-5%2C-6%2C-7%2C-8%2C-9%2C-10%2C-11%2C-12%2C-13%2C-14%2C-15&return_window=120&ticker_ids={sa_id}',
            headers=headers,params=params).json()
        print(response)
        data = response["estimates"][sa_id]["eps_normalized_actual"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))
        res = []
        for k, v in sorted_items:
            
            res.append([ConvertDate(v[0]["effectivedate"]),float(v[0]["dataitemvalue"])])
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    # GetDividend('NPNYY')
    GetEPS('AAPL')