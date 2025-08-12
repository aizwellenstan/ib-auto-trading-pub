import pandas as pd
from modules.aiztradingview import GetClose
from modules.dict import take
from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=8)

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
total_cash = float(cashDf['value'])
print(total_cash)

# optionCost = 259 + 80 + 307 + 102
# optionCost = 259 + 61
optionCost = 4386
total_cash -= optionCost

portfolioPath = './data/GapFast.csv'
import os
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    keepOpenList = list(df.Symbol.values)

closeDict = GetClose()
portfolioDict = {}
for symbol in keepOpenList:
    try:
        portfolioDict[symbol] = closeDict[symbol]
    except:
        continue

total = 0
for i in range(0, len(keepOpenList)):
    count = 0
    if total > 0: break
    for k, v in portfolioDict.items():
        count += 1
        if i == count:
            dividendList = take(count,portfolioDict)
            for symbol in dividendList:
                vol = total_cash/count/portfolioDict[symbol]
                if vol < 1: 
                    total = count-1
        # vol = total_cash/count/v
        # print(k,vol)
        # if count == i: break
        # if vol < 1: 
        #     total = count-2
        #     break

if total < 1:
    total = len(keepOpenList)
if total < 8:
    total = 8

print(total)
count = 0
divPortfolioDict = {}
for k, v in portfolioDict.items():
    if v < 1: continue
    vol = total_cash/total/v
    print(k,v,vol)
    divPortfolioDict[k] = vol
    count += 1
    if count == total: break
    if vol < 1:
        print(k,"vol < 1")
        break
print(divPortfolioDict)

# divPortfolioPath = './data/divPortfolio.csv'
# df = pd.DataFrame()
# df['Symbol'] = divPortfolioDict.keys()
# df['DivdendToPrice'] = divPortfolioDict.values()
# df.to_csv(divPortfolioPath)

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