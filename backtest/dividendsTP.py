rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDataWithDividends

from modules.aiztradingview import GetCloseJP, GetClose
from modules.csvDump import DumpCsv, LoadCsv

# @njit
def Backtest(npArr):
    npArr = npArr[-1082:]
    maxBalance = 1
    maxVal = 0
    val = 1
    while val < 200:
        balance = 1
        position = 0
        op = 0
        lastDividend = 0
        for i in range(1, len(npArr)):
            if position < 1:
                dividend = npArr[i-1][4]
                if dividend > 0:
                    lastDividend = dividend
                    op = npArr[i][0]
                    position = 1
            else:
                tp = op + lastDividend * val
                if npArr[i][1] > tp:
                    gain = tp/op
                    balance *= gain
                    position = 0
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
            # print(maxBalance, maxVal)
        val += 1
    return maxBalance

gainDict = {}

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeDividends.csv"

ignoreList = LoadCsv(ignorePath)
noTradeList = LoadCsv(noTradePath)
closeJP = GetCloseJP()
for symbol, clsoe in closeJP.items():
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    # npArr = GetDataWithDividends(symbol)
    npArr = GetDataWithDividends(symbol, "JPY")
    if len(npArr) < 1:
        ignoreList.append(symbol)
        continue
    balance = Backtest(npArr)
    if balance <= 1: 
        noTradeList.append(symbol)
        continue
    gainDict[symbol] = balance
    print(symbol, balance)

close = GetClose()
for symbol, clsoe in close.items():
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    npArr = GetDataWithDividends(symbol)
    if len(npArr) < 1:
        ignoreList.append(symbol)
        continue
    balance = Backtest(npArr)
    if balance <= 1: 
        noTradeList.append(symbol)
        continue
    gainDict[symbol] = balance
    print(symbol, balance)


DumpCsv(ignorePath, ignoreList)
DumpCsv(noTradePath, noTradeList)
    
gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
print(gainDict)

newGainDict = {}
count = 0
for symbol, gain in gainDict.items():
    newGainDict[symbol] = gain
    count += 1
    if count > 50: break
print(newGainDict)