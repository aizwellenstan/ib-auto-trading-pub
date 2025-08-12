rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.portfolio import GetSharpeSortino
from modules.aiztradingview import GetClose
import numpy as np
from numba import njit, types
from numba.typed import Dict
import pickle

backtestLength = 252 * 3

def getData():
    npArrPicklePath = "./pickle/pro/compressed/npArrDict.p"
    mddPicklePath = "./pickle/pro/compressed/mddDict.p"
    update = False
    dataDict = {}
    mddDict = {}
    if update:
        closeDict = GetClose()
        benchmark = 'BRK.A'
        for symbol, v in closeDict.items():
            npArr = GetSharpeSortino(benchmark, symbol)
            if len(npArr) < 1: continue
            dataDict[symbol] = npArr
            mdd = npArr[0][2]
            mddDict[symbol] = mdd
        mddDict = dict(sorted(mddDict.items(), key=lambda item: item[1], reverse=True))
        print(mddDict)
        pickle.dump(npArrDict, open(npArrPicklePath, "wb"))
        print("pickle dump finished")
        pickle.dump(mddDict, open(mddPicklePath, "wb"))
        print("pickle dump finished")
    else:
        import gc
        output = open(npArrPicklePath, "rb")
        gc.disable()
        dataDict = pickle.load(output)
        output.close()
        gc.enable()
        output = open(mddPicklePath, "rb")
        gc.disable()
        mddDict = pickle.load(output)
        output.close()
        gc.enable()
    

    newDataDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])
    for k,v in dataDict.items():
        if k not in mddDict: continue
        if len(v) < backtestLength: continue
        mdd = mddDict[k]
        closeArr = v[:,3]
        gain = v[:,3]/v[:,0]
        if np.isinf(gain).any(): 
            print(k)
            continue
        mdd = mddDict[k]
        mdd = np.empty(len(v)).fill(mdd)
        print(mdd)
        v = np.c_[v[:,0], v[:,1], v[:,2], v[:,3], gain, mdd]
        newDataDict[np.unicode_(k)]=np.float32(v)
    
    mddDict = dict(sorted(mddDict.items(), key=lambda item: item[1], reverse=True))
    newMddDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32)
    for symbol, v in mddDict.items():
        newMddDict[np.unicode_(symbol)] = np.float32(mddDict[symbol])
    
    newDataDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])
    for k,v in dataDict.items():
        newDataDict[np.unicode_(k)]=np.float32(v)
    
    return newMddDict, newDataDict

mddDict, dataDict = getData()
mddList = []
for k, v in mddDict.items():
    if v in mddList: continue
    mddList.append(v)
mddList = np.float32(mddList)

# @njit
def GetDailyGain(gainList):
    if len(gainList) < 1: return 1
    vol = 1 / len(gainList)
    dailyGain = 0
    for gain in gainList:
        dailyGain += vol * gain
    return dailyGain
    
# @njit
def Backtest(dataDict, period, mddLimit):
    totalGain = 1
    for i in range(1, backtestLength):
        # maxMomentum = 2
        gain = 1
        gainList = np.empty(0)
        for symbol, npArr in dataDict.items():
            # momentum = npArr[i-1][3]/npArr[i-1-period][3]
            # if (
            #     momentum < maxMomentum and
            #     npArr[i][0] < npArr[i-1][2]
            # ):
            #     maxMomentum = momentum
            #     gain = npArr[i][4]
            if npArr[i][5] < mddLimit: continue

            gain = npArr[i][4]
            gainList = np.append(gainList, gain)
            dailyGain = GetDailyGain(gainList)
        # totalGain *= gain
        totalGain *= dailyGain
    return totalGain

# @njit
def main(mddList, mddDict, dataDict):
    maxTotalGain = 0
    minMddLimit = 0
    maxPeriod = 0
    for mddLimit in mddList:
        # newDataDict = {}
        # for symbol in dataDict.keys():
        #     if symbol not in mddDict: continue
        #     mdd = mddDict[symbol]
        #     if mdd < mddLimit: continue
        #     newDataDict[symbol] = dataDict[symbol]
        period = 1
        # while period < 252:
        totalGain = Backtest(dataDict, period, mddLimit)
        if totalGain > maxTotalGain:
            maxTotalGain = totalGain
            minMddLimit = mddLimit
            maxPeriod = period
        print(maxTotalGain,minMddLimit,maxPeriod)
        period += 1
        
        
if __name__ == '__main__':
    main(mddList, mddDict, dataDict)
