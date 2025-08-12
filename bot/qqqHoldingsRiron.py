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

def main(update=True):
    import pickle
    picklePath = f"{rootPath}/backtest/pickle/pro/compressed/riron.p"
    dataDict = {}
    if update:
        dataDict["QQQ"] = GetNpData("QQQ")[-1058:]
        for symbol, days in rironDict.items():
            dataDict[symbol] = GetNpData(symbol)[-1058:]
        pickle.dump(dataDict, open(picklePath, "wb"), protocol=-1)
    else:
        output = open(picklePath, "rb")
        dataDict = pickle.load(output)
        output.close()

    qqqArr = dataDict["QQQ"]
    signalDict = {}
    for symbol, npArr in dataDict.items():
        signalDict[symbol] = npArr[:,3] / qqqArr[:,3]

    rironPriceDict = {}
    avgSignalValDict = {}
    shift = 1
    for symbol, days in rironDict.items():
        signalVal = signalDict[symbol]
        i = len(signalVal) - shift
        avgSignalVal = np.sum(signalVal[i-days:i])/days
        riron = qqqArr[-1-shift][3] * avgSignalVal
        rironPriceDict[symbol] = riron
        avgSignalValDict[symbol] = avgSignalVal

    predict = 0
    for symbol, riron in rironPriceDict.items():
        predict += riron / avgSignalValDict[symbol]
    predict /= len(avgSignalValDict)
    
    if npArr[-shift][0] < predict:
        print('QQQ BUY')
        if npArr[-shift][3] < npArr[-shift][0]:
            print('LOSS')
main(update=False)