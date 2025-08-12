rootPath = "..";import sys;sys.path.append(rootPath)
import pandas as pd
from modules.data import GetDataWithVolumeDate
from numba import range

symbol = "SPY"
spyNpArr = GetDataWithVolumeDate(symbol)
csvPath = f"{rootPath}/data/option/spy_gamma.csv"
spyGammaNpArr = pd.read_csv(csvPath).to_numpy()

symbol = "QQQ"
qqqNpArr = GetDataWithVolumeDate(symbol)
csvPath = f"{rootPath}/data/option/qqq_gamma.csv"
qqqGammaNpArr = pd.read_csv(csvPath).to_numpy()

spyGammaDict = {}
for i in range(0, len(spyGammaNpArr)):
    if spyGammaNpArr[i][0] not in spyGammaDict:
        spyGammaDict[spyGammaNpArr[i][0]] = [
            [spyGammaNpArr[i][1], 
            spyGammaNpArr[i][0],spyGammaNpArr[i][2]]
        ]
    else:
        spyGammaDict[spyGammaNpArr[i][0]].append(
            [spyGammaNpArr[i][1],spyGammaNpArr[i][2], 
                spyGammaNpArr[i][3]]
        )

qqqGammaDict = {}
for i in range(0, len(qqqGammaNpArr)):
    if qqqGammaNpArr[i][0] not in qqqGammaDict:
        qqqGammaDict[qqqGammaNpArr[i][0]] = [
            [qqqGammaNpArr[i][1], 
            qqqGammaNpArr[i][0],qqqGammaNpArr[i][2]]
        ]
    else:
        qqqGammaDict[qqqGammaNpArr[i][0]].append(
            [qqqGammaNpArr[i][1],qqqGammaNpArr[i][2], 
                qqqGammaNpArr[i][3]]
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


balance = 1
ddList = []
for i in range(0, len(spyNpArr)):
    if spyNpArr[i-1][5] not in spyGammaDict: continue
    gain = spyNpArr[i][3] / spyNpArr[i][0]
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
for i in range(0, len(spyNpArr)):
    if spyNpArr[i-1][5] not in spyGammaDict: continue
    spyGammaNpArr = spyGammaDict[spyNpArr[i-1][5]]

    target = 0
    found = False
    for j in dteList:
        if found: break
        for k in range(0, len(spyGammaNpArr)):
            if j == spyGammaNpArr[k][0]:
                target = spyGammaNpArr[k][2]
                found = True
                break
    # if target < npArr[i-1][3]: continue
    if target < npArr[i][0]: continue
    close = npArr[i][3]
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
