rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDataLts

import numpy as np

# # @njit
def Backtest(qqqNpArr, spyNpArr):
    balance = 1
    npArr = qqqNpArr
    for i in range(1, len(npArr)):
        ratio = qqqNpArr[0:i][:,3] / spyNpArr[0:i][:,3]
        mean = np.mean(ratio)
        print(ratio[-1])
        if ratio[-1] > mean:
            npArr = spyNpArr
        else:
            npArr = qqqNpArr
        gain = npArr[i][3] / npArr[i][0]
        balance *= gain
    return balance

dataDict = {}
symbolList = ["QQQ", "SPY", "^TNX", "BRK-B", "IWM", "DIA"]
for symbol in symbolList:
    dataDict[symbol] = GetDataLts(symbol)

qqqNpArr = dataDict["QQQ"]
spyNpArr = dataDict["SPY"]

# 1.3330136434043027 QQQ
res = Backtest(qqqNpArr, spyNpArr)
print(res)