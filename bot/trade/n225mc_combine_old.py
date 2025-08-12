# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.strategy.threeBarPlay import ThreeBarPlay
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
# from modules.trade.utils import GetVol

# ibc = ibc.Ib()
# ib = ibc.GetIB(19)

# total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
# print(total_cash)
# total_cash /= exchangeRate

# def main():
#     MIN_VOL = 1
#     hourLimit = GetTradeTime()
#     contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
#     tfs = ['5 mins']
#     lastOpMap = {}
#     while(ib.sleep(2)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         t = hour * 60 + minute
#         if hour == hourLimit + 7: continue
#         tradeDict = {}
#         for tf in tfs:
#             npArrSignal = ibc.GetDataNpArr(contractMES, tf)
#             if len(npArrSignal) < 1: continue
#             sType = ""
#             signal, op, sl, tp = ThreeBarReversal(npArrSignal, tf, tick_val=0.25)
#             if signal != 0: sType = "THREE BAR REVERSAL MES"
#             if signal == 0: 
#                 signal, op, sl, tp = ThreeBarPlay(npArrSignal, tf, tick_val=0.25)
#                 if signal == 0: continue
#                 if signal != 0: sType = "THREE BAR PLAY MES"
#             if signal != 0:
#                 npArr = ibc.GetDataNpArr(contractN225MC, tf)
#                 if len(npArr) < 1: continue
#                 op, sl, tp = GetOPSLTP(npArr, signal, tf, 1)
#                 tradeDict[tf] = [signal, op, sl, tp, sType]
#         for tf, res in tradeDict.items():
#             signal, op, sl, tp, sType = res
#             closePos = False
#             if signal != 0:
#                 msg = f'{sType} {contractN225MC.symbol} {tf} {signal} {op} {sl} {tp}'
#                 vol = 1
#                 trades = ibc.GetOpenTrades()
#                 for trade in trades:
#                     if trade.contract == contractN225MC:
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
#                 if tf not in lastOpMap or op != lastOpMap[tf]:
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 10, 'JPY')
#                     if vol < MIN_VOL: continue
#                     ExecTrade(ibc, signal, contractN225MC, vol, op, sl, tp, closePos, True)
#                     Alert(msg)
#                     lastOpMap[tf] = op
#                 else:
#                     print(msg)
#         print(contractN225MC.symbol)

# if __name__ == '__main__':
#     main()