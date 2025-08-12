# import sys 
# mainFolder = '../../'
# sys.path.append(mainFolder)
# import datetime as dt
# from modules.expir import GetExpir
# from modules.discord import Alert
# import os
# import pandas as pd
# import numpy as np
# from modules.trade.placeOrder import PlaceOrder
# import modules.ib as ibc
# from modules.trade.vol import GetVolSlTp
# from modules.normalizeFloat import NormalizeFloat

# ibc = ibc.Ib()
# ib = ibc.GetIB(25)
# total_cash, avalible_cash = ibc.GetTotalCash()
# basicPoint = 0.01

# def HandleBuyOption(symbol, chains, tp):
#     for optionschain in chains:
#         strikeList = optionschain.strikes
#         for strike in strikeList:
#             if strike > tp:
#                 optionContract = ibc.GetOptionCallContract(symbol, optionschain.expirations[1], strike)
#                 positions = ibc.GetAllPositions()
#                 if symbol not in positions:
#                     PlaceOrder(ib, optionContract)
#                 message = symbol+' M 1OTM C TP: '+str(tp)
#                 Alert(message)
#                 print(message)
#                 return 1
#     return 0

# def HandleBuy(symbol, target):
#     ask, bid = ibc.GetAskBid(symbol)
#     op = bid + 0.01
#     if op > ask - 0.01: op = ask - 0.01
#     vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
#     if (target - op) * vol < 2: return 1
#     if(ask>0 and bid>0):
#         target = NormalizeFloat(target, basicPoint)
#         print(f"ask {ask} bid {bid}")
#         print(symbol,vol,op,sl,target)
#         positions = ibc.GetAllPositions()
#         if symbol not in positions:
#             ibc.HandleBuyLimit(symbol,vol,op,sl,target,basicPoint)
#         return vol
#     return 1

# def scanner(retraceDict, contractDict, hour, minute, sec, 
#     hourLimit, chainsDict, previousCloseDict, tradeDict
#     ):

#     signalSymbol = "KO"
#     symbol = "PEP"
#     signalContract = contractDict[signalSymbol]
#     signalBid = ibc.GetBidByContract(signalContract)

#     if signalBid > previousCloseDict[signalSymbol]:
#         contract = contractDict[symbol]
#         ask = ibc.GetAskByContract(contract)
#         previousClose = previousCloseDict[symbol]
#         if ask < previousClose:
#             retraceVal = retraceDict[symbol]
#             tp = ask + (previousClose - ask) * retraceVal
    
#             if hour == hourLimit and minute >= 30 and sec >= 5:
#                 trade = HandleBuy(symbol, tp)
#                 if trade > 0:
#                     tradeDict[symbol] = trade

#     return tradeDict
    
# def init():
#     message = "Only Trade Discord Alert!!"
#     Alert(message)

# def shutDown():
#     message = "SHUT DOWN, GET GREEN GET OUT"
#     Alert(message)
#     print(message)

# def main():
#     dayLightSaving = True
#     if dayLightSaving:
#         hourLimit = 13
#     else:
#         hourLimit = 14
#     retraceDict = {
#         "KO": 0,
#         "PEP": 0.98
#     }
#     init()
#     contractDict = {}
#     chainsDict = {}
#     previousCloseDict = {}
#     shift = 0
#     for symbol, target in retraceDict.items():
#         contract = ibc.GetStockContract(symbol)
#         contractDict[symbol] = contract
#         chainsDict[symbol] = ibc.GetChains(symbol)
#         previousCloseDict[symbol] = ibc.GetData1D(contract)[-1-shift].close
#     tradeDict = {}
#     while(ib.sleep(1)):
#         hour = ib.reqCurrentTime().hour
#         minute = ib.reqCurrentTime().minute
#         sec = ib.reqCurrentTime().second
#         tradeDict = scanner(retraceDict, contractDict, 
#             hour, minute, sec, hourLimit, 
#             chainsDict, previousCloseDict, tradeDict)
#         print('tick')
#         if dayLightSaving:
#             if(hour == 13 and minute == 51 and sec == 0):
#                 shutDown()
#         else:
#             if(hour == 14 and minute == 51 and sec == 0):
#                 shutDown()

# if __name__ == '__main__':
#     main()