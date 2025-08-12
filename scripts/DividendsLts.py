import pandas as pd
from modules.aiztradingview import GetCloseAll, GetCloseJP
from modules.dict import take
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(10)

total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()

# optionCost = 259 + 80 + 307 + 102
# optionCost = 259 + 61 + 5 + 729 + 102 + 42 
# optionCost = 4386
optionCost = 0
total_cash -= optionCost
print(total_cash)

portfolioPath = './data/DividendGainPerDay.csv'
import os
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    keepOpenList = list(df.Symbol.values)

ignoreList = ['USAC','SUN', 'BHRB', 'CTO']
closeDictUS = GetCloseAll()
closeDictJP = GetCloseJP()
portfolioDict = {}
for symbol in keepOpenList:
    if symbol in closeDictUS:
        if symbol in ignoreList: continue
        portfolioDict[symbol] = closeDictUS[symbol]
    elif symbol in closeDictJP:
        portfolioDict[symbol] = closeDictJP[symbol] * exchangeRate

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
                volLimit = 1
                if symbol in closeDictJP:
                    volLimit = 100
                if vol < volLimit:
                    total = count-1
if total < 1: total = len(portfolioDict)

print(total)
count = 0
divPortfolioDict = {}
for k, v in portfolioDict.items():
    vol = total_cash/total/v
    print(k,v,vol)
    divPortfolioDict[k] = vol
    count += 1
    if count == total: break
    if vol < 1:
        print(k,"vol < 1")
        break
print(divPortfolioDict)

divPortfolioPath = './data/divPortfolioLts.csv'
df = pd.DataFrame()
df['Symbol'] = divPortfolioDict.keys()
df['DivdendToPrice'] = divPortfolioDict.values()
df.to_csv(divPortfolioPath)

positions = ibc.GetPositions()
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