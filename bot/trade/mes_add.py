# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import pandas as pd
# import numpy as np
# from ib_insync import *
# from modules.strategy.threeBarReversal import ThreeBarReversal
# from modules.discord import Alert
# import modules.ib as ibc

# ibc = ibc.Ib()
# ib = ibc.GetIB(1)

# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=11)

# def ConvertTenMin(df):
#     df.set_index('date', inplace=True)  # Set timestamp as index
#     df = df.resample('10min').apply({
#         'open': 'first',
#         'high': 'max',
#         'low': 'min',
#         'close': 'last'
#     })
#     try:
#         df = df[['open','high','low','close']]
#     except: return []
#     return df

# cache5min = pd.DataFrame()
# def GetData(contract, tf, update5m=False):
#     global cache5min
#     if tf not in ['10m']:
#         data = ib.reqHistoricalData(
#             contract, endDateTime='', durationStr='2 D',
#             barSizeSetting=tf, whatToShow='ASK', useRTH=False)
#         df = pd.DataFrame(data)
#         if tf in ['5 mins']:
#             cache5min = df
#         try:
#             df = df[['open','high','low','close']]
#         except: return []
#         return df.to_numpy()
#     else:
#         if update5m:
#             data = ib.reqHistoricalData(
#             contract, endDateTime='', durationStr='2 D',
#             barSizeSetting='5 mins', whatToShow='ASK', useRTH=False)
#             df = pd.DataFrame(data)
#             cache5min = df
#         df = ConvertTenMin(cache5min)
#         if np.isnan(df.to_numpy()).any():
#             data = ib.reqHistoricalData(
#             contract, endDateTime='', durationStr='1 D',
#             barSizeSetting='5 mins', whatToShow='ASK', useRTH=False)
#             df = pd.DataFrame(data)
#             cache5min = df
#     try:
#         df = df[['open','high','low','close']]
#     except: return []
#     return df.to_numpy()

# def execTrades(tradeList):
#     for c in tradeList:
#         options_contract = Option(c[0], c[1], c[2], c[3], 'SMART', tradingClass=c[0])
#         print(options_contract)
#         PlaceOrder(ib, options_contract)

# def ExecTrade(signal, contract, vol, op, sl, tp, closePos):
#     trades = 0
#     positions = ib.positions()  # A list of positions, according to IB
#     if signal > 0:
#         # for position in positions:
#         #     if (
#         #         position.contract == contract and
#         #         position.position > 0
#         #     ): trades += 1
#         # if trades < 1:
#         ibc.HandleBuyLimitTpWithContract(
#             contract, vol, op, sl, tp, closePos)
#         # else:
#         #     Alert(f'alerady have {signal} in {contract.symbol}')
#     elif signal < 0:
#         # for position in positions:
#         #     if (
#         #         position.contract == contract and
#         #         position.position < 0
#         #     ): trades += 1
#         # if trades < 1:
#         ibc.HandleSellLimitTpWithContract(
#             contract, vol, op, sl, tp, closePos)
#         # else:
#         #     Alert(f'alerady have {signal} in {contract.symbol}')

# def main():
#     dayLightSaving = True
#     if dayLightSaving:
#         hourLimit = 13
#     else:
#         hourLimit = 14

#     # positions = ib.positions()  # A list of positions, according to IB
#     # for position in positions:
#     #     contract = position.contract
#     #     print(contract)
#     # sys.exit()

#     contract = Future(conId=637533398, symbol='MES', lastTradeDateOrContractMonth='20240920', multiplier='5', currency='USD', localSymbol='MESU4', tradingClass='MES')
#     ib.qualifyContracts(contract)
#     contractCheck = Future(conId=637533593, symbol='MNQ', lastTradeDateOrContractMonth='20240920', multiplier='2', currency='USD', localSymbol='MNQU4', tradingClass='MNQ')
#     ib.qualifyContracts(contractCheck)
#     # contract = Future(conId=618688988, symbol='N225M', lastTradeDateOrContractMonth='20240912', multiplier='100', currency='JPY', localSymbol='169090019', tradingClass='225M')
#     # ib.qualifyContracts(contract)
#     # contract = Stock('QQQ', 'SMART', 'USD')
#     # ib.qualifyContracts(contract)

#     # ExecTrade(1, contract, 1, 400, 399, 7000)
#     # ib.sleep(2)

    
#     tfs = ['5 mins', '10 mins']
#     lastOpMap = {}
#     # while(ib.sleep(2)):
#     currentTime = ib.reqCurrentTime()
#     hour = currentTime.hour
#     minute = currentTime.minute
#     t = hour * 60 + minute
#     restrict = False
#     if t < hourLimit * 60 + 30: 
#         print(hour, minute)
#         restrict = True
#     elif t >= (hourLimit + 2) * 60:
#     # elif t > (hourLimit + 7) * 60:
#         print(hour, minute)
#         restrict = True
#     if not restrict:
#         tfs = ['5 mins', '10 mins', '10m']
#     else:
#         tfs = ['10 mins', '10m']
#     tradeDict = {}
#     for tf in tfs:
#         if not restrict:
#             npArr = GetData(contract, tf)
#             if len(npArr) < 1: continue
#             signal, op, sl, tp = ThreeBarReversal(npArr, 0.25)
#             if signal == 0: continue
#             break
#         else:
#             npArr = GetData(contractCheck, tf, True)
#             if len(npArr) < 1: continue
#             signalCheck, op, sl, tp = ThreeBarReversal(npArr, 0.25)
#             npArr = GetData(contract, tf, True)
#             if len(npArr) < 1: continue
#             signal, op, sl, tp = ThreeBarReversal(npArr, 0.25)
#             if signal == 0: continue
#             if signalCheck != signal: continue
#         tradeDict[tf] = [signal, op, sl, tp]
#     for tf, res in tradeDict.items():
#         signal, op, sl, tp = res
#         closePos = False
#         if signal != 0:
#             msg = f'{contract.symbol} {tf} {signal} {op} {sl} {tp}'
#             vol = 1
#             # trades = ibc.GetOpenTrades()
#             # for trade in trades:
#             #     if trade.contract == contract:
#             #         if trade.order.action == 'BUY':
#             #             if signal > 0:
#             #                 print(f'Pending BUY Order {trade.contract.symbol}')
#             #                 continue
#             #             elif signal < 0:
#             #                 closePos = True
#             #         elif trade.order.action == 'SELL':
#             #             if signal < 0:
#             #                 print(f'Pending SELL Order {trade.contract.symbol}')
#             #                 continue
#             #             elif signal > 0:
#             #                 closePos = True
#             if tf not in lastOpMap:
#                 ExecTrade(signal, contract, vol, op, sl, tp, False)
#                 Alert(msg)
#                 lastOpMap[tf] = op
#             elif op != lastOpMap[tf]:
#                 ExecTrade(signal, contract, vol, op, sl, tp, False)
#                 Alert(msg)
#                 lastOpMap[tf] = op
#             else:
#                 print(msg)
#     print(contract.symbol)
                
#     # trade = 0
#     # while(ib.sleep(2)):
#     #     currentTime = ib.reqCurrentTime()
#     #     hour = currentTime.hour
#     #     minute = currentTime.minute
#     #     second = currentTime.second
#     #     # if(hour == hourLimit and minute >= 30 and sec >= 5):
#     #     #     execTrades(tradeList)
#     #     #     break
#     #     print(hour,minute,second)
#     #     execTrades(tradeList)
#     #     break

# if __name__ == '__main__':
#     main()