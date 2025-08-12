# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarPlay import ThreeBarPlay, GetOPSLTP
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
# from modules.trade.utils import GetVol

# ibc = ibc.Ib()
# ib = ibc.GetIB(13)

# total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
# print(total_cash)

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
        
#         # if not (
#         #     (t >= 0 and t < 6 * 60) or # Tokyo
#         #     (t >= hourLimit * 60 + 30 and t < (hourLimit + 3) * 60) # NY 2230 - 0100
#         # ): 
#         #     print("CLOSE POS 1500 0100")
#         #     continue
#         if hour == hourLimit + 7: continue
#         tradeDict = {}
#         for tf in tfs:
#             npArrSignal = ibc.GetDataNpArr(contractMES, tf)
#             if len(npArrSignal) < 1: continue
#             signal, op, sl, tp = ThreeBarPlay(npArrSignal, tf, tick_val=0.25)
#             if signal == 0: continue
#             npArr = ibc.GetDataNpArr(contractN225MC, tf)
#             if len(npArr) < 1: continue
#             op, sl, tp = GetOPSLTP(npArr, signal, tf, 1)
#             tradeDict[tf] = [signal, op, sl, tp]
#             if signal != 0: break
#         for tf, res in tradeDict.items():
#             signal, op, sl, tp = res
#             closePos = False
#             if signal != 0:
#                 msg = f'THREE BAR PLAY {contractN225MC.symbol} {tf} {signal} {op} {sl} {tp}'
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
#                     # vol = GetVol(total_cash, op, sl, tp, MIN_VOL)
#                     vol = 1
#                     print(contractN225MC.symbol, vol)
#                     if vol < MIN_VOL: continue
#                     ExecTrade(ibc, signal, contractN225MC, vol, op, sl, tp, closePos, True)
#                     Alert(msg)
#                     lastOpMap[tf] = op
#                 else:
#                     print(msg)
#         print(contractN225MC.symbol)

# if __name__ == '__main__':
#     main()