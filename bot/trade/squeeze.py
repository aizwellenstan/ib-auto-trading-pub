# rootPath = '../..'
# import sys
# sys.path.append(rootPath)
# import pandas as pd
# import os
# import modules.ib as ibc
# from modules.trade.vol import GetVolSlTp
# from modules.csvDump import LoadDict
# from modules.aiztradingview import GetSqueeze

# ibc = ibc.Ib()
# ib = ibc.GetIB(20)

# squeezeTradePath = f'{rootPath}/data/Squeeze.csv'
# squeezeTradeDict = LoadDict(squeezeTradePath,'sl')

# total_cash = ibc.GetTotalCash()
# basicPoint = 0.01

# def CheckGap(symbol):
#     shift = 0
#     contract = ibc.GetStockContract(symbol)
#     hisBarsD1 = ib.reqHistoricalData(
#         contract, endDateTime='', durationStr='2 D',
#         barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
#     if len(hisBarsD1) < 2: return False
#     if hisBarsD1[-1-shift].open>hisBarsD1[-2-shift].close:
#         return True
#     return False

# def HandleBuy(symbol, initSL):
#     # if CheckGap(symbol):
#     ask, bid = ibc.GetAskBid(symbol)
#     op = bid + 0.01
#     if op > ask - 0.01: op = ask - 0.01
#     vol, sl, tp = GetVolSlTp(symbol, total_cash, op, 'USD')
#     if sl < initSL: return 0
#     if(ask>0 and bid>0):
#         print(f"ask {ask} bid {bid}")
#         print(symbol,vol,op,sl,tp)
#         # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
#         return vol
#     return 0
        
# ignoreList = []
# passList = []
# positions = ibc.GetPositions()

# squeezeDict = GetSqueeze()

# for symbol, sl in squeezeTradeDict.items():
# # for symbol in reverseList:
#     if sl < 0.01: continue
#     if symbol in ignoreList: continue
#     if symbol in positions: continue
#     if symbol not in squeezeDict: continue
#     print('SQUEEZE',symbol, sl)
#     trade = HandleBuy(symbol, sl)
#     if trade > 0:
#         passList.append(symbol)
# print(passList)