from modules.data import GetNpData
from modules.aiztradingview import GetClose
from modules.dict import take
import pandas as pd
from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=11)

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
total_cash = float(cashDf['value'])
print(total_cash)

# optionCost = 259 + 80 + 307 + 102
# optionCost = 900
optionCost = 4386
total_cash -= optionCost
print(total_cash)

catNpArr = GetNpData('CAT')

buy = False
if catNpArr[-1][3] > catNpArr[-2][3] * 1.05:
    print('BUY TSLA')
    buy = True
elif catNpArr[-1][3] < catNpArr[-2][3] * (1 - 0.05):
    print('SELL TSLA')

if buy:
    keepOpenList = ['TSLA', 'NVDA', 'AVGO', 'QCOM', 'MS', 'DE', 'AAPL', 'BN', 'NKE', 'GOOG', 'BNS', 'MSFT', 'WFC',
    'TD', 'PM', 'BA', 'LOW', 'UPS', 'RY', 'ABBV', 'BAC', 'BRK.A', 'TXN', 'DUK', 'LIN', 'BRK.B',
    # 'JPM', 'MA',
    # 'HD', 'GS', 'DHR', 'LLY', 'COST', 'CAT', 'KO', 'XOM', 'RTX', 'TMO', 'ADBE', 'ACN', 'MCD', 'ORCL', 'UNP',
    # 'TMUS', 'PG', 'ELV', 'V', 'CMCSA',
    # 'IBM', 'UNH', 'C', 'CVS', 'AMZN', 'CSCO', 'CVX', 'PEP', 'NEE', 'CHTR', 'META', 'AMT', 'CRM', 'BMY', 'TBB', 'TBC', 'DIS', 'MRK', 'DUKB', 'VZ', 'WMT', 'T'
    ]

    closeDict = GetClose()
    portfolioDict = {}
    for symbol in keepOpenList:
        if symbol in closeDict:
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

    divPortfolioPath = './data/largeCapPortfolioAll.csv'
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