rootPath = ".."
import sys
sys.path.append(rootPath)
import math
import pandas as pd
from ib_insync import *
from modules.discord import Alert
from typing import NamedTuple
from modules.normalizeFloat import NormalizeFloat
from modules.trade.utils import ceil_round

class LimitBracketOrder(NamedTuple):
    parent: Order
    stopLoss: Order

class LimitBracketMocOrder(NamedTuple):
    parent: Order
    stopLoss: Order
    moc: Order

class LimitTpBracketOrder(NamedTuple):
    parent: Order
    takeProfit: Order
    stopLoss: Order

class BracketCloseOrder(NamedTuple):
    parent: Order
    moc: Order

class MarketBracketOrder(NamedTuple):
    parent: Order
    takeProfit: Order

class MarketSingleOrder(NamedTuple):
    parent: Order

class LimitSingleOrder(NamedTuple):
    parent: Order

class LitOrder(Order):
    def __init__(self, action: str, 
                totalQuantity: float, 
                lmtPrice: float,
                triggerPrice: float,
                orderId: int,
                parentId: int,
                **kwargs):
        Order.__init__(
            self, orderType='LIT', action=action,
            totalQuantity=totalQuantity, 
            lmtPrice=lmtPrice, 
            auxPrice=triggerPrice,
            orderId=orderId,
            transmit=True,
            parentId=parentId,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)

class TrialLimit(Order):
    def __init__(self, action: str, 
                totalQuantity: float, 
                lmtPrice: float,
                trailStopPrice: float,
                trailingPercent: float,
                orderId: int,
                parentId: int,
                **kwargs):
        Order.__init__(
            self, orderType='TRAIL LIMIT', action=action,
            totalQuantity=totalQuantity, 
            lmtPrice=lmtPrice, 
            trailStopPrice = trailStopPrice,
            trailingPercent=trailingPercent, 
            orderId=orderId,
            transmit=True,
            parentId=parentId,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)

class Ib:
    ib = None
    clientId = 0

    def GetIB(self, clientId=1):
        self.ib = IB()
        # IB Gateway
        # ib.connect('127.0.0.1', 4002, clientId=1)

        # TWS
        self.ib.connect('127.0.0.1', 7497, clientId=clientId)
        self.clientId = clientId
        return self.ib

    def reconnect(self):
        self.ib.disconnect()
        self.clientId += 1
        self.ib.connect('127.0.0.1', 7497, clientId=self.clientId)
        return self.ib

    def GetTotalCash(self, account=""):
        oriCashDf = pd.DataFrame(self.ib.accountValues(account))
        # cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        # cashDf = cashDf.loc[cashDf['tag'] == 'AvailableFunds']
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'NetLiquidationByCurrency']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        total_cash = float(cashDf['value'].iloc[0])
        print("TOTAL_CASH", total_cash)
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'AvailableFunds']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        avalible_cash = float(cashDf['value'].iloc[0])
        print("AVALIBLE_CASH", avalible_cash)
        return total_cash, avalible_cash

    def GetTotalCashExchangeRate(self):
        oriCashDf = pd.DataFrame(self.ib.accountValues())
        # cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        # cashDf = cashDf.loc[cashDf['tag'] == 'AvailableFunds']
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'NetLiquidationByCurrency']
        cashDf = cashDf.loc[cashDf['currency'] == 'BASE']
        total_cash = float(cashDf['value'].iloc[0])
        print(total_cash)
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'AvailableFunds']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        avalible_cash = float(cashDf['value'].iloc[0])
        print(avalible_cash)
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'ExchangeRate']
        cashDf = cashDf.loc[cashDf['currency'] == 'JPY']
        exchangeRate = float(cashDf['value'].iloc[0])
        print(exchangeRate)
        
        return total_cash, exchangeRate

    def GetAvailableCash(self):
        oriCashDf = pd.DataFrame(self.ib.accountValues())
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(oriCashDf)
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'CashBalance']
        cashDf = cashDf.loc[cashDf['currency'] == 'JPY']
        avalible_cash = float(cashDf['value'].iloc[0])
        print(avalible_cash)
        return avalible_cash

    def GetBalance(self):
        oriCashDf = pd.DataFrame(self.ib.accountValues())
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(oriCashDf)
        cashDf = oriCashDf.loc[oriCashDf['tag'] == 'NetLiquidation']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        avalible_cash = float(cashDf['value'].iloc[0])
        print(avalible_cash)
        return avalible_cash
    
    def qualifyContracts(self, contract):
        return self.ib.qualifyContracts(contract)
    
    def GetStockContract(self, symbol, currency='USD'):
        contract = Stock(symbol, 'SMART', currency)
        self.ib.qualifyContracts(contract)
        return contract

    def GetStockContractJP(self, symbol):
        contract = Stock(symbol, 'TSEJ', 'JPY')
        self.ib.qualifyContracts(contract)
        return contract
    
    def GetCFDContract(self, symbol, currency):
        contract = CFD(symbol, 'SMART', 'USD')
        return contract

    def GetStockContractQuickJP(self, symbol):
        contract = Stock(symbol, 'TSEJ', 'JPY')
        return contract

    def GetStockContractSmartJP(self, symbol):
        contract = Stock(symbol, 'SMART', 'JPY')
        return contract

    def GetOptionCallContract(self, symbol, expiration, strike):
        contract = Option(symbol, expiration, strike, 'C', 'SMART', tradingClass=symbol)
        self.ib.qualifyContracts(contract)
        return contract

    def GetOptionPutContract(self, symbol, expiration, strike):
        contract = Option(symbol, expiration, strike, 'P', 'SMART', tradingClass=symbol)
        self.ib.qualifyContracts(contract)
        return contract

    def GetAskBid(self,symbol):
        contract = self.GetStockContract(symbol)
        ticker=self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)
        ask = ticker.ask
        bid = ticker.bid
        retryCount = 0
        while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
            print("retry")
            ticker=self.ib.reqMktData(contract, '', False, False)
            self.ib.sleep(3)
            ask = ticker.ask
            bid = ticker.bid
            retryCount += 1

        if (math.isnan(bid) or bid < 0.2):
            try:
                bid = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

                ask = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
            except:
                print("math.isnan(bid) or bid < 0.2")
                return 0, 0
        return ask, bid

    def GetAskBidWithContract(self,contract):
        ticker=self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)
        ask = ticker.ask
        bid = ticker.bid
        retryCount = 0
        while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
            print("retry")
            ticker=self.ib.reqMktData(contract, '', False, False)
            self.ib.sleep(3)
            ask = ticker.ask
            bid = ticker.bid
            retryCount += 1

        if (math.isnan(bid) or bid < 0.2):
            try:
                bid = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

                ask = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
            except:
                print("math.isnan(bid) or bid < 0.2")
                return 0, 0
        return ask, bid
    
    def GetOptionPrice(self, contract):
        ticker = self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)
        bid = ticker.bid
        ask = ticker.ask
        if math.isnan(ask) or ask < 0:
            ask = self.ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[-1].close
        if math.isnan(bid) or bid < 0:
            bid = self.ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 min', whatToShow='BID', useRTH=True)[-1].close
        return bid, ask

    def limitBracketOrder(self, c,
        action: str, quantity: float,
        limitPrice: float, **kwargs) -> LimitBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        trail_perc = 4 #12.5 #2.3
        trailStopPrice = limitPrice - math.ceil(limitPrice * trail_perc)*100/100
        if trailStopPrice < 0.02: trailStopPrice = 0.02
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = trailStopPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return LimitBracketOrder(parent, stopLoss)

    def limitBracketMocOrder(self, c,
        action: str, quantity: float,
        limitPrice: float, **kwargs) -> LimitBracketMocOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        trail_perc = 2 #12.5 #2.3
        trailStopPrice = limitPrice - math.ceil(limitPrice * trail_perc)*100/100
        if trailStopPrice < 0.02: trailStopPrice = 0.02
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = trailStopPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        moc = Order(
            orderType='MOC', action=reverseAction,
            totalQuantity=quantity,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=True,
            conditionsIgnoreRth=True,
            parentId=parent.orderId,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True)
        return LimitBracketMocOrder(parent, stopLoss, moc)
    
    def litLimitBracketOrderWithTp(self, c,
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float,
        stopLossPrice: float, 
        closePos: bool, tick_val=5,**kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parentQuantity = quantity
        if closePos: parentQuantity += 1
        parent = LimitOrder(
            action, parentQuantity, limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = LimitOrder(
            reverseAction, quantity, takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        lmtPrice = stopLossPrice
        if reverseAction == 'SELL':
            lmtPrice -= tick_val
        else:
            lmtPrice += tick_val
        stopLoss = LitOrder(
            reverseAction, quantity,
            orderId=self.ib.client.getReqId(),
            lmtPrice=lmtPrice, 
            triggerPrice=stopLossPrice,
            parentId=parent.orderId)
        return BracketOrder(parent, takeProfit, stopLoss)
    
    def trailLimitBracketOrderWithTp(self, c,
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float,
        stopLossPrice: float, 
        closePos: bool, tick_val=5,**kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parentQuantity = quantity
        if closePos: parentQuantity += 1
        parent = LimitOrder(
            action, parentQuantity, limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = LimitOrder(
            reverseAction, quantity, takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        lmtPrice = stopLossPrice
        if reverseAction == 'SELL':
            lmtPrice -= tick_val
        else:
            lmtPrice += tick_val
        stopLoss = TrialLimit(
            reverseAction, quantity,
            orderId=self.ib.client.getReqId(),
            lmtPrice=stopLossPrice, 
            trailStopPrice = stopLossPrice,
            trailingPercent=0.35,
            parentId=parent.orderId)
        return BracketOrder(parent, takeProfit, stopLoss)
    
    def stopBracketOrderWithTp(self, c,
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float,
        stopLossPrice: float, account: str, outsideRth=True, 
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parentQuantity = quantity
        parent = LimitOrder(
            action, parentQuantity, limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        takeProfit = LimitOrder(
            reverseAction, quantity, takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        stopLoss = StopOrder(
            reverseAction, quantity, stopLossPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return BracketOrder(parent, takeProfit, stopLoss)
    
    def stopLimitBracketOrderWithTp(self, c,
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float,
        stopLossPrice: float, 
        closePos: bool, tick_val=5, outsideRth=True, 
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parentQuantity = quantity
        if closePos: parentQuantity += 1
        parent = LimitOrder(
            action, parentQuantity, limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = LimitOrder(
            reverseAction, quantity, takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        lmtPrice = stopLossPrice
        if reverseAction == 'SELL':
            lmtPrice -= tick_val
        else:
            lmtPrice += tick_val
        stopLoss = StopLimitOrder(
            reverseAction, quantity, lmtPrice,
            stopLossPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth=outsideRth,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return BracketOrder(parent, takeProfit, stopLoss)

    def limitTpBracketOrder(self, c,
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float,
        stopLossPrice: float, 
        closePos: bool, **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parentQuantity = quantity
        if closePos: parentQuantity += 1
        parent = LimitOrder(
            action, parentQuantity, limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = LimitOrder(
            reverseAction, quantity, takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        stopLoss = StopOrder(
            reverseAction, quantity, stopLossPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return BracketOrder(parent, takeProfit, stopLoss)
    
    def dynamicTrailTpBracketOrder(self, 
        action: str, quantity: float,
        limitPrice: float, stopLoss: float, 
        takeProfitPrice: float, IS_ADD: bool,
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = Order(
            orderType='LMT', action=reverseAction,
            totalQuantity=quantity,
            lmtPrice=takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        trail_perc = 1.71
        if IS_ADD: trail_perc = 0.83
        trailStopPrice = stopLoss
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            stopLossPrice = stopLoss,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = trailStopPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return BracketOrder(parent, takeProfit, stopLoss)
    
    def limitSlTrailTpBracketOrder(self, 
        action: str, quantity: float, 
        limitPrice: float,
        sl: float,
        takeProfitPrice: float, 
        minTick: float,
        fixedTrail: bool,
        account: str,
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=False,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        # trail_perc = (1 - sl/limitPrice) * 100
        # if trail_perc < 0.07: trail_perc = 0.07
        # if trail_perc < 0.73: trail_perc = 0.73
        auxPrice = abs(limitPrice - sl)
        if auxPrice < 30 and not fixedTrail:
            auxPrice = ceil_round(auxPrice * 1.08108108108, minTick)
        elif auxPrice > 50: auxPrice = 50
        # elif auxPrice > 76: auxPrice = 76
        # auxPrice = minTick * 70
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            # trailingPercent = trail_perc,
            auxPrice=auxPrice,
            trailStopPrice = sl,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=False,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        takeProfit = Order(
            orderType='LMT', action=reverseAction,
            totalQuantity=quantity,
            lmtPrice=takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth=False,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return BracketOrder(parent, stopLoss, takeProfit)
    
    def limitSlTrailMocBracketOrder(self, 
        action: str, quantity: float, 
        limitPrice: float,
        sl: float,
        minTick: float, 
        account: str,
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=False,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        # trail_perc = (1 - sl/limitPrice) * 100
        # if trail_perc < 0.07: trail_perc = 0.07
        # if trail_perc < 0.13: trail_perc = 0.13
        # if trail_perc < 0.73: trail_perc = 0.73
        auxPrice = abs(limitPrice - sl)
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            # trailingPercent = trail_perc,
            auxPrice=auxPrice,
            trailStopPrice = sl,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=False,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        moc = Order(
            orderType='MOC', action=reverseAction,
            totalQuantity=quantity,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=False,
            conditionsIgnoreRth=True,
            parentId=parent.orderId,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            account=account,
            hidden=True)
        return BracketOrder(parent, stopLoss, moc)

    def limitTpTrailBracketOrder(self, 
        action: str, quantity: float,
        limitPrice: float, takeProfitPrice: float, 
        **kwargs) -> LimitTpBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        takeProfit = Order(
            orderType='LMT', action=reverseAction,
            totalQuantity=quantity,
            lmtPrice=takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        trail_perc = 4 #12.5 #5
        trailStopPrice = limitPrice - math.ceil(limitPrice * trail_perc)*100/100
        if trailStopPrice < 0.02: trailStopPrice = 0.02
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = trailStopPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return BracketOrder(parent, takeProfit, stopLoss)

    def limitTrailBracketOrder(self, 
        action: str, quantity: float,
        limitPrice: float,  trail_perc: float,
        **kwargs) -> LimitBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = limitPrice*(1-trail_perc/100),
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return LimitBracketOrder(parent, stopLoss)

    def limitSlTrailBracketOrder(self, 
        action: str, quantity: float,
        limitPrice: float, sl: float, 
        **kwargs) -> LimitBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        trail_perc = (1 - sl/limitPrice) * 100
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            trailingPercent = trail_perc,
            trailStopPrice = sl,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)
        return LimitBracketOrder(parent, stopLoss)
    
    def limitSlFixedTrailBracketOrder(self, 
        action: str, quantity: float,
        limitPrice: float, sl: float, 
        auxPrice: float,
        account: str,
        **kwargs) -> LimitBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            auxPrice=auxPrice,
            trailStopPrice = sl,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return LimitBracketOrder(parent, stopLoss)

    def limitSlFixedTrailBracketOrderPre(self, 
        action: str, quantity: float,
        limitPrice: float, sl: float, 
        auxPrice: float,
        account: str,
        **kwargs) -> LimitBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        stopLoss = Order(
            orderType='TRAIL', action=reverseAction,
            totalQuantity=quantity,
            auxPrice=auxPrice,
            trailStopPrice = sl,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return LimitBracketOrder(parent, stopLoss)

    def limitOrder(self, 
        action: str, quantity: float,
        limitPrice: float, 
        account: str,
        **kwargs) -> LimitBracketOrder:
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return LimitSingleOrder(parent)

    def marketOrderWithTp(self, c,
        action: str, quantity: float,
        limitPrice: float, account: str, **kwargs) -> MarketBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = Order(
            orderType='LMT', action=action,
            totalQuantity=quantity,
            lmtPrice=limitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth=False,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        if action == 'BUY': takeProfitPrice = limitPrice * 10
        elif action == 'SELL': takeProfitPrice = 0.1
        takeProfit = Order(
            orderType='LMT', action=reverseAction,
            totalQuantity=quantity,
            lmtPrice=takeProfitPrice,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            parentId=parent.orderId,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return MarketBracketOrder(parent, takeProfit)

    def marketOrder(self, action: str, quantity: float,
        account: str, **kwargs) -> MarketBracketOrder:
        assert action in ('BUY', 'SELL')
        reverseAction = 'BUY' if action == 'SELL' else 'SELL'
        parent = MarketOrder(
            action=action, totalQuantity=quantity,
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=False,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            account=account,
            **kwargs)
        return MarketSingleOrder(parent)

    def HandleBuyLimit(self, symbol, vol, op, sl, tp, basicPoint):
        contract = self.GetStockContract(symbol)
        vol = int(vol)
        op = NormalizeFloat(op, basicPoint)
        if op < 11.24 and vol < 18: return 0
        high_bracket = self.limitBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitFree(self, symbol, vol, op, sl, tp, basicPoint):
        contract = self.GetStockContract(symbol)
        vol = int(vol)
        op = NormalizeFloat(op, basicPoint)
        high_bracket = self.limitBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleStopBracketOrderWithTpWithContract(self, contract, action, vol, op, sl, tp, account=''):        
        high_bracket = self.stopBracketOrderWithTp(
            contract,
            action=action, quantity=vol,
            limitPrice=op,
            takeProfitPrice=tp,
            stopLossPrice=sl,
            account=account)
        for order in high_bracket:
            print(order)
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleTrailStopBracketOrderWithTpWithContract(self, contract, action, vol, op, sl, tp, minTick, fixedTrail, account=''):
        high_bracket = self.limitSlTrailTpBracketOrder(
            action=action, quantity=vol,
            limitPrice=op,
            sl = sl,
            takeProfitPrice=tp,
            minTick=minTick,
            fixedTrail=fixedTrail,
            account=account)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def BuyOption(self, contract, vol, op, sl=0.26, account=''):
        action = 'BUY'
        auxPrice = 0.5
        sl = op - sl
        high_bracket = self.limitSlFixedTrailBracketOrder(
            action=action, quantity=vol,
            limitPrice=op, sl=sl, auxPrice=auxPrice,
            account=account)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            # self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op} sl {op-0.5}"
        print(trade)
        Alert(trade)

    def BuyOptionPre(self, contract, vol, op, account=''):
        action = 'BUY'
        auxPrice = 0.5
        sl = op - 0.26
        if sl < 0.06: sl = 0.06
        high_bracket = self.limitSlFixedTrailBracketOrderPre(
            action=action, quantity=vol,
            limitPrice=op, sl=sl, auxPrice=auxPrice,
            account=account)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            # self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op} sl {op-0.5}"
        print(trade)
        Alert(trade)

    def LimitSingleOrder(self, contract, action, vol, op, account=''):
        high_bracket = self.limitOrder(
            action=action, quantity=vol,
            limitPrice=op,
            account=account)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op}"
        print(trade)
        Alert(trade)

    def HandleTrailStopBracketOrderWithMocWithContract(self, contract, action, vol, op, sl, minTick, account=''):
        high_bracket = self.limitSlTrailMocBracketOrder(
            action=action, quantity=vol,
            limitPrice=op,
            sl=sl,
            minTick=minTick,
            account='')
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} LIMIT vol {vol} op {op} sl {sl}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitTpWithContract(self, contract, vol, op, sl, tp, closePos=False):
        high_bracket = self.limitTpBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op,
            takeProfitPrice=tp,
            stopLossPrice=sl,
            closePos=closePos)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} BUY LIMIT vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleSellLimitTpWithContract(self, contract, vol, op, sl, tp, closePos=False):
        high_bracket = self.limitTpBracketOrder(
            contract,
            action='SELL', quantity=vol,
            limitPrice=op,
            takeProfitPrice=tp,
            stopLossPrice=sl,
            closePos=closePos)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} SELL LIMIT vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleDynamicTrailTpWithContract(self, contract, action, vol, op, sl, tp, IS_ADD=False):
        op = op
        high_bracket = self.dynamicTrailTpBracketOrder(
            action=action, quantity=vol,
            limitPrice=op,
            stopLoss=sl,
            takeProfitPrice=tp,
            IS_ADD=IS_ADD)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitTrailWithContract(self, contract, vol, op):
        high_bracket = self.limitTrailBracketOrder(
            action='BUY', quantity=vol,
            limitPrice=op, trail_perc=28)
        for order in high_bracket:
            print(order)
            order_res = self.ib.placeOrder(contract=contract, order=order)
            print(order_res)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op}"
        print(trade)
        Alert(trade)
        return 1

    def HandleMarketOrder(self, contract, action, vol, account=''):
        orders = self.marketOrder(action = action, quantity = vol,
        account = account)
        for order in orders:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            # print(order_res)
            # self.ib.sleep(1)
        # print(contract,order)
        # trade = f"Submitted Market {contract.symbol} {action} vol {vol}"
        # print(trade)
        # Alert(trade)

    def PlaceOptionOrder(self, options_contract, vol):
        print(options_contract)
        bars = self.ib.reqHistoricalData(
            contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
            whatToShow='BID', useRTH=True)
        if len(bars) < 1:
            print("ERR", options_contract)
            return -1
        op = bars[-1].close+0.01
        return self.HandleBuyLimitTrailWithContract(options_contract, vol, op)

    def HandleBuyLimitTpTrailWithContract(self, contract, contractSmart, vol, tp):
        op = self.GetBidByContract(contract) + 1
        high_bracket = self.limitTpTrailBracketOrder(
            action='BUY', quantity=vol,
            limitPrice=op,
            takeProfitPrice=tp)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contractSmart, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} tp {tp}"
        print(trade)
        Alert(trade)
        
    def HandleBuyLimitTpTrail(self, symbol, vol):
        contract = self.GetStockContractJP(symbol)
        contractSmart =  self.GetStockContractSmartJP(symbol)
        
        op = self.GetBidByContract(contract) + 1
        tp = NormalizeFloat(op * 1.35, 0.1)
        high_bracket = self.limitTpTrailBracketOrder(
            action='BUY', quantity=vol,
            limitPrice=op,
            takeProfitPrice=tp)
        IS_CANCELLED = False
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contractSmart, order=order)
            self.ib.sleep(1)
            if order_res.orderStatus.status == "Cancelled":
                IS_CANCELLED = True
                print("CANNCELLED", symbol)
                break
        if IS_CANCELLED:
            self.reconnect()
            return -1
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} tp {tp}"
        print(trade)
        Alert(trade)
        return vol

    def HandleBuyLimitTrail(self, symbol, vol):
        contract = self.GetStockContractJP(symbol)
        contractSmart =  self.GetStockContractSmartJP(symbol)
        
        op = self.GetAskByContract(contract)
        high_bracket = self.limitBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contractSmart, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitCFD(self, symbol, vol, currency):
        contract = self.GetStockContract(symbol, currency)
        cfdContract = self.GetCFDContract(symbol, currency)
        op = self.GetAskByContract(contract)
        high_bracket = self.limitBracketMocOrder(
            cfdContract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=cfdContract, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op}"
        print(trade)
        Alert(trade)

    def bracketCloseOrder(self, action: str, vol: float, 
        **kwargs) -> BracketCloseOrder:

        parent = Order(
            orderType='TRAIL', action=action,
            totalQuantity=int(vol),
            trailingPercent = 4,
            orderId=self.ib.client.getReqId(),
            transmit=False,
            outsideRth = True,
            tif="GTC",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True,
            **kwargs)

        moc = Order(
            orderType='MOC', action=action,
            totalQuantity=int(vol),
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=True,
            conditionsIgnoreRth=True,
            parentId=parent.orderId,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True)
        return (parent, moc)

    def HandleMOC(self, contract, vol, action):
        contract.exchange = "SMART"
        order = Order(
            orderType='MOC', action=action,
            totalQuantity=int(vol),
            orderId=self.ib.client.getReqId(),
            transmit=True,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True)
        self.ib.placeOrder(contract=contract, order=order)
        self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} MOC vol {vol}"
        print(trade)
        Alert(trade)

    def HandleStopMOC(self, contract, vol, action):
        contract.exchange = "SMART"
        bracket = self.bracketCloseOrder(action, vol)
        for order in bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} MOC vol {vol}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitTrailUS(self, symbol, vol):
        contract = self.GetStockContract(symbol)
        contractSmart =  contract
        
        op = self.GetBidByContract(contract) + 0.01
        high_bracket = self.limitBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contractSmart, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitSlTrail(self, symbol, vol, sl, limit):
        contract = self.GetStockContractJP(symbol)
        contractSmart =  self.GetStockContractSmartJP(symbol)
        
        op = self.GetBidByContract(contract) + 1
        if op >= limit: pass
        high_bracket = self.limitSlTrailBracketOrder(
            action='BUY', quantity=vol,
            limitPrice=op,
            sl=sl)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contractSmart, order=order)
            self.ib.sleep(1)
        print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} sl {sl}"
        print(trade)
        Alert(trade)

    def HandleBuyLimitWithContract(self, contract, vol, op, sl, tp, basicPoint):
        high_bracket = self.limitBracketOrder(
            contract,
            action='BUY', quantity=vol,
            limitPrice=op)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} sl {sl} tp {tp}"
        print(trade)
        Alert(trade)

    def HandleLimitOrder(self, contract, action, vol, op, account):
        high_bracket = self.marketOrderWithTp(
            contract,
            action=action, quantity=vol,
            limitPrice=op, account=account)
        for order in high_bracket:
            order_res = self.ib.placeOrder(contract=contract, order=order)
            self.ib.sleep(1)
            print(contract,order)
        trade = f"Submitted {contract.symbol} {action} vol {vol} op {op}"
        print(trade)
        Alert(trade)

    def GetPositionsOri(self):
        return self.ib.positions()

    def GetPositions(self):
        positions = self.ib.positions()  # A list of positions, according to IB
        positionList = []
        for position in positions:
            contract = position.contract
            if contract.strike > 0: continue
            if contract.secType == 'CASH': continue
            positionList.append(position)
        return positionList

    def GetAllPositions(self):
        positions = self.ib.positions()  # A list of positions, according to IB
        positionList = []
        for position in positions:
            contract = position.contract
            if contract.secType == 'CASH': continue
            positionList.append(contract.symbol)
        return positionList

    def GetOpenTrades(self):
        trades = self.ib.openTrades()  # A list of positions, according to IB
        return trades
    
    def cancelUntriggered(self):
        positions = self.ib.positions()
        contracts = [position.contract for position in positions]
        openTrades = self.ib.openTrades()
        for trade in openTrades:
            print(trade.contract)
            if trade.order.parentId == 0 or trade.contract not in contracts:
                self.ib.cancelOrder(trade.order)
        return openTrades
    
    def CleanUp(self, contract, vol, account):
        print("CLEAN UP", vol)
        if vol > 0: action = 'SELL'
        elif vol < 0: action = 'BUY'
        else: assert False
        vol = abs(vol)
        self.HandleMarketOrder(contract, action, vol, account)
        return 1

    def GetChains(self, symbol):
        contract = self.GetStockContract(symbol)
        chains = self.ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
        return chains

    def GetOptionChains(self, contract):
        return self.ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)

    def GetOptionContract(self, symbol, expir, strike, optType):
        option_contract = Option(symbol, expir, strike, optType, 'SMART', tradingClass=symbol)
        return option_contract

    def GetAsk(self, symbol):
        try:
            day = 1
            contract = self.GetStockContract(symbol)
            data = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr=f"{day} D",
                barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
            return data[-1].close
        except: return 0

    def GetAskBidJP(self, symbol):
        contract = self.GetStockContractJP(symbol)
        ticker=self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)
        ask = ticker.ask
        bid = ticker.bid
        retryCount = 0
        while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
            print("retry")
            ticker=self.ib.reqMktData(contract, '', False, False)
            self.ib.sleep(3)
            ask = ticker.ask
            bid = ticker.bid
            retryCount += 1

        if (math.isnan(bid) or bid < 0.2):
            try:
                bid = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

                ask = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
            except:
                print("math.isnan(bid) or bid < 0.2")
                return 0, 0
        return ask, bid

    def GetAskJP(self, symbol):
        try:
            day = 1
            contract = self.GetStockContractJP(symbol)
            data = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr=f"{day} D",
                barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
            return data[-1].close
        except: return 0

    def GetAskByContract(self, contract):
        day = 1
        try:
            data = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr=f"{day} D",
                barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
            return data[-1].close
        except:
            return 0

    def GetBidByContract(self, contract):
        ticker=self.ib.reqMktData(contract, '', False, False)
        self.ib.sleep(2)
        bid = ticker.bid
        retryCount = 0
        while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
            print("retry")
            ticker=self.ib.reqMktData(contract, '', False, False)
            self.ib.sleep(3)
            bid = ticker.bid
            retryCount += 1

        if (math.isnan(bid) or bid < 0.2):
            try:
                bid = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close
            except:
                print("math.isnan(bid) or bid < 0.2")
                return 0
        return bid
    
    def GetDataNpArr(self, contract, tf, whatToShow='TRADES', useRTH=False):
        try:
            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            data = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr='3 D',
                barSizeSetting=tf, whatToShow=whatToShow, useRTH=useRTH)
            df = pd.DataFrame(data)
            df = df[['open','high','low','close','volume', 'barCount', 'date']]
        except: return []
        return df.to_numpy()
    
    def GetDataDf(self, contract, tf, whatToShow='TRADES'):
        # from datetime import datetime
        # data = self.ib.reqHistoricalData(
        #     contract, endDateTime=datetime.strptime("2024-08-12", '%Y-%m-%d'), durationStr='20 D',
        #     barSizeSetting=tf, whatToShow='TRADES', useRTH=False)
        # data = self.ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='20 D',
        #     barSizeSetting=tf, whatToShow='TRADES', useRTH=False)
        # data = self.ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='30 D',
        #     barSizeSetting=tf, whatToShow=whatToShow, useRTH=False)
        data = self.ib.reqHistoricalData(
            contract, endDateTime='', durationStr='40 D',
            barSizeSetting=tf, whatToShow=whatToShow, useRTH=False)
        # data = self.ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='8 D',
        #     barSizeSetting=tf, whatToShow=whatToShow, useRTH=False)
        # data = self.ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='360 D',
        #     barSizeSetting=tf, whatToShow=whatToShow, useRTH=False)
        df = pd.DataFrame(data)
        print(df)
        df['date'] = pd.to_datetime(df.date)
        df.set_index(df.date, inplace=True)
        df = df[['open','high','low','close', 'volume', 'barCount', 'date']]
        return df

    def GetNpData1m(self, contract):
        data = self.ib.reqHistoricalData(
                contract=contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                whatToShow='TRADES', useRTH=True)
        df = pd.DataFrame(data)
        df = df[['open','high', 'low', 'close']]
        return df.to_numpy()

    def GetData(self,contract):
        data = self.ib.reqHistoricalData(
                contract=contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                whatToShow='TRADES', useRTH=True)
        return data

    def GetData1D(self,contract):
        data = self.ib.reqHistoricalData(
                contract=contract, endDateTime='', durationStr='2 D', barSizeSetting='1 day',
                whatToShow='TRADES', useRTH=True)
        return data

    def GetUSContractDict(self, symbolList):
        contractDict = {}
        for symbol in symbolList:
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            contractDict[symbol] = contract
        return contractDict

    def CancelOrder(self, order):
        return self.ib.cancelOrder(order)
