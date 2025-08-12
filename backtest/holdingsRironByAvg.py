rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.holdings import GetHoldings

from modules.data import GetNpData
import numpy as np

symbol = 'QQQ'
holdings = GetHoldings(symbol)
print(holdings)

total = 0
for k, v in holdings.items():
    total += v

bairitsu = 1/total
percentageDict = {}
for k, v in holdings.items():
    percentageDict[k] = v * bairitsu


# import sys
# sys.exit(0)

rironDict = {
    'GOOGL': 37,
    'GOOG': 37,
    'AMZN': 2,
    'AAPL': 53,
    'AVGO': 12,
    'META': 9,
    'MSFT': 9,
    'NVDA': 2,
    'PEP': 42,
    'TSLA': 2
}


# # @njit
def Backtest(qqqArr, dataDict):
    signalDict = {}
    for symbol, npArr in dataDict.items():
        signalDict[symbol] = npArr[:,3] / qqqArr[:,3]

    maxBalance = 1
    maxVal = 1
    val = 1
    # while val < 2:
    balance = 1
    for i in range(len(qqqArr)-55, len(qqqArr)):
        rironPriceDict = {}
        avgSignalValDict = {}
        for symbol, days in rironDict.items():
            signalVal = signalDict[symbol]
            avgSignalVal = np.sum(signalVal[i-days:i])/days
            riron = qqqArr[i-1][3] * avgSignalVal
            rironPriceDict[symbol] = riron
            avgSignalValDict[symbol] = avgSignalVal

        predict = 0
        for symbol, riron in rironPriceDict.items():
            predict += riron / avgSignalValDict[symbol]
        predict /= len(avgSignalValDict)
        op = qqqArr[i][0]
        if predict > op:
            close = qqqArr[i][3]
            if qqqArr[i][1] > predict:
                close = predict
            gain = close/op
            balance *= gain
    if balance > maxBalance:
        maxBalance = balance
        maxVal = val
        print(maxBalance, maxVal)
    # val += 0.01

def main(rironDict):
    dataDict = {}
    qqqArr = GetNpData("QQQ")[-1058:]
    for symbol, days in rironDict.items():
        dataDict[symbol] = GetNpData(symbol)[-1058:]

    Backtest(qqqArr, dataDict)

main(rironDict)