import pandas as pd
from modules.aiztradingview import GetProfitableCloseJP, GetProfitableClose
from modules.dict import take
import modules.ib as ibc
import yfinance as yf
from modules.trade.vol import GetVolSlTp

ibc = ibc.Ib()
ib = ibc.GetIB(10)

total_cash, avalible_cash = ibc.GetTotalCash()

# optionCost = 259 + 80 + 307 + 102
# optionCost = 259 + 61 + 5 + 729 + 102 + 42
optionCost = 0
# optionCost = 4386
total_cash -= optionCost
print(total_cash)

def floor_to_nearest_100(number):
    return (number // 100) * 100

# portfolioPath = './data/Sharpe.csv'
# import os
# if os.path.exists(portfolioPath):
#     df = pd.read_csv(portfolioPath)
#     keepOpenList = list(df.Symbol.values)

# ticker = "USDJPY=X"
# usdjpy = yf.Ticker(ticker).history(period="1d")["Close"][-1]

# closeDictJP = GetProfitableCloseJP()
# closeDict = GetProfitableClose()
# portfolioDict = {}
# for symbol in keepOpenList:
#     if symbol in closeDictJP:
#         portfolioDict[symbol] = closeDictJP[symbol]/usdjpy
#     if symbol in closeDict:
#         portfolioDict[symbol] = closeDict[symbol]

# total = 0
# for i in range(0, len(keepOpenList)):
#     count = 0
#     if total > 0: break
#     for k, v in portfolioDict.items():
#         count += 1
#         if i == count:
#             dividendList = take(count,portfolioDict)
#             for symbol in dividendList:
#                 vol = int(total_cash/count/portfolioDict[symbol])
#                 volLimit = 1
#                 if symbol in closeDictJP: 
#                     volLimit = 100
#                     vol = floor_to_nearest_100(vol)
#                 if vol < volLimit: 
#                     total = count-1
# if total < 1: total = len(portfolioDict)

# print("total",total)
# count = 0
# sharpePortfolioDict = {}
# for symbol, v in portfolioDict.items():
#     vol = int(total_cash/total/v)
#     if symbol in closeDictJP:
#         v = closeDictJP[symbol]
#         vol = floor_to_nearest_100(vol)
#     print(symbol,v,vol)
#     sharpePortfolioDict[symbol] = vol
#     count += 1
#     if count == total: break
#     if vol < 1:
#         print(symbol,"vol < 1")
#         break
# print("sharpePortfolioDict",sharpePortfolioDict)

# divPortfolioPath = './data/sharpePortfolioAll.csv'
# df = pd.DataFrame()
# df['Symbol'] = sharpePortfolioDict.keys()
# df['DivdendToPrice'] = sharpePortfolioDict.values()
# df.to_csv(divPortfolioPath)

# positions = ibc.GetPositions()
# positionDict = {}
# for position in positions:
#     symbol = position.contract.symbol
#     position = position.position
#     positionDict[symbol] = position
#     if symbol not in sharpePortfolioDict:
#         print(symbol, 'SELL')
    
# tradeDict = {}
# for symbol, v in sharpePortfolioDict.items():
#     if symbol in positionDict:
#         if int(v) > positionDict[symbol]:
#             print(symbol, 'BUY', v-positionDict[symbol])
#             tradeDict[symbol] = v
#             print(positionDict[symbol])
#         elif int(v) < positionDict[symbol]:
#             print(k, 'SELL', positionDict[symbol]-int(v))
#     else:
#         print(symbol, 'BUY', v)
#         tradeDict[symbol] = v

basicPoint = 0.01
def HandleBuy(symbol):
    ask, bid = ibc.GetAskBid(symbol)
    # op = bid + 0.01
    op = 29.95
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    print(vol)
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        ibc.HandleBuyLimitFree(symbol,vol,op,sl,tp,basicPoint)

# netIncome > 2000
# HandleBuy("RGTI")
# HandleBuy("AKLI")
HandleBuy('INTC')