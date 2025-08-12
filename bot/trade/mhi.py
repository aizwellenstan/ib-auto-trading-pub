# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.ma import ExtremeHighLow
# from modules.strategy.fourBarTP import FourBarTP
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, GetExtreamOp, CheckITM
# from modules.trade.utils import GetVol
# from ib_insync import Stock, Forex
# from config import load_credentials
# ACCOUNT = load_credentials('account')
# if ACCOUNT == "": sys.exit()

# ibc = ibc.Ib()
# ib = ibc.GetIB(24)

# total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
# print(total_cash, avalible_cash)
# contract = Forex('USDHKD')
# ticker=ib.reqMktData(contract, '', False, False)
# ib.sleep(2)
# exchangeRate = ticker.bid
# total_cash *= exchangeRate
# # total_cash *= 4 # margin
# total_cash /= 2
# print(total_cash)

# contractDict = GetFuturesContracts(ib)

# # contract1489 = Stock("1489", 'TSEJ', 'JPY')
# # ib.qualifyContracts(contract1489)
# # print(contract1489)

# tradeDict = {}

# def CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: x0500-0600
#     strategy: mhi 5 min ExtremeHighLow
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = ExtremeHighLow(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "ExtremeHighLow"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: x 0500-0600
#     strategy: n225mc 30 mins 4btp
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['30 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = FourBarTP(npArr, tf, tick_val)
#         if signal == 0: continue
#         sType = "4btp"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFvg(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-2300
#     strategy: mes 5 min fvg
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Fvg(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "Fvg"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def main():
#     MIN_VOL = 1
#     contract = contractDict["MHI"]
#     tick_val = ib.reqContractDetails(contract)[0].minTick
#     hourLimit = GetTradeTime()
#     dataDict = {}
#     tfs = ['5 mins', '30 mins']
#     lastOpMap = {}
#     IS_EXEC_TRADE = 0
#     lastSignal = 0
#     lastTp = 0
#     while(ib.sleep(5)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         t = hour * 60 + minute
#         if hour in [20, 21, 22]: continue # x0500-0600
#         if hour == 23 and minute < 50: continue
#         print(hour, minute)
#         for tf in tfs:
#             dataDict[tf] = ibc.GetDataNpArr(contract, tf)
        
#         # Normal Trading Hour 1015-1300 1400-1730
#         if hour < 1: continue
#         if hour == 1 and minute < 15: continue
#         if hour == 8 and minute >= 30: continue
#         if hour > 8: continue

#         if(
#             t >= 1 * 60 + 15 and
#             t < 7 * 60 + 10
#         ): 
#             IS_EXEC_TRADE = CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val)
        
#         # IS_EXEC_TRADE = CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val)

#         for tf, res in tradeDict.items():
#             signal, op, sl, tp, sType = res
#             closePos = False
#             positions = ibc.GetPositionsOri()  # A list of positions, according to IB
#             if signal != 0:
#                 lastSignal = signal
#                 lastTp = tp
#                 msg = f'{sType} {contract.symbol} {tf} {signal} {op} {sl} {tp}'
#                 trades = ibc.GetOpenTrades()
#                 for trade in trades:
#                     if trade.contract == contract:
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
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 10, 'HKD')
#                     oriOP = op
#                     orders = ib.openTrades()
#                     ibc.cancelUntriggered()
#                     if vol >= MIN_VOL:
#                         if vol > 1:
#                             for i in range(1, vol + 1):
#                                 if signal == 1:
#                                     if op <= sl: 
#                                         sl = op - tick_val
#                                 else:
#                                     if op >= sl: 
#                                         sl = op + tick_val
#                                 ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                                 if signal == 1:
#                                     # op -= 5
#                                     sl += tick_val
#                                     tp += tick_val * 20
#                                 else:
#                                     # op += 5
#                                     sl -= tick_val
#                                     tp -= tick_val * 20
#                         else:
#                             if signal > 0:
#                                 op += tick_val * 2
#                             elif signal < 0:
#                                 op -= tick_val * 2
#                             ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                     Alert(msg)
#                     lastOpMap[tf] = oriOP
#                 else:
#                     print(msg)
#         if lastSignal != 0 or lastTp != 0:
#             if lastSignal > 0:
#                 if len(dataDict['30 mins']) < 1: continue
#                 if dataDict['30 mins'][-1][3] > lastTp:
#                     ibc.cancelUntriggered()
#                     lastSignal = 0
#                     lastTp = 0
#             else:
#                 if dataDict['30 mins'][-1][3] < lastTp:
#                     ibc.cancelUntriggered()
#                     lastSignal = 0
#                     lastTp = 0
#         IS_EXEC_TRADE = 0
#         print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)

# if __name__ == '__main__':
#     main()