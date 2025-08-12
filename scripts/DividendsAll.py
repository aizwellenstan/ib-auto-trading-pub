import pandas as pd
from modules.aiztradingview import GetClose
from modules.dict import take
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(10)

total_cash, avalible_cash = ibc.GetTotalCash()

# optionCost = 259 + 80 + 307 + 102
optionCost = 259 + 61 + 5 + 729 + 102 + 42 
# optionCost = 4386
total_cash -= optionCost
print(total_cash)

portfolioPath = './data/PortfolioRiron.csv'
import os
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    keepOpenList = list(df.Symbol.values)

ignoreList = ['USAC','SUN']
closeDict = GetClose()
portfolioDict = {}
for symbol in keepOpenList:
    if symbol == "8706":
        portfolioDict['8706'] = 456
    if symbol == "8624":
        portfolioDict['8624'] = 457
    if symbol in closeDict:
        if symbol in ignoreList: continue
        portfolioDict[symbol] = closeDict[symbol]

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

divPortfolioPath = './data/divPortfolioAll.csv'
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
        # elif int(v) < positionDict[k]:
        #     print(k, 'SELL', positionDict[k]-int(v))
    else:
        print(k, 'BUY', v)