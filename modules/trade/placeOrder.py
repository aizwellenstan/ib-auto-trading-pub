from ib_insync import *

def PlaceOrder(ib, options_contract):
    options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
    print(options_contract)
    # trade = ib.placeOrder(options_contract, options_order)
    bars = ib.reqHistoricalData(
        contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
        whatToShow='BID', useRTH=True)
    # limitOrder = LimitOrder('BUY', 1, lmtPrice=bars[-1].close+0.01,account=ib.wrapper.accounts[-1])
    
    if len(bars) < 1:
        print("ERR", options_contract)
        return -1

    limitOrder = Order(
            orderType='LMT', action='BUY',
            totalQuantity=1,
            lmtPrice=bars[-1].close+0.01,
            orderId=ib.client.getReqId(),
            transmit=True,
            outsideRth=True,
            conditionsIgnoreRth=True,
            tif="DAY",
            eTradeOnly=False,
            firmQuoteOnly=False,
            hidden=True)

    trade = ib.placeOrder(options_contract, limitOrder)
    print(trade)
    # limitOrder = LimitOrder('BUY', 1, lmtPrice=bars[-1].close-0.02,account=ib.wrapper.accounts[-1])
    # trade = ib.placeOrder(options_contract, limitOrder)
    # limitOrder = LimitOrder('BUY', 1, lmtPrice=bars[-1].close-0.03,account=ib.wrapper.accounts[-1])
    # trade = ib.placeOrder(options_contract, limitOrder)