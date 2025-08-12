rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

catNpArr = GetNpData('HYG')
qqqNpArr = GetNpData('QQQ')

print(len(catNpArr), len(qqqNpArr))

minLength = min(len(catNpArr), len(qqqNpArr))
# minLength = 1050
catNpArr = catNpArr[-minLength:]
qqqNpArr = qqqNpArr[-minLength:]

from numba import njit

# @njit
def Backtest(catNpArr, qqqNpArr):
    maxBalance = 0
    maxBackDay = 0
    maxDiff = 0
    backDay = 0
    while backDay < 500:
        diff = 0
        # while diff < 1:
        position = 0
        balance = 1
        lastOP = 0
        for i in range(500, len(catNpArr)):
            if catNpArr[i-1][3] > catNpArr[i-1-backDay][0]:
                gain = qqqNpArr[i][3] / qqqNpArr[i][0]
                balance *= gain
        # close = qqqNpArr[i][0]
        # balance += position * close
        # if position > 0:
        #     profit = (close-lastOP) * position
            # print('PROFIT',profit)

        if balance > maxBalance:
            maxBalance = balance
            maxBackDay = backDay
            maxDiff = diff
            print(maxBalance, maxBackDay, maxDiff)
    # diff += 0.01
        backDay += 1

Backtest(catNpArr, qqqNpArr)
