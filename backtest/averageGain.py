rootPath = ".."
import sys
sys.path.append(rootPath)
import pickle
import modules.aiztradingview as aiztradingview

import numpy as np

closeJPDict = aiztradingview.GetCloseJPTradable()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = aiztradingview.GetCloseTradable()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"

update = False
if update:
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpData(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

    for symbol, close in closeDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpData(symbol)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    pickle.dump(dataDict, open(picklePath, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(picklePath, "rb")
    dataDict = pickle.load(output)
    output.close()

# @njit
def Backtest(npArr, buyAtClose=False):
    if len(npArr) < 756: return 0
    # npArr = npArr[-756:]
    npArr = npArr[-252:]
    wins = np.empty(0)
    losses = np.empty(0)
    noVolCount = 0
    for i in range(1, len(npArr)):
        if not buyAtClose:
            if npArr[i][3] > npArr[i][0]:
            # if npArr[i][3] > npArr[i][0]:
                start = 1
                end =1/npArr[i][0]*npArr[i][3]
                res = end-start
                wins = np.append(wins, res)
            else:
                start = 1
                end = 1/npArr[i][0]*npArr[i][3]
                res = end-start
                losses = np.append(losses, res)
        else:
            if npArr[i][0] > npArr[i-1][3]:
            # if npArr[i][3] > npArr[i][0]:
                start = 1
                end =1/npArr[i-1][3]*npArr[i][0]
                res = end-start
                wins = np.append(wins, res)
            else:
                start = 1
                end = 1/npArr[i-1][3]*npArr[i][0]
                res = end-start
                losses = np.append(losses, res)
    total = len(wins) + len(losses)
    avgWin = np.mean(wins) if len(wins) > 0 else 0
    avgLoss = np.mean(losses) if len(losses) > 0 else 0
    avgGain = (len(wins) * avgWin + len(losses) * avgLoss) / total if total > 0 else 0
    print(avgGain)
    # print("AvgWin:", avgWin)
    # print("AvgLoss:", avgLoss)
    # print("Win%:", len(wins) / total)
    # print("Loss%:", len(losses) / total)
    # print("Toal:", len(wins)+len(losses))
    return avgGain

avgGainDict = {}
big = ["AAPL","MSFT","AMZN","TSLA"]

for symbol, close in closeDict.items():
    if symbol not in dataDict: continue
    # if symbol not in big: continue
    # if symbol != "AAPL": continue
    npArr = dataDict[symbol]
    avgGain = Backtest(npArr)
    if avgGain != 0:
        avgGainDict[symbol] = avgGain
    avgGain = Backtest(npArr, True)
    if avgGain != 0:
        avgGainDict[symbol+"_buyAtClose"] = avgGain

# for symbol, close in closeJPDict.items():
#     if symbol not in dataDictJP: continue
#     # if symbol != "9101": continue
#     npArr = dataDictJP[symbol]
#     avgGain = Backtest(npArr)
#     if avgGain != 0:
#         avgGainDict[symbol] = avgGain
#     avgGain = Backtest(npArr, True)
#     if avgGain != 0:
#         avgGainDict[symbol+"_buyAtClose"] = avgGain

avgGainDict = dict(sorted(avgGainDict.items(), key=lambda item: item[1], reverse=True))
# print(avgGainDict)
newAvgGainDict = {}

count = 0
for k, v in avgGainDict.items():
    newAvgGainDict[k] = avgGainDict[k]
    count += 1
    if count > 50: break
print(newAvgGainDict)