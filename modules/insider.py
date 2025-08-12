import requests
import json
import pandas as pd
import numpy as np

# Request for data from Finhub.io (30 calls per second limit: https://finnhub.io/docs/api/rate-limit).
apikey = 'c8i9ncaad3iearbu5ibg'

def GetInsider(symbol :str):
    try:
        r = requests.get('https://finnhub.io/api/v1/stock/insider-transactions?symbol='+symbol+'&token='+apikey)

        # Load the JSON file as a string.
        test = json.loads(r.text)

        df = pd.DataFrame(data=test['data'])

        # Derived attributes from the data.
        df['dollarAmount'] = df['change']*df['transactionPrice']
        df['insiderPortfolioChange'] = df['change']/(df['share'] - df['change'])

        # print(type(df['transactionPrice'][0]))
        conditions = [
            (df['change'] >= 0) & (df['transactionPrice'] > 0),
            (df['change'] <= 0) & (df['transactionPrice'] > 0),
            (df['transactionPrice'] == 0)
        ]
        values = ['Buy', 'Sale', 'Gift']
        df['buyOrSale'] = np.select(conditions, values)

        df = df.set_index('filingDate')
        df = df[['dollarAmount']]
        
        return df
    except:
        return pd.DataFrame()

def CheckInsider(symbol :str):
    insider = GetInsider(symbol)
    if len(insider>1):
        dollarAmount = insider['dollarAmount'].sum()
        if dollarAmount < -195470587: return False
    return True

# insider = GetInsider('CLOV')
# mask = insider.index < str('2021-06-08')
# insider = insider.loc[mask]
# print(insider)