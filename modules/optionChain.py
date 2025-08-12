from ib_insync import *
import pandas as pd
import json
from itertools import groupby
from operator import itemgetter
import math

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

def GetLevel(price, increment = 5):
    return int(price - (price % increment))

def GetPrice(contract):
    [ticker] = ib.reqTickers(contract)
    price = ticker.marketPrice()
    price = GetLevel(price)
    return price

def GetOptionChain(symbol, rights):
    if symbol == 'SPX':
        contract = Index('SPX')
    else:
        contract = Stock(symbol, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    price = GetPrice(contract)
    print(f"{symbol} Price {price}")
    chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
    if symbol == 'SPX': optionSymbol = 'SPXW'
    else: optionSymbol = symbol
    chain = next(c for c in chains if c.tradingClass == optionSymbol and c.exchange == 'SMART')
    if rights == ['P']:
        if symbol == 'SPX':
            strikes = [strike for strike in chain.strikes
                        if strike % 5 == 0
                        and price - 100 < strike < price]
        else:
            strikes = [strike for strike in chain.strikes
                        if strike % 1 == 0
                        and price - 10 < strike < price + 10]
    elif rights == ['C']:
        if symbol == 'SPX':
            strikes = [strike for strike in chain.strikes
                if strike % 5 == 0
                and price < strike < price + 100]
        else:
            strikes = [strike for strike in chain.strikes
                        if strike % 1 == 0
                        and price - 10 < strike < price + 10]
    else:
        if symbol == 'SPX':
            strikes = [strike for strike in chain.strikes
                if strike % 5 == 0
                and price-100 < strike < price + 100]
        else:
            strikes = [strike for strike in chain.strikes
                        if strike % 1 == 0
                        and price - 10 < strike < price + 10]
    expirations = sorted(exp for exp in chain.expirations)[:2]
    contracts = [Option(optionSymbol, expiration, strike, right, 'SMART', tradingClass=optionSymbol)
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)

    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        if math.isnan(ticker.volume): continue
        if ticker.bid > 0 and ticker.ask > 0:
            newTicker = {}
            newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
            newTicker['Strike'] = ticker.contract.strike
            newTicker['Bid'] = ticker.bid
            newTicker['Ask'] = ticker.ask
            # print(vars(ticker))
            newTicker['Right'] = ticker.contract.right
            if ticker.lastGreeks is not None:
                newTicker['Gamma'] = ticker.lastGreeks.gamma
            if ticker.modelGreeks is not None:
                newTicker['Gamma'] = ticker.modelGreeks.gamma
            newTicker['Volume'] = ticker.volume
            newTickers.append(newTicker)

    return price, newTickers

def key_func_expir(k):
    return k['Expir']

fee = 1.64
def GetBullPutCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['P'])
    chain = sorted(chain, key=key_func_expir)

    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                profit = int((sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask'])*100)-fee
                spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                if spread > strikeSpread: continue
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': spread*100-profit-fee
                    })

    return price, combination

def GetBullCallCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['C'])
    chain = sorted(chain, key=key_func_expir)

    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        print(sameExpirChain)
        step = int(strikeSpread/5)
        #ex Buy 4495 call sell 4500 call
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] < sameExpirChain[i]['Ask']:
                premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                profit = int((sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']-premium)*100)-fee
                if profit < 0: continue
                spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': premium*100-fee
                    })

    return price, combination

def GetCustomBullPutCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['P'])
    chain = sorted(chain, key=key_func_expir)

    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                profit = int((sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask'])*100)-3*fee
                if profit > 0:
                    for j in range(step+1, len(sameExpirChain)):
                        ask = sameExpirChain[j]['Ask']
                        if ask*100 < profit:
                            spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                            if spread > strikeSpread: continue
                            be = sameExpirChain[j]['Strike'] - ask - (spread-(sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask']))
                            combination.append({
                                'Expir': sameExpirChain[i-step]['Expir'],
                                'SellStrike': sameExpirChain[i-step]['Strike'],
                                'BuyStrike': sameExpirChain[i]['Strike'],
                                'CustomBuyStrike': sameExpirChain[j]['Strike'],
                                'spread': spread,
                                'profit': profit-ask*100,
                                'loss': spread*100-profit-ask*100-3*fee,
                                'ShortBE': be-0.1
                                })
    return price, combination

def GetCustomBearPutCreaditSpread(symbol, strikeSpread):
    price, putChain = GetOptionChain(symbol, ['P'])
    putChain = sorted(putChain, key=key_func_expir)
    price, callChain = GetOptionChain(symbol, ['C'])

    combination = []
    for key, value in groupby(putChain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'))
        print(sameExpirChain)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > sameExpirChain[i-step]['Bid']:
                for j in range(0, len(callChain)):
                    if callChain[j]['Expir'] != sameExpirChain[i-step]['Expir']: continue
                    premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                    loss = premium * 100 - 2 * fee
                    profit = (strikeSpread - premium) * 100 - 2 * fee
                    if profit < 0: continue
                    ask = callChain[j]['Ask']
                    if ask * 100 > profit-31: continue
                    be = callChain[j]['Strike'] + ask + (sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid'])
                    profit -= ask * 100 - fee
                    loss += ask * 100 + fee
                    spread = sameExpirChain[i]['Strike']-sameExpirChain[i-step]['Strike']
                    combination.append({
                        'Expir': sameExpirChain[i-step]['Expir'],
                        'SellStrike': sameExpirChain[i-step]['Strike'],
                        'BuyStrike': sameExpirChain[i]['Strike'],
                        'CustomBuyStrike': callChain[j]['Strike'],
                        'spread': spread,
                        'profit': profit,
                        'loss': loss,
                        'LongBE': be+0.1
                        })

    return price, combination

def GetBearCallCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['C'])
    chain = sorted(chain, key=key_func_expir)
    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'))
        print(sameExpirChain)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                premium = sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask']
                profit = premium*100-fee
                loss = (strikeSpread - premium) * 100 - fee
                if profit < 0: continue
                spread = sameExpirChain[i]['Strike']-sameExpirChain[i-step]['Strike']
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': loss
                    })
    return price, combination

def GetBullCallCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['C'])
    chain = sorted(chain, key=key_func_expir)
    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        print(sameExpirChain)
        step = int(strikeSpread/5)
        #ex Buy 4495 call sell 4500 call
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] < sameExpirChain[i]['Ask']:
                premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                profit = int((sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']-premium)*100)-fee*2
                if profit < 0: continue
                spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': premium*100-fee*2
                    })

    return price, combination

def GetCustomBearCallCreaditSpread(symbol, strikeSpread):
    price, chain = GetOptionChain(symbol, ['C'])
    chain = sorted(chain, key=key_func_expir)
    combination = []
    for key, value in groupby(chain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'))
        print(sameExpirChain)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                premium = sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask']
                profit = premium*100-fee
                if profit < 0: continue
                for j in range(step+1, len(sameExpirChain)):
                    ask = sameExpirChain[j]['Ask']
                    if ask*100 > profit: continue
                    loss = (strikeSpread - premium) * 100 - fee * 2
                    be = sameExpirChain[j]['Strike'] + ask + (strikeSpread - premium)
                    profit -= ask * 100 - fee
                    loss += ask * 100 + fee
                    spread = sameExpirChain[i]['Strike']-sameExpirChain[i-step]['Strike']
                    combination.append({
                        'Expir': sameExpirChain[i-step]['Expir'],
                        'SellStrike': sameExpirChain[i-step]['Strike'],
                        'BuyStrike': sameExpirChain[i]['Strike'],
                        'CustomBuyStrike': sameExpirChain[j]['Strike'],
                        'spread': spread,
                        'profit': profit,
                        'loss': loss,
                        'LongBE': be+0.1
                        })
    return price, combination

def GetCustomBullCallCreaditSpread(symbol, strikeSpread):
    price, callChain = GetOptionChain(symbol, ['C'])
    callChain = sorted(callChain, key=key_func_expir)
    price, putChain = GetOptionChain(symbol, ['P'])
    combination = []
    for key, value in groupby(callChain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        print(sameExpirChain)
        step = int(strikeSpread/5)
        #ex Buy 4495 call sell 4500 call
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] < sameExpirChain[i]['Ask']:
                for j in range(0, len(putChain)):
                    if putChain[j]['Expir'] != sameExpirChain[i-step]['Expir']: continue
                    premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                    profit = int((sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']-premium)*100)-fee*2
                    loss = premium*100-fee*2
                    if profit < 0: continue
                    ask = putChain[j]['Ask']
                    if ask * 100 > profit: continue
                    be = putChain[j]['Strike'] - ask - premium
                    profit -= ask * 100 - fee
                    loss += ask * 100 + fee
                    spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                    combination.append({
                        'Expir': sameExpirChain[i-step]['Expir'],
                        'SellStrike': sameExpirChain[i-step]['Strike'],
                        'BuyStrike': sameExpirChain[i]['Strike'],
                        'spread': spread,
                        'profit': profit,
                        'loss': loss,
                        'ShortBE': be
                        })

    return price, combination

def GetPut(price, chain):
    combination = []
    for i in range(0, len(chain)):
        be = chain[i]['Strike'] - chain[i]['Ask']
        combination.append({
            'Expir': chain[i]['Expir'],
            'BuyStrike': chain[i]['Strike'],
            'loss': chain[i]['Ask']*100+fee,
            'ShortBE': be-0.1
            })
    return price, combination

def GetCall(price, chain):
    combination = []
    for i in range(0, len(chain)):
        be = chain[i]['Strike'] + chain[i]['Ask']
        combination.append({
            'Expir': chain[i]['Expir'],
            'BuyStrike': chain[i]['Strike'],
            'loss': chain[i]['Ask']*100-fee,
            'LongBE': be + 0.1
            })
    return price, combination

def GetBearCallLadder(symbol):
    price, callChain = GetOptionChain(symbol, ['C'])
    callChain = sorted(callChain, key=key_func_expir)
    combination = []
    for key, value in groupby(callChain, key_func_expir):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        print(sameExpirChain)
        step = int(strikeSpread/5)
        #ex Buy 4495 call sell 4500 call
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] < sameExpirChain[i]['Ask']:
                premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                profit = int((sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']-premium)*100)-fee*2
                loss = premium*100-fee*2
                if profit < 0: continue
                ask = putChain[j]['Ask']
                if ask * 100 > profit: continue
                be = putChain[j]['Strike'] - ask - premium
                profit -= ask * 100 - fee
                loss += ask * 100 + fee
                spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': loss,
                    'ShortBE': be
                    })

    return price, combination

# def GetHighestVol(symbol):
#     price, chain = GetOptionChain(symbol, ['P','C'])
#     maxCallVol = 0
#     maxCallStrike = 0
#     maxPutVol = 0
#     maxPutStrike = 0
#     for contract in chain:
#         if contract['Right'] == 'C':
#             if contract['Volume'] > maxCallVol:
#                 maxCallVol = contract['Volume']
#                 maxCallStrike = contract['Strike']
#         else:
#             if contract['Volume'] > maxPutVol:
#                 maxPutVol = contract['Volume']
#                 maxPutStrike = contract['Strike']
#     return price, maxCallStrike, maxPutStrike

import operator
def GetSupportResistance(symbol):
    price, chain = GetOptionChain(symbol, ['P','C'])
    maxCallVol = 0
    maxCallStrike = 0
    maxPutVol = 0
    maxPutStrike = 0

    callDict = {}
    putDict = {}
    for contract in chain:
        if contract['Right'] == 'C':
            callDict[contract['Strike']] = contract['Volume']
            if contract['Volume'] > maxCallVol:
                maxCallVol = contract['Volume']
                maxCallStrike = contract['Strike']
        else:
            putDict[contract['Strike']] = contract['Volume']
            if contract['Volume'] > maxPutVol:
                maxPutVol = contract['Volume']
                maxPutStrike = contract['Strike']
    callDict = sorted(callDict.items(), key=operator.itemgetter(1), reverse=True)
    putDict = sorted(putDict.items(), key=operator.itemgetter(1), reverse=True)

    resistanceList = []
    supportList = []
    if maxCallStrike > 0:
        resistanceList = [maxCallStrike]
        supportList = [maxPutStrike]
    lastHigh = 9999
    lastLow = 0
    for key, value in callDict:
        if key > lastHigh: continue
        else: lastHigh = key
        if key < maxCallStrike and key >= price:
            resistanceList.append(key)
    for key, value in putDict:
        if key < lastLow: continue
        else: lastLow = key
        if key > maxPutStrike and key <= price:
            supportList.append(key)
    return price, resistanceList, supportList

def GetAllPut(symbol):
    price, chain = GetOptionChain(symbol,['P'])
    return GetPut(price, chain)

def GetAllCall(symbol):
    price, chain = GetOptionChain(symbol,['C'])
    return GetCall(price, chain)

def GetSPXPut():
    price, chain = GetOptionChain('SPX',['P'])
    return GetPut(price, chain)

def GetSPXCall():
    price, chain = GetOptionChain('SPX',['C'])
    return GetCall(price, chain)

def GetSPYPut():
    price, chain = GetOptionChain('SPY',['P'])
    return GetPut(price, chain)

def GetSPYCall():
    price, chain = GetOptionChain('SPY',['C'])
    return GetCall(price, chain)

def GetQQQPut():
    price, chain = GetOptionChain('QQQ',['P'])
    return GetPut(price, chain)

def GetQQQCall():
    price, chain = GetOptionChain('QQQ',['C'])
    return GetCall(price, chain)

def GetDIAPut():
    price, chain = GetOptionChain('DIA',['P'])
    return GetPut(price, chain)

def GetDIACall():
    price, chain = GetOptionChain('DIA',['C'])
    return GetCall(price, chain)

def GetSPXBullPutCreaditSpread(spread=5):
    return GetBullPutCreaditSpread('SPX', spread)

def GetSPXBullCallCreaditSpread(spread=5):
    return GetBullCallCreaditSpread('SPX', spread)

def GetSPXBearCallCreaditSpread(spread=5):
    return GetBearCallCreaditSpread('SPX', spread)

def GetSPXCustomBullPutCreaditSpread(spread=5):
    return GetCustomBullPutCreaditSpread('SPX', spread)

def GetSPXCustomBearPutCreaditSpread(spread=5):
    return GetCustomBearPutCreaditSpread('SPX', spread)

def GetSPXCustomBearCallCreaditSpread(spread=5):
    return GetCustomBearCallCreaditSpread('SPX', spread)

def GetSPXCustomBullCallCreditSpread(spread=5):
    return GetCustomBullCallCreaditSpread('SPX', spread)
