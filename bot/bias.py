rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetBias, GetBiasJP, GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import LoadDict, DumpDict
from modules.normalizeFloat import NormalizeFloat
import modules.ib as ibc
from modules.trade.vol import GetVolTp

ibc = ibc.Ib()
ib = ibc.GetIB(26)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

closeJPDict = GetBiasJP()
closeDict = GetBias()
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
bias = 0.0482831585
noVolCountLimit = 2

shift = 0
tradeDictJP = {}
tradeDictUS = {}
for symbol, gain in gainDict.items():
    if (
        symbol not in closeDict and
        symbol not in closeJPDict
    ): continue
    # if gain < 1: continue
    if gain < 29.6796: continue
    currency = "USD"
    if symbol in closeJPDict:
        currency = "JPY"
    npArr = []
    if currency == "JPY":
        npArr = GetNpData(symbol, "JPY")
    else:
        npArr = GetNpData(symbol)
    if len(npArr) < shift+1: continue
    closeArr = npArr[:,3]
    sma25 = SmaArr(closeArr, 25)
    bias25 = (closeArr-sma25)/closeArr
    if bias25[-1-shift] < -bias:
        smaTp = sma25[-1]
        op = closeArr[-1]
        sl  = op - (smaTp - op)
        if symbol in closeJPDict:
            print(symbol)
            sl = NormalizeFloat(sl, 1)
            vol, tp = GetVolTp(
                total_cash,avalible_cash,op,sl,'JPY'
            )
            smaTp = NormalizeFloat(smaTp, 1)
            print(symbol,"VOL",vol,"TP",tp)
            if tp > smaTp:
                tp = smaTp
            if (tp - op) * vol < 2: continue
            tradeDictJP[symbol] = tp
        else:
            sl = NormalizeFloat(sl, 0.01)
            vol, tp = GetVolTp(
                total_cash,avalible_cash,op,sl,'USD'
            )
            print(symbol,"VOL",vol,"TP",tp)
            smaTp = NormalizeFloat(smaTp, 0.01)
            if tp > smaTp:
                tp = smaTp
            if (tp - op) * vol < 2: continue
            tradeDictUS[symbol] = tp

tradeJPPath = f"{rootPath}/data/BiasJP.csv"
tradeUSPath = f"{rootPath}/data/BiasUS.csv"
DumpDict(tradeDictJP,"tp",tradeJPPath)
DumpDict(tradeDictUS,"tp",tradeUSPath)