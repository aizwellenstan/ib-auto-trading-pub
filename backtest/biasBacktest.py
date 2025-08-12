rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
import pickle

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = GetClose()
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
def GetNoVolCount(npArr):
    npArr = npArr[-756:]
    noVolCount = 0
    for i in range(26, len(npArr)):
        if (
            npArr[i][0] == npArr[i][3]
        ):
            noVolCount += 1
    return noVolCount

gainPath = f"{rootPath}/data/gainDict.csv"
gainDict = LoadDict(gainPath, "gain")
closeJPDict = GetCloseJP()
attrFactor = "close"
closeAttrDict = GetAttr(attrFactor)
closeAttrJPDict = GetAttrJP(attrFactor)
closeAttrLimit = 45.5
closeAttrJPLimit = 1028

attrFactor = "market_cap_basic"
capAttrDict = GetAttr(attrFactor)
capAttrJPDict = GetAttrJP(attrFactor)
capAttrLimit = 623742950
capAttrJPLimit = 5719504393

attrFactor = "number_of_shareholders"
holdersAttrDict = GetAttr(attrFactor)
holdersAttrJPDict = GetAttrJP(attrFactor)
holdersAttrLimit = 132
holdersAttrJPLimit = 3103

attrFactor = "after_tax_margin"
marginAttrDict = GetAttr(attrFactor)
marginAttrJPDict = GetAttrJP(attrFactor)
marginAttrLimit = 34.45287679
marginAttrJPLimit = 3.24540326

attrFactor = "average_volume_90d_calc"
volAttrDict = GetAttr(attrFactor)
volAttrJPDict = GetAttrJP(attrFactor)
volAttrLimit = 278954.73333333
volAttrJPLimit = 18726.66666667

attrFactor = "ADR"
attrDict = GetAttr(attrFactor)
attrJPDict = GetAttrJP(attrFactor)

bias = 0.0482831585

# flaot
# attrLimit = 12785983
# attrJPLimit = 2549207
# float_shares_outstanding 1.0124352334970264

# attrLimit = 623742950
# attrJPLimit = 5719504393
# market_cap_basic 1.0130591132547746

# attrLimit = 45.5
# attrJPLimit = 1028
# close 1.0137363056285043

# attrLimit = 248009000
# attrJPLimit = 142103000
# net_income 1.0067127387886323

# attrLimit = 132
# attrJPLimit = 3103
# number_of_shareholders 1.0152587438048268

# attrLimit = 34.45287679
# attrJPLimit = 3.24540326
# after_tax_margin 1.0109449874096463

# attrLimit = 19.0948
# attrJPLimit = 28.1645
# earnings_per_share_basic_ttm 1.008048358772024

# attrLimit = 23.50977955
# attrJPLimit = 4.66060156
# return_on_invested_capital 1.0064819671208751

# attrLimit = 261466000
# attrJPLimit = 3886695000
# total_current_assets 1.0073820230960946

# attrLimit = 278954.73333333
# attrJPLimit = 18726.66666667
# average_volume_90d_calc 1.0197454787729434

# attrLimit = 2.96637452
# attrJPLimit = 36.53535479
# price_earnings_ttm 1.0054610567298035

attrLimit = 1.68752143
attrJPLimit = 37.28571429

maxNoVolCountLimit = 0
maxAvgGain = 0
maxAvgGainJP = 0
noVolCountLimit = 6
while noVolCountLimit > 1:
    gainList = np.empty(0)
    gainJPList = np.empty(0)
    for symbol, gain in gainDict.items():
        if gain < 1: continue
        # if symbol not in attrDict:continue
        # if symbol not in gainable: continue
        # if attrDict[symbol] < attrLimit: continue
        # if attrDict[symbol] > attrLimit: continue
        currency = "USD"
        if symbol in closeJPDict:
            currency = "JPY"
        if currency == "JPY":
            # if symbol not in closeAttrJPDict: continue
            # closeAttr = closeAttrJPDict[symbol]
            # if closeAttr < closeAttrJPLimit: continue
            # if symbol not in capAttrJPDict: continue
            # capAttr = capAttrJPDict[symbol]
            # if capAttr < capAttrJPLimit: continue
            # if symbol not in holdersAttrJPDict: continue
            # holdersAttr = holdersAttrJPDict[symbol]
            # if holdersAttr < holdersAttrJPLimit: continue
            # if symbol not in marginAttrJPDict: continue
            # marginAttr = marginAttrJPDict[symbol]
            # if marginAttr < marginAttrJPLimit: continue
            if symbol not in volAttrJPDict: continue
            volAttr = volAttrJPDict[symbol]
            if volAttr < volAttrJPLimit: continue
            if symbol not in attrJPDict: continue
            attr = attrJPDict[symbol]
            if attr < attrJPLimit: continue
        else:
            # if symbol not in closeAttrDict: continue
            # closeAttr = closeAttrDict[symbol]
            # if closeAttr < closeAttrLimit: continue
            # if symbol not in capAttrDict: continue
            # capAttr = capAttrDict[symbol]
            # if capAttr < capAttrLimit: continue
            # if symbol not in holdersAttrDict: continue
            # holdersAttr = holdersAttrDict[symbol]
            # if holdersAttr < holdersAttrLimit: continue
            # if symbol not in marginAttrDict: continue
            # marginAttr = marginAttrDict[symbol]
            # if marginAttr < marginAttrLimit: continue
            if symbol not in volAttrDict: continue
            volAttr = volAttrDict[symbol]
            if volAttr < volAttrLimit: continue
            if symbol not in attrDict: continue
            attr = attrDict[symbol]
            if attr < attrLimit: continue
        npArr = []
        if currency == "JPY":
            if symbol not in dataDictJP: continue
            npArr = dataDictJP[symbol]
        else:
            if symbol not in dataDict: continue
            npArr = dataDict[symbol]
        if len(npArr) < 2: continue
        closeArr = npArr[:,3]
        sma25 = SmaArr(closeArr, 25)
        bias25 = (closeArr-sma25)/closeArr
        if (
            bias25[-2] < -bias
        ):
            gain = npArr[-1][3] / npArr[-1][0]
            noVolCount = GetNoVolCount(npArr)
            if noVolCount > noVolCountLimit: continue
            if symbol in closeJPDict:
                gainJPList = np.append(gainJPList,gain)
            else:
                gainList = np.append(gainList,gain)


    lengthGainList = len(gainList)
    lengthGainJPList = len(gainJPList)
    if lengthGainList < 1:
        lengthGainList = 1
    if lengthGainJPList < 1:
        lengthGainJPList = 1
    avgGain = sum(gainList)/lengthGainList
    avgGainJP = sum(gainJPList)/lengthGainJPList 
    avgTotalGain = (avgGain+avgGainJP) /2
    


    if (
        (avgGain > maxAvgGain and
        avgGainJP >= maxAvgGainJP) or
        (avgGain >= maxAvgGain and
        avgGainJP > maxAvgGainJP)
    ):
        maxAvgGain = avgGain
        maxAvgGainJP = avgGainJP
        maxNoVolCountLimit = noVolCountLimit
        print(maxAvgGain,maxAvgGainJP,maxNoVolCountLimit)
        print(attrFactor, avgTotalGain)
    noVolCountLimit -= 1