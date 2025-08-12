from ib_insync import *
import pandas as pd
import json
# util.startLoop()

# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=2)

# spx = Index('SPX', 'CBOE')
# ib.qualifyContracts(spx)

# ib.reqMarketDataType(4)

# [ticker] = ib.reqTickers(spx)

# spxValue = ticker.marketPrice()

# print(spxValue)

# chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)

# print(util.df(chains))

# chain = next(c for c in chains if c.tradingClass == 'SPX' and c.exchange == 'SMART')

# strikes = [strike for strike in chain.strikes
#         if strike % 5 == 0
#         and spxValue - 20 < strike < spxValue + 20]
# expirations = sorted(exp for exp in chain.expirations)[:3]
# # print(expirations)
# rights = ['P', 'C']

# contracts = [Option('SPX', expiration, strike, right, 'SMART', tradingClass='SPX')
#         for right in rights
#         for expiration in expirations
#         for strike in strikes]

# contracts = ib.qualifyContracts(*contracts)

# tickers = ib.reqTickers(*contracts)

# print(tickers)

# newTickers = []
# for ticker in tickers:
# 	newTicker = {}
# 	newTicker['expir'] = ticker.contract.lastTradeDateOrContractMonth
# 	newTicker['strike'] = ticker.contract.strike
# 	newTicker['bid'] = ticker.bid
# 	newTicker['ask'] = ticker.ask
# 	newTickers.append(newTicker)

# df = pd.DataFrame(newTickers)
# for col in df.columns:
#     print(col)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(df)

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3)
spx = Index('SPX')
ib.qualifyContracts(spx)

def GetLevel(price, increment = 5):
    rounded = int(price - (price % increment))

    return rounded

def GetSPXPrice():
    [ticker] = ib.reqTickers(spx)
    price = ticker.marketPrice()
    # price = ticker.last
    price = GetLevel(price)
    return price

fee = 3.28

def GetSPXPutOptionChain():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    # strikes = [strike for strike in chain.strikes
    # 		if strike % 5 == 0
    # 		and spxValue - 20 < strike < spxValue + 20]
    # expirations = sorted(exp for exp in chain.expirations)[:3]
    # rights = ['P', 'C']
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue - 100 < strike < spxValue]
    expirations = sorted(exp for exp in chain.expirations)[:5]

    # expirations = sorted(exp for exp in chain.expirations)[:12]
    # expirations = sorted(exp for exp in chain.expirations)[:9]
    # expirations = sorted(exp for exp in chain.expirations)[:1]
    rights = ['P']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        if ticker.bid > 0 and ticker.ask > 0:
            newTicker = {}
            newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
            newTicker['Strike'] = ticker.contract.strike
            newTicker['Bid'] = ticker.bid
            newTicker['Ask'] = ticker.ask
            newTickers.append(newTicker)

    # keyValList = [expir]
    # expectedResult = [d for d in newTickers if d['expir'] in keyValList]
    return newTickers

from itertools import groupby

# define a fuction for key
def key_func(k):
    return k['Expir']

from operator import itemgetter
def GetSPXBullPutCreaditSpread(strikeSpread):
    chain = GetSPXPutOptionChain()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                profit = int((sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask'])*100)-fee
                spread = sameExpirChain[i-step]['Strike']-sameExpirChain[i]['Strike']
                combination.append({
                    'Expir': sameExpirChain[i-step]['Expir'],
                    'SellStrike': sameExpirChain[i-step]['Strike'],
                    # 'SellBid':sameExpirChain[i-1]['Bid'],
                    # 'SellAsk':sameExpirChain[i-1]['Ask'],
                    # 'BuyBid':sameExpirChain[i]['Bid'],
                    # 'BuyAsk':sameExpirChain[i]['Ask'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'spread': spread,
                    'profit': profit,
                    'loss': spread*100-profit-fee
                    })

    return combination

def GetSPXCallOptionChain():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue + 100 > strike > spxValue]
    expirations = sorted(exp for exp in chain.expirations)[:11]
    rights = ['C']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)

    return newTickers

def GetSPXBullCallCreaditSpread(strikeSpread):
    chain = GetSPXCallOptionChain()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
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

    return combination

def GetSPXCustomBullPutCreaditSpread(strikeSpread):
    chain = GetSPXPutOptionChain()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i-step]['Bid'] > sameExpirChain[i]['Ask']:
                profit = int((sameExpirChain[i-step]['Bid']-sameExpirChain[i]['Ask'])*100)-2*fee
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
                                'loss': spread*100-profit-ask*100-1.5*fee,
                                'ShortBE': be-0.1
                                })

    return combination

def GetSPXCallOptionChainHigher():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue < strike < spxValue + 100]
    expirations = sorted(exp for exp in chain.expirations)[:11]
    rights = ['C']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)

    return newTickers

def GetSPXPutOptionChainHigher():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue < strike < spxValue + 100]
    expirations = sorted(exp for exp in chain.expirations)[:11]
    rights = ['P']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)

    return newTickers

def GetSPXBearCallCreaditSpread(strikeSpread):
    chain = GetSPXCallOptionChainHigher()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
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

    return combination

def GetSPXBearPutCreaditSpread(strikeSpread):
    chain = GetSPXPutOptionChainHigher()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'))
        print(sameExpirChain)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > sameExpirChain[i-step]['Bid']:
                premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                loss = premium * 100 - fee
                profit = (strikeSpread - premium) * 100 - fee
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

    return combination

def GetSPXCustomBearPutCreaditSpread(strikeSpread):
    chain = GetSPXPutOptionChainHigher()
    chain = sorted(chain, key=key_func)

    callChain = GetSPXCallOptionChainHigher()

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'))
        print(sameExpirChain)
        step = int(strikeSpread/5)
        for i in range(step, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > sameExpirChain[i-step]['Bid']:
                for j in range(step+1, len(callChain)):
                    if callChain[j]['Expir'] != sameExpirChain[i-step]['Expir']: continue
                    premium = sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid']
                    loss = premium * 100 - 1.5 * fee
                    profit = (strikeSpread - premium) * 100 - fee
                    if profit < 0: continue
                    ask = callChain[j]['Ask']
                    if ask*100 > profit: continue
                    be = callChain[j]['Strike'] + ask + (sameExpirChain[i]['Ask']-sameExpirChain[i-step]['Bid'])
                    profit -= ask*100-fee*0.5
                    loss -= ask*100
                    spread = sameExpirChain[i]['Strike']-sameExpirChain[i-step]['Strike']
                    combination.append({
                        'Expir': sameExpirChain[i-step]['Expir'],
                        'SellStrike': sameExpirChain[i-step]['Strike'],
                        'BuyStrike': sameExpirChain[i]['Strike'],
                        'spread': spread,
                        'profit': profit,
                        'loss': loss,
                        'LongBE': callChain[j]['Strike']+0.1
                        })

    return combination


def GetSPXCallOptionChainAll():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue - 100 < strike < spxValue]
    expirations = sorted(exp for exp in chain.expirations)[:11]
    rights = ['C']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)

    return newTickers

def GetSPXCall():
    chain = GetSPXCallOptionChainAll()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        for i in range(0, len(sameExpirChain)):
            be = sameExpirChain[i]['Strike'] + sameExpirChain[i]['Ask']
            combination.append({
                'Expir': sameExpirChain[i]['Expir'],
                'BuyStrike': sameExpirChain[i]['Strike'],
                'loss': sameExpirChain[i]['Ask']*100-fee,
                'LongBE': be + 0.1
                })

    return combination

def GetSPXPutOptionChainAll():
    spxValue = GetSPXPrice()
    print(f"SPX Price {spxValue}")
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and spxValue - 100 < strike]
    expirations = sorted(exp for exp in chain.expirations)[:11]
    rights = ['P']
    contracts = [Option('SPXW', expiration, strike, right, 'SMART', tradingClass='SPXW')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)
    return newTickers

def GetSPXPut():
    chain = GetSPXPutOptionChain()
    chain = sorted(chain, key=key_func)

    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        for i in range(0, len(sameExpirChain)):
            be = sameExpirChain[i]['Strike'] - sameExpirChain[i]['Ask']
            combination.append({
                'Expir': sameExpirChain[i]['Expir'],
                'BuyStrike': sameExpirChain[i]['Strike'],
                'loss': sameExpirChain[i]['Ask']*100+fee,
                'ShortBE': be-0.1
                })

    return combination

dia = Contract(secType='STK', conId=73128548, symbol='DIA', exchange='SMART', primaryExchange='ARCA', currency='USD', localSymbol='DIA', tradingClass='DIA')

def GetDIAPrice():
    [ticker] = ib.reqTickers(dia)
    price = ticker.marketPrice()
    price = GetLevel(price, 1)
    return price

def GetDIAPutOptionChain():
    diaValue = GetDIAPrice()
    print(f"DIA Price {diaValue}")
    chains = ib.reqSecDefOptParams(dia.symbol, '', dia.secType, dia.conId)
    chain = next(c for c in chains if c.tradingClass == 'DIA' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 1 == 0
            and diaValue - 10 < strike < diaValue + 10]
    expirations = sorted(exp for exp in chain.expirations)[:2]
    rights = ['P']
    contracts = [Option('DIA', expiration, strike, right, 'SMART', tradingClass='DIA')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)
    return newTickers

def GetDIAPut():
    chain = GetDIAPutOptionChain()
    chain = sorted(chain, key=key_func)
    diaValue = GetDIAPrice()
    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        for i in range(0, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > 0:
                be = sameExpirChain[i]['Strike'] - sameExpirChain[i]['Ask']
                combination.append({
                    'Expir': sameExpirChain[i]['Expir'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'loss': sameExpirChain[i]['Ask']*100-fee,
                    'ShortBE': be
                    })

    return combination

qqq = Stock('QQQ', 'SMART', 'USD')
ib.qualifyContracts(qqq)
def GetQQQPrice():
    [ticker] = ib.reqTickers(qqq)
    price = ticker.marketPrice()
    price = GetLevel(price, 1)
    return price

def GetQQQPutOptionChain():
    qqqValue = GetQQQPrice()
    print(f"QQQ Price {qqqValue}")
    chains = ib.reqSecDefOptParams(qqq.symbol, '', qqq.secType, qqq.conId)
    chain = next(c for c in chains if c.tradingClass == 'QQQ' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 1 == 0
            and qqqValue - 90 < strike < qqqValue + 90]
    expirations = sorted(exp for exp in chain.expirations)[:2]
    rights = ['P']
    contracts = [Option('QQQ', expiration, strike, right, 'SMART', tradingClass='QQQ')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)
    return newTickers

def GetQQQPut():
    chain = GetQQQPutOptionChain()
    chain = sorted(chain, key=key_func)
    qqqValue = GetQQQPrice()
    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        for i in range(0, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > 0:
                be = sameExpirChain[i]['Strike'] - sameExpirChain[i]['Ask']
                if be < qqqValue + 0.2: continue
                combination.append({
                    'Expir': sameExpirChain[i]['Expir'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'loss': sameExpirChain[i]['Ask']*100-fee,
                    'ShortBE': be
                    })

    return combination

spy = Stock('SPY', 'SMART', 'USD')
ib.qualifyContracts(spy)
def GetSPYPrice():
    [ticker] = ib.reqTickers(spy)
    price = ticker.marketPrice()
    price = GetLevel(price, 1)
    return price

def GetSPYPutOptionChain():
    spyValue = GetSPYPrice()
    print(f"SPY Price {spyValue}")
    chains = ib.reqSecDefOptParams(spy.symbol, '', spy.secType, spy.conId)
    chain = next(c for c in chains if c.tradingClass == 'SPY' and c.exchange == 'SMART')
    strikes = [strike for strike in chain.strikes
            if strike % 1 == 0
            and spyValue - 70 < strike < spyValue + 70]
    expirations = sorted(exp for exp in chain.expirations)[:2]
    rights = ['P']
    contracts = [Option('SPY', expiration, strike, right, 'SMART', tradingClass='SPY')
            for right in rights
            for expiration in expirations
            for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    newTickers = []
    for ticker in tickers:
        newTicker = {}
        newTicker['Expir'] = ticker.contract.lastTradeDateOrContractMonth
        newTicker['Strike'] = ticker.contract.strike
        newTicker['Bid'] = ticker.bid
        newTicker['Ask'] = ticker.ask
        newTickers.append(newTicker)
    return newTickers

def GetSPYPut():
    chain = GetSPYPutOptionChain()
    chain = sorted(chain, key=key_func)
    spyValue = GetSPYPrice()
    combination = []
    for key, value in groupby(chain, key_func):
        sameExpirChain = list(value)
        sameExpirChain = sorted(sameExpirChain, key=itemgetter('Strike'), reverse=True)
        for i in range(0, len(sameExpirChain)):
            if sameExpirChain[i]['Ask'] > 0:
                be = sameExpirChain[i]['Strike'] - sameExpirChain[i]['Ask']
                if be < spyValue + 0.2: continue
                combination.append({
                    'Expir': sameExpirChain[i]['Expir'],
                    'BuyStrike': sameExpirChain[i]['Strike'],
                    'loss': sameExpirChain[i]['Ask']*100-fee,
                    'ShortBE': be
                    })

    return combination

# chain = GetSPXPutOptionChain()
# print(chain)
# combination = GetSPXBullPutCreaditSpread(5)
# print(combination)

# combination = GetSPXBullCallCreaditSpread(5)
# print(combination)

# combination = GetSPXCustomBullPutCreaditSpread(5)
# print(combination)