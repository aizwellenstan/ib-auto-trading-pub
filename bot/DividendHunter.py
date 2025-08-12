rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetDivivdendHunter
from modules.dividendCalendar import GetExDividendNp
import pandas as pd
import os

from modules.numpyLookup import LookUp

# https://www.nasdaq.com/market-activity/dividends
npArr = GetExDividendNp(1)
print(npArr)
closeDict = GetDivivdendHunter()
portfolioDict = {}
try:
    symbols = npArr[:,0]
    dividendDict = {}
    for symbol in symbols:
        if symbol not in closeDict: continue
        div = LookUp(npArr, symbol, 0)[1]
        print(symbol, div)
        close = closeDict[symbol]
        dividendToPrice = div/close
        if dividendToPrice < 0.07: continue
        portfolioDict[symbol] = dividendToPrice
        dividendDict[symbol] = div
except: pass

portfolioDict = dict(sorted(portfolioDict.items(), key=lambda item: item[1], reverse=True))
print(portfolioDict)
portfolioList = list(portfolioDict.keys())
print(portfolioList)

resDict = {}
for symbol in portfolioList:
    resDict[symbol] = dividendDict[symbol]

exDividendPath = f'{rootPath}/data/ExDividend.csv'
# if len(resDict) > 0:
df = pd.DataFrame()
df['Symbol'] = resDict.keys()
df['Divdend'] = resDict.values()
df.to_csv(exDividendPath)
