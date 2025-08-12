rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolume
import numpy as np
from modules.aiztradingview import GetTradable, GetGainable
from modules.csvDump import DumpDict
import pickle


dataPath = "./pickle/dataArrGainable.p"
dataArr = {}
closeDict = GetGainable()

closeDict["USO"] = 0
closeDict["QQQ"] = 0
closeDict["SPY"] = 0
closeDict["DIA"] = 0
closeDict["IWM"] = 0
closeDict["BRK.B"] = 0
closeDict["CAT"] = 0
closeDict["HYG"] = 0
closeDict["SM"] = 0
closeDict["OBE"] = 0

update = False
if update:
    for symbol, close in closeDict.items():
        npArr = GetNpDataVolume(symbol)
        if len(npArr) < 1: continue
        dataArr[symbol] = npArr
        print(symbol)

    pickle.dump(dataArr, open(dataPath, "wb"))
    print("pickle dump finished")
else:
    # import gc
    output = open(dataPath, "rb")
    # gc.disable()
    dataArr = pickle.load(output)
    output.close()
    # gc.enable()

# @njit
def Backtest(originalSignalArr, npArr):
    minLength = min(len(originalSignalArr),len(npArr))
    signalArr = originalSignalArr[-minLength:]
    npArr = npArr[-minLength:]
    signalVal = npArr[:,3] / signalArr[:,3]

    balance = 1
    maxBalance = 1
    maxVal = 1
    val = 1
    while val < 100:
        balance = 1
        for i in range(val, minLength):
            avgSignalVal = np.sum(signalVal[i-val:i])/val
            if signalVal[i-1] < avgSignalVal:
                tp = signalArr[i-1][3] * avgSignalVal
                if (
                    # signalArr[i][0] > signalArr[i-1][3] and
                    # npArr[i][0] < npArr[i-1][3] and
                    npArr[i][0] < tp
                ):
                    if npArr[i][1] < tp:
                        tp = npArr[i][3]
                    gain = tp/npArr[i][0]
                    balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
        val += 1
    print(maxBalance, maxVal)
    gainPerDay = maxBalance/(minLength-maxVal)
    return gainPerDay

def main():
    closeDict = GetGainable()
    gainPerDayDict = {}
    # QQQ SPY DIA IWM BRK.B CAT HYG
    # signalArr = ["USO"]
    signalArr = closeDict.keys()
    signalArr = ["SM"]
    closeDict = {"OBE":0}
    # signalArr = ["SM"]
    # closeDict = {"OBE":0}
    # signalArr = ["ALPS"]
    # closeDict = {"GPOR":0}
    # signalArr = ["DVN"]
    # closeDict = {"OXY":0}
    for signal in signalArr:
        if signal not in dataArr: continue
        originalSignalArr = dataArr[signal]
        originalSignalArr = originalSignalArr[-1058:]
        for symbol, close in closeDict.items():
            if symbol == 'GMBL': continue
            if symbol == "EP": continue
            if symbol == "CEI": continue
            if symbol == "MXC": continue
            if symbol =="GPOR": continue
            # if symbol == 'LIN': continue
            # if symbol == 'NVDA': continue
            if symbol not in dataArr: continue
            print(symbol)
            npArr = dataArr[symbol]
            if len(npArr) < 101: continue
            gainPerDay = Backtest(originalSignalArr, npArr)
            gainPerDayDict[signal+"_"+symbol] = gainPerDay
            print(symbol, gainPerDay)
            # break
        
    gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
    newGainPerDayDict = {}
    count = 0
    for symbol, gainPerDay in gainPerDayDict.items():
        if gainPerDay == 0: continue
        newGainPerDayDict[symbol] = gainPerDay
        count += 1
        if count > 100: break
    print(newGainPerDayDict)



if __name__ == '__main__':
    main()
