from ib_insync import *
from modules.discord import Alert

def GetTradeTime():
    dayLightSaving = False
    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14
    return hourLimit

def GetFuture(ib, conId=563947733, symbol='NQ', lastTradeDateOrContractMonth='20241220', multiplier='20', currency='USD', localSymbol='NQZ4', tradingClass='NQ', right='', primaryExchange=''):
    future = Future(
        conId=conId, symbol=symbol, 
        lastTradeDateOrContractMonth=lastTradeDateOrContractMonth, 
        multiplier=multiplier, currency=currency, 
        localSymbol=localSymbol, tradingClass=tradingClass)
    ib.qualifyContracts(future)
    print(future)
    return future

def GetFuturesContracts(ib):
    # https://pennies.interactivebrokers.com/cstools/contract_info/v3.10/index.php
    contractDict = {}
    contractDict["ES"] = GetFuture(ib, conId=495512557, symbol='ES', lastTradeDateOrContractMonth='20241220', multiplier='50', currency='USD', localSymbol='ESZ4', tradingClass='ES')
    contractDict["NQ"] = GetFuture(ib, conId=563947733, symbol='NQ', lastTradeDateOrContractMonth='20241220', multiplier='20', currency='USD', localSymbol='NQZ4', tradingClass='NQ')
    contractDict["YM"] = GetFuture(ib, conId=672387412, symbol='YM', lastTradeDateOrContractMonth='20241220', multiplier='5', currency='USD', localSymbol='YMZ4', tradingClass='YM')
    contractDict["MNQ"] = GetFuture(ib, conId=691171685, symbol='MNQ', lastTradeDateOrContractMonth='20250620', right='0', multiplier='2', primaryExchange='CME', currency='USD', localSymbol='MNQM5', tradingClass='MNQ')
    contractDict["MES"] = GetFuture(ib, conId=691171673, symbol='MES', lastTradeDateOrContractMonth='20250620', right='0', multiplier='5', primaryExchange='CME', currency='USD', localSymbol='MESM5', tradingClass='MES')
    contractDict["MYM"] = GetFuture(ib, conId=672387407, symbol='MYM', lastTradeDateOrContractMonth='20241220', multiplier='0.5', currency='USD', localSymbol='MYMZ4', tradingClass='MYM')
    contractDict["TOPX"] = GetFuture(ib, conId=652809919, symbol='TOPX', lastTradeDateOrContractMonth='20241212', multiplier='10000', currency='JPY', localSymbol='169120005', tradingClass='TPX')
    contractDict["MNTPX"] = GetFuture(ib, conId=689341765, symbol='MNTPX', lastTradeDateOrContractMonth='20241212', multiplier='1000', currency='JPY', localSymbol='169120006', tradingClass='TPXM')
    contractDict["MCL"] = GetFuture(ib, conId=645904247, symbol='MCL', lastTradeDateOrContractMonth='20241119', multiplier='100', currency='USD', localSymbol='MCLZ4', tradingClass='MCL')
    contractDict["N225"] = GetFuture(ib, conId=326066886, symbol='N225', lastTradeDateOrContractMonth='20241212', multiplier='1000', currency='JPY', localSymbol='169120018', tradingClass='225')
    contractDict["N225M"] = GetFuture(ib, conId=395556077, symbol='N225M', lastTradeDateOrContractMonth='20241212', multiplier='100', currency='JPY', localSymbol='169120019', tradingClass='225M')
    contractDict["N225MC"] = GetFuture(ib, conId=709538015, symbol='N225MC', lastTradeDateOrContractMonth='20241212', multiplier='10', currency='JPY', localSymbol='169120023', tradingClass='225MC')
    contractDict["MHI"] = GetFuture(ib, conId=726172442, symbol='MHI', lastTradeDateOrContractMonth='20241030', multiplier='10', currency='HKD', localSymbol='MHIV4', tradingClass='MHI')
    contractDict["DJIA"] = GetFuture(ib, conId=672750938, symbol='DJIA', lastTradeDateOrContractMonth='20241220', multiplier='100', currency='JPY', localSymbol='169120073', tradingClass='DJIA')
    contractDict["GC"] = GetFuture(ib, conId=347896248, symbol='GC', lastTradeDateOrContractMonth='20241227', multiplier='100', currency='USD', localSymbol='GCZ4', tradingClass='GC')
    contractDict["MGC"] = GetFuture(ib, conId=639786536, symbol='MGC', lastTradeDateOrContractMonth='20250626', multiplier='10', currency='USD', localSymbol='MGCM5', tradingClass='MGC')
    contractDict["SIL"] = GetFuture(ib, conId=719262093, symbol='SI', lastTradeDateOrContractMonth='20250729', multiplier='1000', currency='USD', localSymbol='SILN5', tradingClass='SIL')
    contractDict["JPY"] = GetFuture(ib, conId=383308433, symbol='JPY', lastTradeDateOrContractMonth='20240916', multiplier='12500000', currency='USD', localSymbol='6JU4', tradingClass='6J')
    contractDict["NKD"] = GetFuture(ib, conId=353749282, symbol='NKD', lastTradeDateOrContractMonth='20241212', multiplier='5', currency='USD', localSymbol='NKDZ4', tradingClass='NKD')
    return contractDict

# def cancelUntriggered(ib):
#     oos = list(ib.openOrders())
#     ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
#     dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
#     aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
#     for oo in aoos:
#         print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
#         if oo.orderType == "LMT":
#             ib.cancelOrder(oo)

def cancelUntriggeredAll(ibc, trades, contract):
    IS_ITM = True
    for trade in trades:
        if trade.contract == contract:
            if trade.order.orderType == "LMT":
                ibc.CancelOrder(trade.order)
    return IS_ITM

def cancelUntriggered(ibc, trades, contract, action):
    IS_ITM = True
    reverseAction = 'BUY' if action == 'SELL' else 'SELL'
    for trade in trades:
        if trade.contract == contract:
            if trade.order.action == action:
                if trade.order.orderType == "LMT":
                    ibc.CancelOrder(trade.order)
    return IS_ITM

def GetAvgCost(ibc, contract):
    positions = ibc.GetPositionsOri()
    for position in positions:
        print(position)
        if position.contract == contract:
            if position.contract.multiplier == "": 
                return 0
            avgCost = position.avgCost / int(position.contract.multiplier)
            return avgCost
    return 0

def CheckITM(ibc, trades, contract, action):
    cancelUntriggered(ibc, trades, contract, action)
    avgCost = GetAvgCost(ibc, contract)
    IS_ITM = True
    reverseAction = 'BUY' if action == 'SELL' else 'SELL'
    for trade in trades:
        if trade.contract == contract:
            if trade.order.action == reverseAction:
                if trade.order.orderType == "TRAIL":
                    if action == "BUY":
                        print(trade.order.trailStopPrice, avgCost)
                        if trade.order.trailStopPrice < avgCost:
                            IS_ITM = False
                    else:
                        if trade.order.trailStopPrice > avgCost:
                            IS_ITM = False
    return IS_ITM

def ExecTrade(ibc, signal, contract, vol, op, sl, tp, closePos, outsideRth=False):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    if signal > 0:
        # cancelUntriggered(ib)
        for position in positions:
            if (
                position.contract == contract and
                position.position > 0
            ): trades += 1
        if trades < 1:
            ibc.HandleStopBracketOrderWithTpWithContract(
                contract, 'BUY', vol, op, sl, tp, closePos, outsideRth)
        else:
            Alert(f'already have {signal} in {contract.symbol}')
    elif signal < 0:
        # cancelUntriggered(ib)
        for position in positions:
            if (
                position.contract == contract and
                position.position < 0
            ): trades += 1
        if trades < 1:
            ibc.HandleStopBracketOrderWithTpWithContract(
                contract, 'SELL', vol, op, sl, tp, closePos)
        else:
            Alert(f'already have {signal} in {contract.symbol}')

def ExecBracket(ibc, signal, contract, vol, op, sl, tp, account=''):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    if signal > 0:
        # cancelUntriggered(ib)
        action = 'BUY'
        ibc.HandleStopBracketOrderWithTpWithContract(contract, action, vol, op, sl, tp, account)
        # for position in positions:
        #     if (
        #         position.contract == contract and
        #         position.position > 0 and 
        #         position.contract.right == ''
        #     ): trades += 1
        # if trades < 1:
        #     ibc.HandleStopBracketOrderWithTpWithContract(contract, action, vol, op, sl, tp, account)
        # else:
        #     Alert(f'already have {signal} in {contract.symbol}')
    elif signal < 0:
        # cancelUntriggered(ib)
        action = 'SELL'
        for position in positions:
            if (
                position.contract == contract and
                position.position < 0
            ): trades += 1
        if trades < 1:
            ibc.HandleStopBracketOrderWithTpWithContract(contract, action, vol, op, sl, tp, account)
        else:
            Alert(f'already have {signal} in {contract.symbol}')

def CleanUp(ibc, signal, contract, account=""):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    if signal > 0:
        for position in positions:
            if (
                position.contract == contract and
                position.position > 0
            ): trades += 1
            if (
                position.contract == contract and
                position.position < 0
            ): 
                print("CLEAN UP")
                ibc.CleanUp(contract, position.position, account)
        if trades < 1:
            ibc.cancelUntriggered()
        else:
            Alert(f'already have {signal} in {contract.symbol}')
    elif signal < 0:
        for position in positions:
            if (
                position.contract == contract and
                position.position < 0
            ): trades += 1
            if (
                position.contract == contract and
                position.position > 0
            ): 
                ibc.CleanUp(contract, position.position, account)
        if trades < 1:
            ibc.cancelUntriggered()
        else:
            Alert(f'already have {signal} in {contract.symbol}')

def GetCurrentPosition(ibc, contract):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    for position in positions:
        if (
            position.contract == contract
        ):  return position.position
    return 0

def ExecTrail(ibc, signal, contract, vol, op, sl, tp, minTick, fixedTrail=False, account="", orders=[]):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    if signal > 0:
        action = 'BUY'
        for position in positions:
            if (
                position.contract == contract and
                position.position > 0
            ): trades += 1
            if (
                position.contract == contract and
                position.position < 0
            ): 
                print("CLEAN UP")
                ibc.CleanUp(contract, position.position, account)
        if trades < 1:
            ibc.HandleTrailStopBracketOrderWithTpWithContract(
                contract, action, vol, op, sl, tp, minTick, fixedTrail, account)
        elif CheckITM(ibc, orders, contract, action):
            ibc.HandleTrailStopBracketOrderWithTpWithContract(
            contract, action, vol, op, sl, tp, minTick, fixedTrail, account)
        else:
            Alert(f'already have {signal} in {contract.symbol}')
    elif signal < 0:
        action = 'SELL'
        for position in positions:
            if (
                position.contract == contract and
                position.position < 0
            ): trades += 1
            if (
                position.contract == contract and
                position.position > 0
            ): 
                ibc.CleanUp(contract, position.position, account)
        if trades < 1:
            ibc.cancelUntriggered()
            ibc.HandleTrailStopBracketOrderWithTpWithContract(
                contract, action, vol, op, sl, tp, minTick, fixedTrail, account)
        elif CheckITM(ibc, orders, contract, action):
                ibc.HandleTrailStopBracketOrderWithTpWithContract(
                contract, action, vol, op, sl, tp, minTick, fixedTrail, account)
        else:
            Alert(f'already have {signal} in {contract.symbol}')

def GetExtreamOp(signal, vol, op, sl, tick_val=5):
    extreamOp = op
    for i in range(1, vol + 1):
        if signal == 1:
            if op <= sl: 
                sl = op - tick_val
        else:
            if op >= sl: 
                sl = op + tick_val
        extreamOp = op
        if signal == 1:
            op -= tick_val
            sl += tick_val
        else:
            op += tick_val
            sl -= tick_val
    return extreamOp

def ExecTrailMOC(ibc, signal, contract, vol, op, sl, minTick=0.01, account=''):
    trades = 0
    positions = ibc.GetPositionsOri()  # A list of positions, according to IB
    if signal > 0:
        for position in positions:
            if (
                position.contract == contract and
                position.position > 0
            ): trades += 1
        if trades < 1:
            ibc.HandleTrailStopBracketOrderWithMocWithContract(
                contract, 'BUY', vol, op, sl, minTick, account='')
        else:
            Alert(f'already have {signal} in {contract.symbol}')
    elif signal < 0:
        for position in positions:
            if (
                position.contract == contract and
                position.position < 0
            ): trades += 1
        if trades < 1:
            ibc.HandleTrailStopBracketOrderWithMocWithContract(
                contract, 'SELL', vol, op, sl, minTick, account)
        else:
            Alert(f'already have {signal} in {contract.symbol}')