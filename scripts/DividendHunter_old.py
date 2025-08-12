import pandas as pd
from modules.aiztradingview import GetClose
from modules.dict import take
from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=10)

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
total_cash = float(cashDf['value'])
print(total_cash)

# optionCost = 259 + 80 + 307 + 102
# optionCost = 259 + 61 + 5 + 729 + 102
optionCost = 4386
total_cash -= optionCost
total_cash /= 2

# https://www.nasdaq.com/market-activity/dividends
portfolioPath = './data/ExDividend.csv'
import os
dividendDict = {}
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    dividendDict = df.set_index('Symbol').Divdend.to_dict()
closeDict = GetClose()
portfolioDict = {}
for symbol, div in dividendDict .items():
    if symbol in closeDict:
        portfolioDict[symbol] = closeDict[symbol]

total = 0
for i in range(0, len(dividendDict)):
    count = 0
    if total > 0: break
    for k, v in portfolioDict.items():
        count += 1
        if i == count:
            dividendList = take(count,portfolioDict)
            for symbol in dividendList:
                vol = int(total_cash/count/portfolioDict[symbol])
                div = dividendDict[symbol] * vol
                if vol < 1 or div < 2: 
                    total = count-1

print(total)
count = 0
divPortfolioDict = {}
for symbol, v in portfolioDict.items():
    vol = int(total_cash/total/v)
    div = dividendDict[symbol] * vol
    if div < 2:
        print(div,"div < 2")
        break
    print(symbol,v,vol)
    divPortfolioDict[symbol] = vol
    count += 1
    if count == total: break
    if vol < 1:
        print(symbol,"vol < 1")
        break
print(divPortfolioDict)

divPortfolioPath = './data/portfolioExDividend.csv'
df = pd.DataFrame()
df['Symbol'] = divPortfolioDict.keys()
df['DivdendToPrice'] = divPortfolioDict.values()
df.to_csv(divPortfolioPath)

positions = ib.positions()
positionDict = {}
for position in positions:
    symbol = position.contract.symbol
    position = position.position
    positionDict[symbol] = position
    if symbol not in divPortfolioDict:
        print(symbol, 'SELL')
        
for k, v in divPortfolioDict.items():
    if k in positionDict:
        if int(v) > positionDict[k]:
            print(k, 'BUY', v-positionDict[k])
            print(positionDict[k])
    else:
        print(k, 'BUY', v)