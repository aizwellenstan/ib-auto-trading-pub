# import os;from pathlib import Path
# rootPath = Path(os.path.dirname(__file__)).parent.parent
# import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
# from modules.discord import Alert
# import modules.ib as ibc
# from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
# from modules.strategy.ma import ExtremeHighLow, SimpleMaCross
# from modules.strategy.vwap import HpVwapCross
# from modules.strategy.copula import Copula
# from modules.strategy.kernelema import KernelEma
# from modules.strategy.macd import Macd
# from modules.strategy.manipulationBlock import Mb
# from modules.strategy.ob import ObFiveMin
# from modules.strategy.vsa import NoSupplyBar
# from modules.strategy.threeBarPlay import ThreeBarPlay
# from modules.strategy.harami import Harami
# from modules.strategy.fourBarTP import FourBarTP
# from modules.strategy.trend import Trend
# from modules.strategy.donchainChannel import DcBreakOut
# from modules.strategy.irb import HpIrb, ReverseIrb
# from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail
# from modules.trade.utils import GetVol
# from ib_insync import Stock, Forex
# from config import load_credentials
# ACCOUNT = load_credentials('account')
# print(ACCOUNT)

# ibc = ibc.Ib()
# ib = ibc.GetIB(22)

# total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
# print(total_cash, avalible_cash)
# contract = Forex('USDJPY')
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

# def CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0100
#     strategy: mntpx 5 min ExtremeHighLow
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

# def CheckHpVwapCross(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: 2230-0130
#     strategy: mes 5 mins fade rsi
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = HpVwapCross(npArr, tf, tick_val)
#     if signal == 0: return 0
#     sType = "HpVwapCross"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckCopula(IS_EXEC_TRADE, dataDict, tick_val):
#     """
#     tradeTime: x 0500-0600
#     strategy: mntpx 30 mins copula
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '30 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     npArr2 = ibc.GetDataNpArr(contractDict["N225"], tf)
#     if len(npArr2) < 1: return 0
#     signal, op, sl, tp = Copula(npArr, npArr2, tf, tick_val)
#     if signal == 0: return 0
#     if abs(op - sl) <= 1: return 0
#     if signal > 0:
#         if tp < op: return 0
#     elif signal < 0:
#         if tp > op: return 0
#     sType = "COPULA"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckKernelEma(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: x 0500-0600
#     strategy: mntpx 5 mins kernelema
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = KernelEma(npArr, tf, 5)
#     if signal == 0: return 0
#     if abs(op - sl) <= 1: return 0
#     if signal > 0:
#         if tp < op: return 0
#     elif signal < 0:
#         if tp > op: return 0
#     sType = "KERNEL EMA"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckSimpleMaCross(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2200-2300
#     strategy: mes 5 mins 10 25 simple ma cross
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = SimpleMaCross(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "10 25 SIMPLE MA CROSS"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckMacd(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: x 0500-0600
#     strategy: mntpx 5 mins macd
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Macd(npArr, tf, tick_val=5)
#     if signal == 0: return 0
#     sType = "MACD"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# # def CheckMesSignalThreeBayPlayThreeBayReversal(IS_EXEC_TRADE, dataDict):
# #     """
# #     tradeTime: x 0500
# #     strategy: mes 5 mins threeBayPlay threeBarReversal
# #     """
# #     if IS_EXEC_TRADE: return 1
# #     global tradeDict
# #     tf = '5 mins'
# #     npArrSignal = ibc.GetDataNpArr(contractMES, tf)
# #     if len(npArrSignal) < 1: return 0
# #     sType = ""
# #     signal, op, sl, tp = ThreeBarReversal(npArrSignal, tf, tick_val=0.25)
# #     if signal == 0: return 0 
# #     sType = "THREE BAR REVERSAL MES"
# #     op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=5)
# #     tradeDict[tf] = [signal, op, sl, tp, sType]
# #     return 1

# def CheckHpIrb(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: x0500-0600
#     strategy: mntpx 5 mins hpirb
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = HpIrb(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "HPIRB"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# # def CheckObFiveMin(IS_EXEC_TRADE, dataDict):
# #     """
# #     tradeTime: x 0500-0600
# #     strategy: mntpx 5 mins ob
# #     """
# #     if IS_EXEC_TRADE: return 1
# #     global tradeDict
# #     tf = '5 mins'
# #     npArr = dataDict[tf]
# #     if len(npArr) < 1: return 0
# #     signal, op, sl, tp = ObFiveMin(npArr, tf, tick_val=5)
# #     if signal == 0: return 0
# #     sType = "OB"
# #     tradeDict[tf] = [signal, op, sl, tp, sType]
# #     return 1

# # def CheckThreeBarPlay(IS_EXEC_TRADE, dataDict):
# #     """
# #     tradeTime: 0900-1500 2230-0100
# #     strategy: n225mc 5 mins threeBarPlay
# #     """
# #     if IS_EXEC_TRADE: return 1
# #     global tradeDict
# #     tf = '5 mins'
# #     npArr = dataDict[tf]
# #     if len(npArr) < 1: return 0
# #     signal, op, sl, tp = ThreeBarPlay(npArr, tf, tick_val=5)
# #     if signal == 0: return 0
# #     sType = "THREE BAR PLAY"
# #     tradeDict[tf] = [signal, op, sl, tp, sType]
# #     return 1

# # def CheckThreeBarReversal(IS_EXEC_TRADE):
# #     """
# #     tradeTime: x 0300-0500
# #     strategy: n225mc & mntpx 20 mins / 30 mins threeBarReversal
# #     """
# #     if IS_EXEC_TRADE: return 1
# #     global tradeDict
# #     tfs = ['20 mins', '30 mins']
# #     for tf in tfs:
# #         npArr = ibc.GetDataNpArr(contractMNTPX, tf)
# #         if len(npArr) < 1: continue
# #         signalCheck, op, sl, tp =  ThreeBarReversal(npArr, tf, tick_val=5)
# #         if signalCheck == 0: continue
# #         npArr = ibc.GetDataNpArr(contractN225MC, tf)
# #         if len(npArr) < 1: continue
# #         signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=5)
# #         if signal == 0: continue
# #         if signal != signalCheck: continue
# #         if signal == 1: op += 5 #one tick above topx 10.5
# #         sType = "n225mc & mntpx THREE BAR REVERSAL"
# #         tradeDict[tf] = [signal, op, sl, tp, sType]
# #         return 1
# #     return 0

# def main():
#     MIN_VOL = 1
#     contract = contractDict["MNTPX"]
#     tick_val = ib.reqContractDetails(contract)[0].minTick
#     hourLimit = GetTradeTime()
#     dataDict = {}
#     tfs = ['5 mins', '30 mins']
#     lastOpMap = {}
#     IS_EXEC_TRADE = 0
#     while(ib.sleep(2)):
#         currentTime = ib.reqCurrentTime()
#         hour = currentTime.hour
#         minute = currentTime.minute
#         t = hour * 60 + minute
#         if hour in [20, 21, 22]: continue # x0500-0600
#         if hour == 23 and minute < 50: continue
#         print(hour, minute)
#         for tf in tfs:
#             dataDict[tf] = ibc.GetDataNpArr(contractDict["TOPX"], tf)

#         IS_EXEC_TRADE = CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, tick_val)

#         IS_EXEC_TRADE = CheckCopula(IS_EXEC_TRADE, dataDict, tick_val)

#         if(
#             t >= hourLimit * 60 + 40 and
#             t < (hourLimit + 1) * 60
#         ): 
#             IS_EXEC_TRADE = CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val)

#         for tf, res in tradeDict.items():
#             signal, op, sl, tp, sType = res
#             closePos = False
#             if signal != 0:
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
#                     vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1000, 'JPY')
#                     if vol < MIN_VOL: vol = 1
#                     oriOP = op
#                     if vol > 1:
#                         for i in range(1, vol + 1):
#                             if signal == 1:
#                                 if op <= sl: 
#                                     sl = op - 5
#                             else:
#                                 if op >= sl: 
#                                     sl = op + 5
#                             ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                             if signal == 1:
#                                 sl += 5
#                                 tp += 100
#                             else:
#                                 sl -= 5
#                                 tp -= 100
#                     else:
#                         ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
#                     Alert(msg)
#                     lastOpMap[tf] = oriOP
#                 else:
#                     print(msg)
#         IS_EXEC_TRADE = 0
#         print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)

# if __name__ == '__main__':
#     main()