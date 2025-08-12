# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrailMOC
# from modules.strategy.vwap import GetVwapStrategy
# from modules.trade.utils import GetVol
# from ib_insync import *

# ibc = ibc.Ib()
# ib = ibc.GetIB(15)

# total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
# print(total_cash)
# total_cash /= exchangeRate

# def GetContractDict(symbolList):
#     contractDict = {}
#     cfdContractDict = {}
#     for symbol in symbolList:
#         contract = Stock(symbol, 'TSEJ', 'JPY')
#         ib.qualifyContracts(contract)
#         contractDict[symbol] = contract
#         contract = CFD(symbol, 'SMART', 'JPY')
#         ib.qualifyContracts(contract)
#         cfdContractDict[symbol] = contract
#     return contractDict, cfdContractDict

# def main():
#     MIN_VOL = 100
#     import pandas as pd
#     df = pd.read_csv("cfd_vwap_jp.csv")
#     df.columns = ["i","symbol"]
#     symbolList = df["symbol"].values.tolist()
#     symbolDict = {"6315":1}
#     for symbol in symbolList:
#         symbolDict[symbol] = 1
#     print(symbolDict)
#     contractDict, cfdContractDict = GetContractDict(list(symbolDict.keys()))
#     hourLimit = GetTradeTime()
#     tf = '5 mins'
#     lastOpMap = {}
#     while(ib.sleep(60)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         tradeDict = {}
#         for symbol, contract in contractDict.items():
#             npArr = ibc.GetDataNpArr(contract, tf)
#             if len(npArr) < 1: continue
#             signal, op, sl, tp = GetVwapStrategy(npArr, tick_val=1)
#             print(cfdContractDict[symbol].symbol)
#             if signal == 0: continue
#             bias = symbolDict[symbol]
#             if bias != 0:
#                 if signal != bias: continue
#             tradeDict[symbol] = [signal, op, sl, tp]
#         for symbol, res in tradeDict.items():
#             signal, op, sl, tp = res
#             closePos = False
#             if signal != 0:
#                 msg = f'VWAP {cfdContractDict[symbol].symbol} {tf} {signal} {op} {sl} {tp}'
#                 vol = 100
#                 trades = ibc.GetOpenTrades()
#                 for trade in trades:
#                     if trade.contract == cfdContractDict[symbol]:
#                         if trade.order.action == 'BUY':
#                             if signal > 0:
#                                 print(f'Pending BUY Order {trade.contract.symbol}')
#                                 continue
#                             elif signal < 0:
#                                 closePos = True
#                         elif trade.order.action == 'SELL':
#                             if signal < 0:
#                                 print(f'Pending SELL Order {trade.contract.symbol}')
#                                 continue
#                             elif signal > 0:
#                                 closePos = True
#                 if symbol not in lastOpMap or op != lastOpMap[symbol]:
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1, 'JPY')
#                     print(symbol, vol)
#                     if vol < MIN_VOL: continue
#                     ExecTrailMOC(ibc, signal, cfdContractDict[symbol], vol, op, sl, tp, closePos)
#                     Alert(msg)
#                     lastOpMap[symbol] = op
#                 else:
#                     print(msg)
            

# if __name__ == '__main__':
#     main()