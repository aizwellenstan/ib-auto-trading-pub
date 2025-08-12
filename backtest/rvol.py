import sys
sys.path.append('../')
from modules.aiztradingview import GetVol, GetPreVol, GetShares, GetMarketCap
import pandas as pd

volDict = GetVol('USD')
sharesDict = GetShares('USD')
marketcapDict = GetMarketCap()

# PreMarketVolume
# DWAC 34264405
# PHUN 139606054
# BKKT 5780083
# PTPI 613575

preVolDict = {}
preVolDict['DWAC'] = 34264405
preVolDict['PHUN'] = 139606054
preVolDict['BKKT'] = 5780083
preVolDict['PTPI'] = 613575

limit = 0.0001289803

for key in preVolDict:
    rvol = preVolDict[key] / marketcapDict[key]
    if rvol < limit: continue
    print(key,'{0:.10f}'.format(rvol))

preVolDict = GetPreVol('USD')
symList = ['NCLH','CCL','ALZN']

for key in symList:
    rvol = preVolDict[key] / marketcapDict[key]
    if rvol < limit: continue
    print(key,'{0:.10f}'.format(rvol))

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]

shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
first_table = payload[0]
second_table = payload[1]
df = first_table
sp500symbols = df['Symbol'].values.tolist()

for sym in symList:
    if sym in shortableSymList:
        if sym in sp500symbols: continue
        print(sym,"faq")

symbols = ['DWAC','PHUN','BKKT','PTPI','ALZN']
for sym in symbols:
    if sym in shortableSymList:
        print(sym)