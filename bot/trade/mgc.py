# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.strategy.ma import Irb, ReverseIrb, ExtremeHighLow
# from modules.strategy.rsi import Rsi
# from modules.strategy.donchainChannel import DcMidReversal
# from modules.strategy.copula import Copula
# from modules.strategy.sweep import Sweep
# from modules.strategy.turn import FourBarTurn
# from modules.strategy.entropyHursts import EntropyHursts
# from modules.strategy.fourBarTP import FourBarTP
# from modules.strategy.volume import OpeningRange
# from modules.strategy.breakout import Breakout
# from modules.strategy.kernelema import KernelEma
# from modules.strategy.rsi import FadeRsi
# from modules.strategy.cci import FadeCci
# from modules.strategy.lorentizianClassification import Lz
# from modules.strategy.vwap import VwapCross
# from modules.strategy.irb import Irb
# from modules.strategy.combine import Combine
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
# from modules.trade.options import BuyOption
# from modules.trade.utils import GetVol
# from ib_insync import Stock, CFD
# from modules.trade.utils import floor_round, ceil_round
# from config import load_credentials
# ACCOUNT = load_credentials('account')
# STOCKACCOUNT = load_credentials('stockAccount')
# CASHACCOUNT = load_credentials('cashAccount')

# ibc = ibc.Ib()
# ib = ibc.GetIB(15)

# total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
# print(total_cash, avalible_cash)
# # total_cash *= 4 # margin
# total_cash /= 2
# print(total_cash)

# stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
# stock_total_cash /= 3

# contractDict = GetFuturesContracts(ib)
# tradeDict = {}

# def CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val, t, hourLimit):
#     """
#     tradeTime: 2230-2359
#     strategy: mnq 5 15 20 min ExtremeHighLow
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) > 0:
#         signal, op, sl, tp = ExtremeHighLow(npArr, tf, tick_val)
#         if signal != 0:
#             sType = "ExtremeHighLow"
#             tradeDict[tf] = [signal, op, sl, tp, sType]
#             return 1
#     if(
#         t >= hourLimit * 60 + 30 and
#         t < (hourLimit + 1) * 60 + 30
#     ): 
#         tfs = ['15 mins', '20 mins']
#         for tf in tfs:
#             npArr = dataDict[tf]
#             if len(npArr) < 1: continue
#             signal, op, sl, tp = ExtremeHighLow(npArr, tf, tick_val)
#             if signal == 0: continue
#             sType = "ExtremeHighLow"
#             tradeDict[tf] = [signal, op, sl, tp, sType]
#             return 1
#     return 0

# def main():
#     MIN_VOL = 1
#     contract = contractDict["MGC"]
#     tick_val = ib.reqContractDetails(contract)[0].minTick
#     hourLimit = GetTradeTime()
#     dataDict = {}
#     tfs = ['5 mins', '15 mins', '20 mins']
#     lastOpMap = {}
#     lastTp = 0
#     lastSignal = 0
#     IS_EXEC_TRADE = 0
#     while(ib.sleep(2)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         if hour == hourLimit + 7: continue
#         for tf in tfs:
#             dataDict[tf] = ibc.GetDataNpArr(contractDict["GC"], tf)

#         minute = currentTime.minute
#         t = hour * 60 + minute

#         if(
#             t >= hourLimit * 60 + 30 and
#             t < (hourLimit + 3) * 60 + 30
#         ): 
#             IS_EXEC_TRADE = CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val, t, hourLimit)
        
#         for tf, res in tradeDict.items():
#             signal, op, sl, tp, sType = res
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
#                         elif trade.order.action == 'SELL':
#                             if signal < 0:
#                                 print(f'Pending SELL Order {trade.contract.symbol}')
#                                 continue
#                 if tf not in lastOpMap or op != lastOpMap[tf]:
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 10, 'USD')
#                     IN_POSITION = False
#                     if vol < MIN_VOL: 
#                         positions = ibc.GetPositionsOri()  # A list of positions, according to IB
#                         if signal > 0:
#                             for position in positions:
#                                 if (
#                                     position.contract == contract and
#                                     position.position > 0
#                                 ): 
#                                     IN_POSITION = True
#                                     break
#                         elif signal < 0:
#                             for position in positions:
#                                 if (
#                                     position.contract == contract and
#                                     position.position < 0
#                                 ): 
#                                     IN_POSITION = True
#                                     break
#                         vol = 1
#                     oriOP = op
#                     if vol > 1:
#                         for i in range(1, vol + 1):
#                             if op == sl: 
#                                 if signal == 1:
#                                     sl = op - tick_val
#                                 else:
#                                     sl = op + tick_val
#                             ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                             if signal == 1:
#                                 sl += tick_val
#                                 tp += tick_val * 400
#                             else:
#                                 sl -= tick_val
#                                 tp -= tick_val * 400
#                     else:
#                         ibc.cancelUntriggered()
#                         if signal > 0:
#                             op += tick_val * 2
#                         elif signal < 0:
#                             op -= tick_val * 2
#                         if not IN_POSITION:
#                             ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                     Alert(msg)
#                     lastOpMap[tf] = oriOP
#                 else:
#                     print(msg)

#         IS_EXEC_TRADE = 0
#         print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)

# if __name__ == '__main__':
#     main()