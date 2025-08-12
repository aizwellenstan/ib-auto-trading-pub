import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.data import GetDataWithVolumeDate
from modules.cnn import GetFear, GetStrength

def backtest(qqq, fear, attrList, reverse=False):
    maxBalance = 1
    maxBuyAttr = 0
    maxSellAttr = 0
    position = 0
    op = 0
    for j in range(0, len(attrList)):
        buyAttr = attrList[j]
        for k in range(j+1, len(attrList)):
            sellAttr = attrList[k]
            balance = 1
            for i in range(1, len(qqq)):
                if not reverse:
                    if position < 1:
                        if fear[i-1] < buyAttr:
                            position = 1
                            op = npArr[i][0]
                    elif fear[i-1] > sellAttr:
                        gain = npArr[i][0] / op
                        balance *= gain
                        position = 0
                else:
                    if position < 1:
                        if fear[i-1] > sellAttr:
                            position = 1
                            op = npArr[i][0]
                    elif fear[i-1] < buyAttr:
                        gain = npArr[i][0] / op
                        balance *= gain
                        position = 0
            if balance > maxBalance:
                maxBalance = balance
                maxBuyAttr = buyAttr
                maxSellAttr = sellAttr
                print(maxBalance, maxBuyAttr, maxSellAttr)

npArr = GetDataWithVolumeDate("QQQ")[-252:]

position = 0
fear = GetStrength()
attrList = fear
attrList.sort()

backtest(npArr, fear, attrList, False)

