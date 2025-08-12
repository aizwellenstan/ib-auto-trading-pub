# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
# from modules.trade.utils import GetVol

# ibc = ibc.Ib()
# ib = ibc.GetIB(12)

# total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
# print(total_cash)

# def main():
#     hourLimit = GetTradeTime()
#     contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
    
#     tfs = ['20 mins', '30 mins']
#     lastOpMap = {}
#     while(ib.sleep(10)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         t = hour * 60 + minute
#         if t < 0 * 60: 
#             print(hour, minute)
#         elif t >= 6 * 60:
#         # elif t > (hourLimit + 7) * 60:
#             print(hour, minute)
#         if hour == hourLimit + 7: continue
#         if(
#             t >= (hourLimit + 5) * 60 and
#             t < (hourLimit + 7) * 60
#         ): 
#             print("LOW VOL")
#             continue
#         tradeDict = {}
#         for tf in tfs:
#             npArr = ibc.GetDataNpArr(contractMNTPX, tf)
#             if len(npArr) < 1: continue
#             signalCheck, op, sl, tp =  ThreeBarReversal(npArr, tf, tick_val=5)

#             npArr = ibc.GetDataNpArr(contractN225MC, tf)
#             if len(npArr) < 1: continue
#             signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=5)

#             if signal == 0 or signal != signalCheck: continue

#             if signal == 1: op += 5 #one tick above topx 10.5
#             tradeDict[tf] = [signal, op, sl, tp]
#             if signal != 0: break
#         for tf, res in tradeDict.items():
#             signal, op, sl, tp = res
#             closePos = False
#             if signal != 0:
#                 msg = f'{contractN225MC.symbol} {tf} {signal} {op} {sl} {tp}'
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