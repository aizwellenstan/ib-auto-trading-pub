rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData


# @njit
def Backtest(signalNpArr, npArr):
    maxBalance = 1
    maxPeriod = 1
    oriSignalArr = signalNpArr
    oriNpArr = npArr
    period = 1
    while period < 756:
        signalNpArr = oriSignalArr[-(756+period):]
        npArr = oriNpArr[-(756+period):]
        
        balance = 1
        for i in range(period, len(npArr)):
            signalPerf = signalNpArr[i-1][3] / signalNpArr[i-period][0]
            perf = npArr[i-1][3] / npArr[i-period][0]
            if signalPerf > perf:
                target = signalPerf * npArr[i-period][0]
                if target > npArr[i][0]:
                    if target > npArr[i][1]:
                        target = npArr[i][3]
                    gain = target / npArr[i][0]
                    balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxPeriod = period
            print(maxBalance, maxPeriod)
        period += 1

signalSymbol = "XOM"
signalNpArr = GetNpData(signalSymbol)

symbol = "CVX"
npArr = GetNpData(symbol)

Backtest(signalNpArr, npArr)
