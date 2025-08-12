rootPath = "..";import sys;sys.path.append(rootPath)
import pandas as pd
from modules.data import GetDataWithVolumeDate
from numba import range

symbol = "SPY"
npArr = GetDataWithVolumeDate(symbol)
csvPath = f"{rootPath}/data/option/spy_gamma.csv"
gammaNpArr = pd.read_csv(csvPath).to_numpy()

gammaDict = {}
for i in range(0, len(gammaNpArr)):
    if gammaNpArr[i][0] not in gammaDict:
        gammaDict[gammaNpArr[i][0]] = [
            [gammaNpArr[i][1], 
            gammaNpArr[i][0],gammaNpArr[i][2]]
        ]
    else:
        gammaDict[gammaNpArr[i][0]].append(
            [gammaNpArr[i][1],gammaNpArr[i][2], 
                gammaNpArr[i][3]]
        )

# maxArr = []
# for i in range(0, len(npArr)):
#     if npArr[i-1][5] in gammaDict:
#         gammaNpArr = gammaDict[npArr[i-1][5]]
#         maxDiff = 9
#         maxDte = 0
#         maxStrike = 0
#         for j in range(0, len(gammaNpArr)):
#             diff = abs(
#                 (gammaNpArr[j][2]-npArr[i-1][3])/npArr[i-1][3]
#             )
#             if diff < maxDiff:
#                 maxDiff = diff
#                 maxDte = gammaNpArr[j][0]
#                 maxStrike = gammaNpArr[j][2]
#         maxArr.append([npArr[i-1][5], maxDte,maxStrike])
# print(maxArr)

# dteDict = {}
# for i in range(0, len(maxArr)):
#     if maxArr[i][1] not in dteDict:
#         dteDict[maxArr[i][1]] = 1
#     else:
#         dteDict[maxArr[i][1]] += 1
# dteDict =  dict(sorted(dteDict.items(), key=lambda item: item[1], reverse=True))
# print(dteDict)


npArr2 = GetDataWithVolumeDate("symbol")
balance = 1
ddList = []
for i in range(0, len(npArr)):
    if npArr[i-1][5] not in gammaDict: continue
    gain = npArr[i][3] / npArr[i][0]
    lastBalance = balance
    balance *= gain
    if balance < lastBalance:
        ddList.append(balance/lastBalance)
ddList.sort()
print(balance)
print(ddList[0])

dteDict = {1: 180, 3: 162, 2: 129, 4: 94, 5: 20, 7: 10, 8: 9, 6: 8, 11: 5, 10: 5, 9: 4, 38: 1, 26: 1, 35: 1, 34: 1, 33: 1, 18: 1,
21: 1, 14: 1}
dteList = list(dteDict.keys())

balance = 1
ddList = []
for i in range(0, len(npArr)):
    if npArr[i-1][5] not in gammaDict: continue
    gammaNpArr = gammaDict[npArr[i-1][5]]

    target = 0
    found = False
    for j in dteList:
        if found: break
        for k in range(0, len(gammaNpArr)):
            if j == gammaNpArr[k][0]:
                target = gammaNpArr[k][2]
                found = True
                break
    # if target < npArr[i-1][3]: continue
    if target < npArr[i][0]: continue
    close = npArr[i+1][0]
    # if npArr[i][1] > target:
    #     close = target
    gain = close / npArr[i][0]
    lastBalance = balance
    balance *= gain
    if balance < lastBalance:
        ddList.append(balance/lastBalance)
ddList.sort()
print(balance)
print(ddList[0])
