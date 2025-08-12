# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
# from modules.orderblocks import GetOrderBlocks

# ibc = ibc.Ib()
# ib = ibc.GetIB(14)

# def main():
#     hourLimit = GetTradeTime()
#     contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMGC = GetFuturesContracts(ib)
#     npArr = ibc.GetDataNpArr(contractMES, '5 mins')

#     ob = GetOrderBlocks(npArr)
#     print(ob)
#     sys.exit()
#     tfs = ['5 mins', '10 mins']
#     lastOpMap = {}
#     while(ib.sleep(2)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         t = hour * 60 + minute
#         restrict = False
#         if t < hourLimit * 60 + 30: 
#             print(hour, minute)
#             restrict = True
#         elif t >= (hourLimit + 2) * 60:
#         # elif t > (hourLimit + 7) * 60:
#             print(hour, minute)
#             restrict = True
        
#         # RTH 22:30 - 06:00 JST
#         # LOV VOL 03:50 - 06:00 JST
#         if(
#             t < hourLimit * 60 + 30 or
#             # t >= (hourLimit + 7) * 60
#             t >= (hourLimit + 5) * 60
#         ): 
#             if t >= (hourLimit + 8) * 60:
#                 print("OUTSIDE RTH")
#                 print(f"START: {hourLimit}:30")
#                 print(f"END: {hourLimit + 8}:00")
#             else:
#                 print("LOW VOL")
#             continue
#         if hour == hourLimit + 7: continue
#         if not restrict:
#             tfs = ['5 mins', '10 mins']
#         else:
#             tfs = ['10 mins']
#         tradeDict = {}
#         for tf in tfs:
#             if not restrict:
#                 npArr = ibc.GetDataNpArr(contractMES, tf)
#                 if len(npArr) < 1: continue
#                 signal, op, sl, tp = ThreeBarReversal(npArr)
#                 if signal == 0: 
#                     if tf in ['10 mins']:
#                         try:
#                             npArr225 = ibc.GetDataNpArr(contractN225M, tf)
#                             if len(npArr) > 1:
#                                 signalN225, op, sl, tp = ThreeBarReversal(npArr225, tick_val=5)
#                                 if signalN225 != 0:
#                                     op, sl, tp = GetOPSLTP(npArr, signalN225, tick_val=0.25)
#                         except: continue
#                 break
#             else:
#                 signalN225 = 0
#                 try:
#                     npArr = ibc.GetDataNpArr(contractN225M, tf)
#                     if len(npArr) > 1:
#                         signalN225, op, sl, tp = ThreeBarReversal(npArr, tick_val=5)
#                 except: pass

#                 npArr = ibc.GetDataNpArr(contractMNQ, tf)
#                 if len(npArr) < 1: continue
#                 signalCheck, op, sl, tp = ThreeBarReversal(npArr, tick_val=0.25)

#                 npArr = ibc.GetDataNpArr(contractMES, tf)
#                 if len(npArr) < 1: continue
#                 signal, op, sl, tp = ThreeBarReversal(npArr, tick_val=0.25)

#                 if signal == 0 or signal != signalCheck:
#                     # Check if N225 HAS Signal
#                     if signalN225 == 0: continue

#                     # Check if N225 AND MES, MNQ has oppisite signal
#                     if (
#                         signalN225 + signal == 0 and
#                         signalN225 + signalCheck == 0
#                     ): continue
#                     signal = signalN225
#                     op, sl, tp = GetOPSLTP(npArr, signalN225, tick_val=0.25)
#             tradeDict[tf] = [signal, op, sl, tp]
#             if signal != 0: break
#         for tf, res in tradeDict.items():
#             signal, op, sl, tp = res
#             closePos = False
#             if signal != 0:
#                 msg = f'{contractMES.symbol} {tf} {signal} {op} {sl} {tp}'
#                 vol = 1
#                 trades = ibc.GetOpenTrades()
#                 for trade in trades:
#                     if trade.contract == contractMES:
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
#                 if tf not in lastOpMap:
#                     ExecTrade(ibc, signal, contractMES, vol, op, sl, tp, closePos)
#                     Alert(msg)
#                     lastOpMap[tf] = op
#                 elif op != lastOpMap[tf]:
#                     ExecTrade(ibc, signal, contractMES, vol, op, sl, tp, closePos)
#                     Alert(msg)
#                     lastOpMap[tf] = op
#                 else:
#                     print(msg)
#         print(contractMES.symbol)

# if __name__ == '__main__':
#     main()