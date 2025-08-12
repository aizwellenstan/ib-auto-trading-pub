import requests
import pandas as pd
import os
FMP_API_KEY = os.environ["FMP_API_KEY"] 

s = requests.Session()
def GetCashFlow(symbol):
    response = s.get(
        f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?period=annual&apikey={FMP_API_KEY}')
    res = response.json()
    df = pd.DataFrame(res)
    df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
    df.set_index('date', inplace=True)
    return df

if __name__ == '__main__':
    cashFlow = GetCashFlow("AAPL")
    print(cashFlow)