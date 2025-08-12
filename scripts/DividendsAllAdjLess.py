# import pandas as pd
# from modules.aiztradingview import GetClose
# from modules.dict import take
# import modules.ib as ibc

# ibc = ibc.Ib()
# ib = ibc.GetIB(10)

# oriTotal_cash, avalible_cash = ibc.GetTotalCash()

# # optionCost = 259 + 80 + 307 + 102

# portfolioPath = './data/PortfolioRiron.csv'
# import os
# if os.path.exists(portfolioPath):
#     df = pd.read_csv(portfolioPath)
#     keepOpenList = list(df.Symbol.values)

# ignoreList = ['USAC','SUN']
# closeDict = GetClose()
# portfolioDict = {}
# for symbol in keepOpenList:
#     if symbol == "8706":
#         portfolioDict['8706'] = 465.01
#     if symbol in closeDict:
#         if symbol in ignoreList: continue
#         portfolioDict[symbol] = closeDict[symbol]

# positions = ibc.GetPositions()
# askDict = {}
# adjVal = 200
# while adjVal < 250:
#     # adjVal = 515
#     optionCost = 259 + 61 + 5 + 729 + 102 + 42 + adjVal
#     total_cash = oriTotal_cash
#     total_cash -= optionCost
#     print(total_cash)

#     total = 0
#     for i in range(0, len(keepOpenList)):
#         count = 0
#         if total > 0: break
#         for k, v in portfolioDict.items():
#             count += 1
#             if i == count:
#                 dividendList = take(count,portfolioDict)
#                 for symbol in dividendList:
#                     vol = total_cash/count/portfolioDict[symbol]
#                     if vol < 1: 
#                         total = count-1
#     if total < 1: total = len(portfolioDict)

#     print(total)
#     count = 0
#     divPortfolioDict = {}
#     for k, v in portfolioDict.items():
#         vol = total_cash/total/v
#         print(k,v,vol)
#         divPortfolioDict[k] = vol
#         count += 1
#         if count == total: break
#         if vol < 1:
#             print(k,"vol < 1")
#             break
#     print(divPortfolioDict)

#     # divPortfolioPath = './data/divPortfolioAll.csv'
#     # df = pd.DataFrame()
#     # df['Symbol'] = divPortfolioDict.keys()
#     # df['DivdendToPrice'] = divPortfolioDict.values()
#     # df.to_csv(divPortfolioPath)

#     keep = ['9101']
#     sellDict = {}

#     positionDict = {}
#     for position in positions:
#         symbol = position.contract.symbol
#         position = position.position
#         positionDict[symbol] = position
#         if symbol not in divPortfolioDict:
#             if symbol == '9101': continue
#             print(symbol, 'SELL')
#             sellDict[symbol] = position
            
#     for k, v in divPortfolioDict.items():
#         if k in positionDict:
#             if int(v) > positionDict[k]:
#                 print(k, 'BUY', v-positionDict[k])
#                 print(positionDict[k])
#             elif int(v) < positionDict[k]:
#                 print(k, 'SELL', positionDict[k]-int(v))
#                 sellDict[symbol] = positionDict[k]-int(v)
#         else:
#             print(k, 'BUY', v)
#     print(sellDict)

#     saved = 0
#     for symbol, v in sellDict.items():
#         if symbol not in askDict:
#             ask = ibc.GetAsk(symbol)
#             if ask < 0.01: cotninue
#             askDict[symbol] = ask
#         else:
#             ask = askDict[symbol]
#         saved += ask * v
#     print(saved, adjVal)
#     adjVal += 1