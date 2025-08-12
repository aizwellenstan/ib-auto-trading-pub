rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolume
import numpy as np
from modules.aiztradingview import GetTradable
from modules.csvDump import DumpDict
import pickle


dataPath = "./pickle/dataArrVolume.p"
dataArr = {}
closeDict = GetTradable()

closeDict["QQQ"] = 0
closeDict["SPY"] = 0
closeDict["DIA"] = 0
closeDict["IWM"] = 0
closeDict["BRK.B"] = 0
closeDict["CAT"] = 0
closeDict["HYG"] = 0

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
def Backtest(originalSignalArr,signal2Arr,signal3Arr,
    signal4Arr,signal5Arr,signal6Arr,signal7Arr,
    signal8Arr,signal9Arr,signal10Arr,npArr):
    minLength = min(len(originalSignalArr),len(npArr),len(signal2Arr))
    signalArr = originalSignalArr[-minLength:]
    signal2Arr = signal2Arr[-minLength:]
    signal3Arr = signal3Arr[-minLength:]
    signal4Arr = signal4Arr[-minLength:]
    signal5Arr = signal5Arr[-minLength:]
    signal6Arr = signal6Arr[-minLength:]
    signal7Arr = signal7Arr[-minLength:]
    signal8Arr = signal8Arr[-minLength:]
    signal9Arr = signal9Arr[-minLength:]
    signal10Arr = signal10Arr[-minLength:]
    # signal11Arr = signal11Arr[-minLength:]
    npArr = npArr[-minLength:]
    signalVal = npArr[:,3] / signalArr[:,3]
    signal2Val = npArr[:,3] / signal2Arr[:,3]
    signal3Val = npArr[:,3] / signal3Arr[:,3]
    signal4Val = npArr[:,3] / signal4Arr[:,3]
    signal5Val = npArr[:,3] / signal5Arr[:,3]
    signal6Val = npArr[:,3] / signal6Arr[:,3]
    signal7Val = npArr[:,3] / signal7Arr[:,3]
    signal8Val = npArr[:,3] / signal8Arr[:,3]
    signal9Val = npArr[:,3] / signal9Arr[:,3]
    signal10Val = npArr[:,3] / signal10Arr[:,3]
    # signal11Val = npArr[:,3] / signal11Arr[:,3]

    balance = 1.
    maxBalance = 1.
    maxVal = 1.
    val = 1.
    maxWR = 0.
    while val < 100:
        balance = 1
        win = 0
        total = 0
        for i in range(val, minLength):
            avgSignalVal = np.sum(signalVal[i-val:i])/val
            avgSignal2Val = np.sum(signal2Val[i-val:i])/val
            avgSignal3Val = np.sum(signal3Val[i-val:i])/val
            avgSignal4Val = np.sum(signal4Val[i-val:i])/val
            avgSignal5Val = np.sum(signal5Val[i-val:i])/val
            avgSignal6Val = np.sum(signal6Val[i-val:i])/val
            avgSignal7Val = np.sum(signal7Val[i-val:i])/val
            avgSignal8Val = np.sum(signal8Val[i-val:i])/val
            avgSignal9Val = np.sum(signal9Val[i-val:i])/val
            avgSignal10Val = np.sum(signal10Val[i-val:i])/val
            # avgSignal11Val = np.sum(signal11Val[i-val:i])/val
            if (
                # signalVal[i-1] < avgSignalVal and
                # signal2Val[i-1] < avgSignal2Val and
                signal3Val[i-1] < avgSignal3Val and
                signal4Val[i-1] < avgSignal4Val and
                signal5Val[i-1] < avgSignal5Val and
                signal6Val[i-1] < avgSignal6Val and
                signal7Val[i-1] < avgSignal7Val and
                signal8Val[i-1] < avgSignal8Val and
                signal9Val[i-1] < avgSignal9Val and
                signal10Val[i-1] < avgSignal10Val
                # signal11Val[i-1] < avgSignal11Val
            ):
                tp = signalArr[i-1][3] * avgSignalVal
                tp2 = signal2Arr[i-1][3] * avgSignal2Val
                # tp3 = signal3Arr[i-1][3] * avgSignal3Val
                # tp4 = signal4Arr[i-1][3] * avgSignal4Val
                # tp5 = signal5Arr[i-1][3] * avgSignal5Val
                # tp6 = signal6Arr[i-1][3] * avgSignal6Val
                # tp7 = signal7Arr[i-1][3] * avgSignal7Val
                tp = min(tp,tp2)
                if (
                    # signalArr[i][0] > signalArr[i-1][3] and
                    # npArr[i][0] < npArr[i-1][3] and
                    npArr[i][0] < tp
                ):
                    if npArr[i][1] < tp:
                        tp = npArr[i][3]
                    gain = tp/npArr[i][0]
                    balance *= gain
                    if gain > 1:
                        win += 1
                    total += 1
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
            maxWR = win/total
        val += 1
    if maxBalance <= 1: return np.array([0.,0.,0.])
    print(maxBalance, maxVal)
    print('WR',maxWR)
    if total < 1: gainPerDay = 0
    else: gainPerDay = maxBalance/total
    res = np.array([gainPerDay,maxVal,maxWR])
    return res

def main():
    from modules.csvDump import LoadDict

    optionPath = f"{rootPath}/data/TradableOption.csv"
    tradableOption = LoadDict(optionPath, "Length")
    tradableOptionList = []
    for symbol, length in tradableOption.items():
        if length < 390: continue
        tradableOptionList.append(symbol)

    # symbolArr = ["QQQ","SQQQ","SPY","IWM",
    #         "^N225","^NDX","^GSPC","DIA",
    #         "VTI","XLV","VWO",
    #         "TZA","XLP","TNA","IAU","XLK","IEF","KRE",
    #         "UNG","VEA","JNK","IEFA","GLD","IYR",
    #         "EWJ","DRIP","XLB","GDXJ","XLRE","AGG","ARKK"
    #         ]
    # "^NDX","^GSPC","^FTSE","^GDAXI"

    signalArr = GetNpDataVolume('QQQ')[-1058:]
    signal2Arr = GetNpDataVolume('SPY')[-1058:]
    signal3Arr = GetNpDataVolume('IWM')[-1058:]
    signal4Arr = GetNpDataVolume('HYG')[-1058:]
    signal5Arr = GetNpDataVolume('AAPL')[-1058:]
    signal6Arr = GetNpDataVolume('XLP')[-1058:]
    signal7Arr = GetNpDataVolume('^N225')[-1058:]
    signal8Arr = GetNpDataVolume('^GDAXI')[-1058:]
    signal9Arr = GetNpDataVolume('SQQQ')[-1058:]
    signal10Arr = GetNpDataVolume('UVXY')[-1058:]
    gainPerDayDict = {}
    valDict = {}
    wrDict = {}
    for symbol in tradableOptionList:
        if symbol != "TSLA": continue
        npArr = GetNpDataVolume(symbol)[-1058:]
        res = Backtest(signalArr,signal2Arr,signal3Arr,signal4Arr,
            signal5Arr,signal6Arr,signal7Arr,signal8Arr,
            signal9Arr,signal10Arr,npArr)
        gainPerDay = res[0]
        if gainPerDay == 0: continue
        gainPerDayDict[symbol] = gainPerDay
        valDict[symbol] = int(res[1])
        print(symbol, gainPerDay)
    gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
    print(gainPerDayDict)
    resDict = {}
    for symbol, gainPerDay in gainPerDayDict.items():
        resDict[symbol] = valDict[symbol] 
    print(resDict)
    import sys
    sys.exit(0)
    closeDict = GetTradable()
    gainPerDayDict = {}
    # QQQ SPY DIA IWM BRK.B CAT HYG
    signalArr = ["QQQ","SPY","DIA","IWM","BRK.B","CAT","HYG"]
    # signalArr = closeDict.keys()
    # signalArr = ["MARXU"]
    # closeDict = {"MVLA":0}
    for signal in signalArr:
        if signal not in dataArr: continue
        originalSignalArr = dataArr[signal]
        originalSignalArr = originalSignalArr[-1058:]
        for symbol, close in closeDict.items():
            if symbol == 'GMBL': continue
            # if symbol == 'LIN': continue
            # if symbol == 'NVDA': continue
            if symbol not in dataArr: continue
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
