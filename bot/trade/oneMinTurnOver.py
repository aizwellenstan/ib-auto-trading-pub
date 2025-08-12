# import sys 
# mainFolder = '../..'
# sys.path.append(mainFolder)
# from modules.discord import Alert
# import numpy as np
# from modules.trade.vol import GetVolTp
# from modules.normalizeFloat import NormalizeFloat
# import math
# import sys
# from modules.trade.placeOrder import PlaceOrder
# import pandas as pd
# from ib_insync import *

# ib = IB()

# # IB Gateway
# # ib.connect('127.0.0.1', 4002, clientId=1)

# # TWS
# ib.connect('127.0.0.1', 7497, clientId=37)

# def GetTotalCash():
#     oriCashDf = pd.DataFrame(ib.accountValues())
#     # cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
#     # cashDf = cashDf.loc[cashDf['tag'] == 'AvailableFunds']
#     cashDf = oriCashDf.loc[oriCashDf['tag'] == 'NetLiquidationByCurrency']
#     cashDf = cashDf.loc[cashDf['currency'] == 'USD']
#     total_cash = float(cashDf['value'])
#     print(total_cash)
#     cashDf = oriCashDf.loc[oriCashDf['tag'] == 'AvailableFunds']
#     cashDf = cashDf.loc[cashDf['currency'] == 'USD']
#     avalible_cash = float(cashDf['value'])
#     print(avalible_cash)
#     return total_cash, avalible_cash

# def GetAllPositions():
#     positions = ib.positions()  # A list of positions, according to IB
#     positionList = []
#     for position in positions:
#         contract = position.contract
#         if contract.secType == 'CASH': continue
#         positionList.append(contract.symbol)
#     return positionList

# def GetNpData1m(contract):
#     data = ib.reqHistoricalData(
#             contract=contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
#             whatToShow='TRADES', useRTH=False)
#     df = pd.DataFrame(data)
#     df = df[['open','high', 'low', 'close']]
#     return df.to_numpy()

# def GetStockContract(symbol):
#     contract = Stock(symbol, 'SMART', 'USD')
#     ib.qualifyContracts(contract)
#     return contract

# def GetOptionContract(symbol, expir, strike, optType):
#     option_contract = Option(symbol, expir, strike, optType, 'SMART', tradingClass=symbol)
#     return option_contract

# def GetChains(symbol):
#     contract = GetStockContract(symbol)
#     chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
#     return chains

# def PlaceOrder(options_contract):
#     options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
#     print(options_contract)
#     # trade = ib.placeOrder(options_contract, options_order)
#     bars = ib.reqHistoricalData(
#         contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
#         whatToShow='BID', useRTH=True)
#     # limitOrder = LimitOrder('BUY', 1, lmtPrice=bars[-1].close+0.01,account=ib.wrapper.accounts[-1])
    
#     if len(bars) < 1:
#         print("ERR", options_contract)
#         return -1

#     limitOrder = Order(
#             orderType='LMT', action='BUY',
#             totalQuantity=1,
#             lmtPrice=bars[-1].close+0.01,
#             orderId=ib.client.getReqId(),
#             transmit=True,
#             outsideRth=True,
#             conditionsIgnoreRth=True,
#             tif="DAY",
#             eTradeOnly=False,
#             firmQuoteOnly=False,
#             hidden=True)

#     trade = ib.placeOrder(options_contract, limitOrder)
#     print(trade)

# total_cash, avalible_cash = GetTotalCash()
# positions = GetAllPositions()
# basicPoint = 0.01

# def CheckSignal(contract):
#     npArr = GetNpData1m(contract)
#     signal = 0
#     op = 0.0
#     sl = 0.0
#     if (
#         npArr[-4][3] > npArr[-4][0] and
#         npArr[-3][3] > npArr[-3][0] and
#         npArr[-2][3] < npArr[-2][0] and
#         npArr[-2][1] > npArr[-3][1] and
#         npArr[-2][2] <= npArr[-3][2] and
#         npArr[-2][3] < npArr[-3][0] and
#         npArr[-2][1] > npArr[-8][1]
#     ):
#         signal = -1
#         sl = npArr[-2][1]
#     elif(
#         npArr[-3][3] < npArr[-3][0] and
#         npArr[-2][1] < npArr[-3][1] and
#         npArr[-2][2] > npArr[-3][2] and not
#         (
#             npArr[-4][3] > npArr[-4][0] and
#             npArr[-3][3] < npArr[-3][0] and
#             npArr[-3][1] > npArr[-4][1] and
#             npArr[-3][2] <= npArr[-4][2] and
#             npArr[-3][3] < npArr[-4][0]
#         )
#     ):
#         signal = 1
#         sl = npArr[-2][2]
#     op = npArr[-1][3]
#     return signal,op, sl

# def scanner(contractDict, expir, strikeDict, strikeReverseDict,
#         hour, minute, sec, 
#         hourLimit, bias
#     ):

#     symbol = "QQQ"
#     contract = contractDict[symbol]
#     signal, op, sl = CheckSignal(contract)
#     print(signal, op, sl)
#     if signal > 0 and bias <= 0:
#         optType = 'C'
#         strikeList = strikeReverseDict[symbol]
#         targetStrike = 0
#         for strike in strikeList:
#             if strike <= op:
#                 targetStrike = strike
#                 break
#         option_contract = GetOptionContract(symbol, expir, strike, optType)
#         if (
#             hour == hourLimit and
#             (
#                 minute >= 30 and sec >= 5
#             ) or
#             (
#                 minute > 30
#             ) or
#             hour > hourLimit
#         ):
#             PlaceOrder(option_contract)
#             message = f"{symbol} C {op} {sl}"
#             Alert(message)
#         bias = 1
#     elif signal < 0 and bias >= 0:
#         optType = 'P'
#         strikeList = strikeDict[symbol]
#         targetStrike = 0
#         for strike in strikeList:
#             if strike >= op:
#                 targetStrike = strike
#                 break
#         option_contract = GetOptionContract(symbol, expir, strike, optType)
#         if (
#             hour == hourLimit and
#             (
#                 minute >= 30 and sec >= 5
#             ) or
#             (
#                 minute > 30
#             ) or
#             hour > hourLimit
#         ):
#             PlaceOrder(option_contract)
#             message = f"{symbol} P {op} {sl}"
#             Alert(message)
#         bias = -1

#     return bias
    
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
#     symbolList = ["QQQ", "SPY"]
#     init()
#     contractDict = {}
#     shift = 0
#     expir = ""
#     strikeDict = {}
#     strikeReverseDict = {}
#     for symbol in symbolList:
#         contract = GetStockContract(symbol)
#         contractDict[symbol] = contract
#         chains = GetChains(symbol)
#         for chain in chains:
#             expir=chain.expirations[1]
#             strikeDict[symbol] = chain.strikes
#             strikeReverseDict[symbol] = chain.strikes[::-1]
#             break
    
#     print(expir)
#     bias = 0
#     while(ib.sleep(1)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         sec = currentTime.second
#         bias = scanner(contractDict, expir, strikeDict,
#             strikeReverseDict,
#             hour, minute, sec, hourLimit, bias)
#         print('tick')
#         if dayLightSaving:
#             if(hour == 13 and minute == 51 and sec == 0):
#                 shutDown()
#         else:
#             if(hour == 14 and minute == 51 and sec == 0):
#                 shutDown()

# if __name__ == '__main__':
#     main()