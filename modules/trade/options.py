from modules.discord import Alert
import math

def BuyOption(ib, ibc, symbol, chains, signal, vol, tp, sl=0.26, account=''):
    preivousStrike = 0
    for optionschain in chains:
        strikeList = optionschain.strikes
        if signal > 0:
            for strike in strikeList:
                if strike >= tp:
                    strike = preivousStrike
                    optionContract = ibc.GetOptionCallContract(symbol, optionschain.expirations[1], strike)
                    ticker=ib.reqMktData(optionContract, '', False, False)
                    ib.sleep(3)
                    ask = ticker.ask
                    op = ticker.bid
                    if math.isnan(op): op = ask
                    if math.isnan(ask): return 0
                    ibc.BuyOption(optionContract, vol, op, sl, account)
                    return 1
                preivousStrike = strike
        elif signal < 0:
            for strike in strikeList[::-1]:
                if strike <= tp:
                    strike = preivousStrike
                    optionContract = ibc.GetOptionPutContract(symbol, optionschain.expirations[1], strike)
                    ticker=ib.reqMktData(optionContract, '', False, False)
                    ib.sleep(3)
                    ask = ticker.ask
                    op = ticker.bid
                    if math.isnan(op): op = ask
                    if math.isnan(ask): return 0
                    ibc.BuyOption(optionContract, vol, op, sl, account)
                    return 1
                preivousStrike = strike
    return 0

def CheckCloseNaketPuts(ibc, symbol):
    positions = ibc.GetPositionsOri()
    STILL_IN_SHORT = False
    # tp = 0.71
    tp = 0.66
    for position in positions:
        if position.contract.symbol == symbol:
            if position.position < 0:
                avgCost = position.avgCost
                contract = position.contract
                ibc.qualifyContracts(contract)
                bid, ask = ibc.GetOptionPrice(contract)
                print(ask, avgCost/100 * tp, avgCost/100*0.71)
                if ask < avgCost/100 * 0.71:
                    Alert(f"SPX NakedPut 0.71 hit {ask} {avgCost/100}")
                if ask < avgCost/100 * tp:
                    if ask < avgCost/100 * 0.66:
                        Alert(f"SPX NakedPut 0.66 hit {ask} {avgCost/100} tp{avgCost/100 * 0.66}")
                    vol = abs(position.position)
                    ibc.LimitSingleOrder(contract, 'BUY', vol, bid, position.account)
                STILL_IN_SHORT = True

    if not STILL_IN_SHORT:
        for position in positions:
            contract = position.contract
            ibc.qualifyContracts(contract)
            if contract.symbol == symbol:
                if position.position > 0:
                    bid, ask = ibc.GetOptionPrice(contract)
                    print(bid, ask)
                    vol = position.position
                    ibc.LimitSingleOrder(contract, 'SELL', vol, bid, position.account)
    return 1