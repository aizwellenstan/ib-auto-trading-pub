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

# total_cash, avalible_cash = ibc.GetTotalCash()
# basicPoint = 0.01

# def CheckSignal():
#     symbol = 'QQQ'
#     contract = ibc.GetStockContract(symbol)
#     hisBarsD1 = ib.reqHistoricalData(
#         contract, endDateTime='', durationStr='2 D',
#         barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
#     if len(hisBarsD1) < 2: return False
#     if hisBarsD1[-2].close>hisBarsD1[-2].open*1.0015:
#         return True
#     return False

# def HandleBuy(symbol):
#     # if CheckGap(symbol):
#     ask, bid = ibc.GetAskBid(symbol)
#     op = bid + 0.01
#     if op > ask - 0.01: op = ask - 0.01
#     vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
#     if vol < 26: return 0
#     if(ask>0 and bid>0):
#         print(f"ask {ask} bid {bid}")
#         print(symbol,vol,op,sl,tp)
#         ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
#         return vol
#     return 0
        
# ignoreList = []
# passList = []
# positions = ibc.GetPositions()

# # squeezeDict = GetSqueeze()

# symbol = 'HROW'
# if CheckSignal():
#     if symbol not in positions:
#         trade = HandleBuy(symbol)
#         print('Buy',symbol)