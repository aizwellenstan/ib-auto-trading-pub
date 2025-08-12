rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
from modules.dict import take

catNpArr = GetNpData('CAT')
qqqNpArr = GetNpData('BRK-B')

print(len(catNpArr), len(qqqNpArr))

minLength = min(len(catNpArr), len(qqqNpArr))
minLength = 1050
catNpArr = catNpArr[-minLength:]
qqqNpArr = qqqNpArr[-minLength:]

from numba import njit

from modules.aiztradingview import GetClose, GetLargeCap

# @njit
def Backtest(catNpArr, qqqNpArr):
    maxBalance = 0
    maxBackDay = 0
    backDay = 253
    # while backDay < 500:
    position = 0
    balance = 2700
    for i in range(254, len(catNpArr)):
        if catNpArr[i-1][3] > catNpArr[i-1-backDay][3]:
            if position > 0: continue
            op = qqqNpArr[i][0]
            if op < 0.01: return 0
            vol = balance/op
            balance -= op * vol
            position += vol
        else:
            close = qqqNpArr[i][0]
            balance += position * close
            position = 0
        
    close = qqqNpArr[i][0]
    balance += position * close

    if balance > maxBalance:
        maxBalance = balance
        maxBackDay = backDay
        # print(maxBalance, maxBackDay)
    # backDay += 1
    return maxBalance


Backtest(catNpArr, qqqNpArr)

closeDict = GetClose()

performanceDict = {}
minLength = 1050

for symbol, marketcap in closeDict.items():
    # symbol = 'AAPL'
    npArr = GetNpData(symbol)
    if len(npArr) < 1: continue
    newCatNpArr = catNpArr
    minLength = min(len(newCatNpArr), len(npArr))
    newCatNpArr = newCatNpArr[-minLength:]
    npArr = npArr[-minLength:]
    balance = Backtest(newCatNpArr, npArr)
    if balance < 2700: 
        # print(balance)
        # MARKETCAP LIMIT 157590401947 49
        # NETINCOME LIMIT 8014000000 53
        # enterprise_value_fq LIMIT 144055000000 71
        print('MARKETCAP LIMIT',marketcap)
        # break
    performanceDict[symbol] = balance/minLength
    print(symbol, balance)
performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
performanceList = take(len(performanceDict),performanceDict)
print(performanceDict)
print(performanceList)
print(len(performanceList))
