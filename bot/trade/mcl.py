# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.combine import Combine
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
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
# contractSCHD = Stock("SCHD", 'SMART', 'USD')
# contractQQQ = Stock("QQQ", 'SMART', 'USD')
# tradeDict = {}

# def CheckCombine(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0130
#     strategy: mcl 5 mins combine
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Combine(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "Combine"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0130
#     strategy: mes 5 mins sweep
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "ThreeBarReversal"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckTrend(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-2255
#     strategy: mes 1 min ema cross
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Trend(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "Trend"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckCopula(IS_EXEC_TRADE, dataDict, tick_val, t, hourLimit):
#     """
#     tradeTime: x 0500-0600
#     strategy: mnq 30 mins copula
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '30 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     if(
#         t >= hourLimit * 60 + 30 and
#         t <= (hourLimit + 5) * 60 + 30
#     ): 
#         npArr2 = ibc.GetDataNpArr(contractSCHD, tf)
#         if len(npArr2) < 1: return 0
#         signal, op, sl, tp = Copula(npArr, npArr2, tf, tick_val)
#         if signal != 0:
#             if abs(op - sl) > 1:
#                 if signal > 0:
#                     if tp < op: return 0
#                 elif signal < 0:
#                     if tp > op: return 0
#                 sType = "COPULA"
#                 tradeDict[tf] = [signal, op, sl, tp, sType]
#                 return 1
#     return 0

# def CheckSweep(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0130
#     strategy: mnq 5 mins sweep
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Sweep(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "SWEEP"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckIrb(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-2255
#     strategy: mnq 15 min irb
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Irb(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "Irb"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckFourBarTurn(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0200
#     strategy: mes 15 mins sweep
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = FourBarTurn(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "FOUR BAR TURN"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckEntropyHursts(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-2300
#     strategy: mnq 5 mins EntropyHursts
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = EntropyHursts(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "EntropyHursts"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckOpeningRange(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2300-2331
#     strategy: mnq 10 15 mins fade rsi
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['1 min']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = OpeningRange(npArr, tf, tick_val)
#         if signal == 0: continue
#         sType = "OPENING RANGE"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0100
#     strategy: mnq 30 mins 4btp
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

# def CheckBreakout(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2300-2331
#     strategy: mnq 10 15 mins fade rsi
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['5 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = Breakout(npArr, tf, tick_val)
#         if signal == 0: continue
#         sType = "BREAK OUT"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckKernelEma(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 5 mins kernelema
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['5 mins', '10 mins', '15 mins', '20 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = FadeRsi(npArr, tf, 5)
#         if signal == 0: continue
#         sType = "KERNEL EMA"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFadeRsi(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 5 mins fade rsi
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['5 mins', '10 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = FadeRsi(npArr, tf, 5)
#         if signal == 0: continue
#         sType = "FADE RSI"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFadeCci(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 10 mins fade cci
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '10 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = FadeCci(npArr, tf, 5)
#     if signal == 0: return 0
#     sType = "FADE CCI"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckLz(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-0100
#     strategy: mnq 30 mins Lz
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf ='30 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Lz(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "LZ"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckVwapCross(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-2255
#     strategy: mnq 5 mins vwap[-50:] 9 ema cross
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = VwapCross(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "9 EMA CROSS 50 VWAP"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1


# # def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t):
# #     """
# #     tradeTime: 2230-0300
# #     strategy: n225mc 5 mins threeBarPlay
# #     """
# #     if IS_EXEC_TRADE: return 1
# #     global tradeDict
# #     tf = '10 mins'
# #     npArr = dataDict[tf]
# #     if len(npArr) < 1: return 0
# #     signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
# #     if signal != 0:
# #         sType = "THREE BAR REVERSAL"
# #         tradeDict[tf] = [signal, op, sl, tp, sType]
# #         return 1
# #     else:
# #         signalTopix = 0
# #         signalN225 = 0
# #         try:
# #             npArrTopix = ibc.GetDataNpArr(contractMNTPX, tf)
# #             if len(npArrTopix) < 1: return 0
# #             signalTopix, op, sl, tp = ThreeBarReversal(npArrTopix, tick_val=5)
# #             npArr225 = ibc.GetDataNpArr(contractN225MC, tf)
# #             if len(npArr225) < 1: return 0
# #             signalN225, op, sl, tp = ThreeBarReversal(npArr225, tick_val=5)
# #         except: return 0
# #         # Check if N225 HAS Signal
# #         if signalTopix == 0: return 0
# #         if signalTopix != signalN225: return 0

# #         # Check if N225 AND MES, MNQ has oppisite signal
# #         if (
# #             signalTopix + signal == 0 and
# #             signalTopix + signalCheck == 0
# #         ): return 0

# #         if signalTopix == 1:
# #             if npArr[-2][2] < npArr[-3][2]: return 0
# #         elif npArr[-2][1] > npArr[-3][1]: return 0
# #         signal = signalTopix
# #         sType = "TOPIX & N225 THREE BAR REVERSAL"
# #         op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val=0.25)
# #         tradeDict[tf] = [signal, op, sl, tp, sType]
# #         return 1

# def main():
#     MIN_VOL = 1
#     contract = contractDict["MCL"]
#     tick_val = ib.reqContractDetails(contract)[0].minTick
#     hourLimit = GetTradeTime()
#     dataDict = {}
#     tfs = ['5 mins']
#     lastOpMap = {}
#     lastTp = 0
#     lastSignal = 0
#     IS_EXEC_TRADE = 0
#     while(ib.sleep(5)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         if hour == hourLimit + 7: continue
#         for tf in tfs:
#             dataDict[tf] = ibc.GetDataNpArr(contract, tf)

#         minute = currentTime.minute
#         t = hour * 60 + minute

#         if(
#             t >= hourLimit * 60 + 30 and
#             t < (hourLimit + 1) * 60 + 15
#         ): 
#             IS_EXEC_TRADE = CheckCombine(IS_EXEC_TRADE, dataDict, tick_val)

#         # if(
#         #     t >= hourLimit * 60 + 30 and
#         #     t < (hourLimit + 1) * 60
#         # ): 
#         #     IS_EXEC_TRADE = CheckIrb(IS_EXEC_TRADE, dataDict, tick_val)
        
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
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 100, 'USD')
#                     if vol < MIN_VOL: vol = 1
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
#                                 tp += tick_val * 20
#                             else:
#                                 sl -= tick_val
#                                 tp -= tick_val * 20
#                     else:
#                         ibc.cancelUntriggered()
#                         ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                     Alert(msg)
#                     lastOpMap[tf] = oriOP
#                 else:
#                     print(msg)

#         IS_EXEC_TRADE = 0
#         print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)
# if __name__ == '__main__':
#     main()