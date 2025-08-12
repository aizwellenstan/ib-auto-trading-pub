from yahoo_fin import options
import pandas as pd
import yfinance as yf
import json

# # gets the data for nearest upcoming expiration date
# chain = options.get_options_chain("^SPX", "04/06/2022")

# puts = chain['puts']
# df = pd.DataFrame(puts)
# for col in df.columns:
#     print(col)
# df = df[['Strike','Bid','Ask']]
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(df)

def GetLevel(price):
    increment = 5
    rounded = int(price - (price % increment))

    return rounded

def GetSPXPrice():
    stockInfo = yf.Ticker("^SPX")
    hist = stockInfo.history(period="7d",interval = "1m",prepost = True)
    print(hist.iloc[-1])
    price = hist.iloc[-1]['Close']
    price = GetLevel(price)

    return price

def GetSPXPutOptionChain(expir):
    price = GetSPXPrice()
    chain = options.get_options_chain("^SPX", expir)
    puts = chain['puts']
    puts = puts.loc[puts['Strike'] < price]
    puts = puts[['Strike','Bid','Ask']]
    puts = puts.loc[(puts['Ask'] > 0) & (puts['Bid'] > 0)]
    puts = json.loads(puts.to_json(orient = 'records'))
    return puts

def GetSPXCreaditSpread(expir,strikeSpread):
    chain = GetSPXPutOptionChain(expir)
    chain = chain[::-1]
    normalChain = [chain[0]]
    combination = []
    for i in range(1, len(chain)):
        if chain[i-1]['Bid'] > chain[i]['Ask']:
            normalChain.append(chain[i])
            profit = int((chain[i-1]['Bid']-chain[i]['Ask'])*100)
            spread = chain[i-1]['Strike']-chain[i]['Strike']
            combination.append({
                'SellStrike': chain[i-1]['Strike'],
                'BuyStrike': chain[i]['Strike'],
                'spread': spread,
                'profit': profit,
                'loss': spread*100-profit
            })
    chain = normalChain
    spreadRange = normalChain[0]['Strike'] - normalChain[-1]['Strike']
    # print(combination)
    # print(spreadRange)
    # strikeDiff = normalChain[0]['Strike'] - normalChain[1]['Strike']

    # spreadRangeStart = 10
    # while spreadRangeStart < spreadRange:
    #     spreadRangeStart += strikeDiff

    if strikeSpread >= 10:
        strikeSelect = 2
        for i in range(strikeSelect, len(chain)):
            profit = int((chain[i-strikeSelect]['Bid']-chain[i]['Ask'])*100)
            spread = chain[i-strikeSelect]['Strike']-chain[i]['Strike']
            combination.append({
                'SellStrike': chain[i-strikeSelect]['Strike'],
                'BuyStrike': chain[i]['Strike'],
                'spread': spread,
                'profit': profit,
                'loss': spread*100-profit
            })

    if strikeSpread >= 15:
        strikeSelect = 3
        for i in range(strikeSelect, len(chain)):
            profit = int((chain[i-strikeSelect]['Bid']-chain[i]['Ask'])*100)
            spread = chain[i-strikeSelect]['Strike']-chain[i]['Strike']
            combination.append({
                'SellStrike': chain[i-strikeSelect]['Strike'],
                'BuyStrike': chain[i]['Strike'],
                'spread': spread,
                'profit': profit,
                'loss': spread*100-profit
            })

    if strikeSpread >= 20:
        strikeSelect = 4
        for i in range(strikeSelect, len(chain)):
            profit = int((chain[i-strikeSelect]['Bid']-chain[i]['Ask'])*100)
            spread = chain[i-strikeSelect]['Strike']-chain[i]['Strike']
            combination.append({
                'SellStrike': chain[i-strikeSelect]['Strike'],
                'BuyStrike': chain[i]['Strike'],
                'spread': spread,
                'profit': profit,
                'loss': spread*100-profit
            })

    if strikeSpread >= 25:
        strikeSelect = 5
        for i in range(strikeSelect, len(chain)):
            profit = int((chain[i-strikeSelect]['Bid']-chain[i]['Ask'])*100)
            spread = chain[i-strikeSelect]['Strike']-chain[i]['Strike']
            combination.append({
                'SellStrike': chain[i-strikeSelect]['Strike'],
                'BuyStrike': chain[i]['Strike'],
                'spread': spread,
                'profit': profit,
                'loss': spread*100-profit
            })

    return combination

# combination = GetSPXCreaditSpread("04/08/2022")
# print(combination)