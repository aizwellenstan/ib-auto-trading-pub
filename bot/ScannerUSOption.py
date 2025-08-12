rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr
from modules.data import GetDataLts
from modules.csvDump import LoadCsv, dump_result_list_to_csv
import numpy as np
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate
from datetime import datetime
from modules.aiztradingview import GetAttr, GetETF, GetDayTrade
from modules.dict import take
from modules.csvDump import LoadDict
from modules.rsi import GetRsi

dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataDictUS = LoadPickle(dataPathUS)

# forwardPathUS = f"{rootPath}/backtest/pickle/pro/compressed/forwardUS.p"
# forwardDict = LoadPickle(forwardPathUS)
forwardDict = {}

optionPath = f"{rootPath}/data/tradableOption.csv"
optionDict = LoadDict(optionPath, "Length")

def Backtest(dataDict, length, 
    sampleArrJP):
    i = length
    today = sampleArrJP[i-1][5]
    signalDict = {}
    
    for symbol, npArr in dataDict.items():
        if npArr[i-1][3] > npArr[i-1][0]: continue
        if npArr[i-1][3] > npArr[i-2][2]: continue
        if npArr[i-1][3] > npArr[i-3][2]: continue
        if npArr[i-1][3] > npArr[i-2][1]: continue
        if npArr[i-1][4] < npArr[i-2][4]: continue
        if npArr[i-1][3] * npArr[i-1][4] > 13306310834.985352: continue
        if npArr[i-1][3] * npArr[i-1][4] < 1887654.9532413483: continue
        if (
            npArr[i-2][4] < npArr[i-4][4] and
            npArr[i-1][4] > npArr[i-2][4]
        ): continue

        diff = abs(npArr[i-1][3] - npArr[i-1][0])
        if diff > 0:
            if (
                npArr[i-1][1] > npArr[i-2][1] and
                npArr[i-1][3] < npArr[i-2][3] and
                (
                    (npArr[i-1][1]-npArr[i-1][3]) / 
                    diff
                ) > 7.9
            ): continue

        volSma5 = SmaArr(npArr[:,4], 5)
        volSma30 = SmaArr(npArr[:,4], 30)
        if volSma5[i-1] < volSma30[i-1]: continue

        rsi = GetRsi(npArr[:,3])
        if (
            rsi[i-1] < 50 or
            rsi[i-1] > 80
        ): continue

        signalDict[symbol] = npArr[i-1][3] / npArr[i-2][0]

    signalDict = dict(sorted(signalDict.items(), key=lambda item: item[1], reverse=True))
    return list(signalDict.keys())

# exchangeDict = GetAttr("exchange")

sampleArr = dataDictUS["AAPL"]
length = len(sampleArr)
dataDict = dataDictUS
etf3x = [
    "SOXS", "SOXL", "TMF", "LABU", "SPXS", 
    "TNA", "TZA", "FNGD", "SPXL", "TECS", 
    "LABD", "TECL", "FNGU", "TMV", "FAZ",
    "DPST", "GDXD", "WEBL", "BNKU", "FAS", "GDXU",
    "DRN", "BERZ", "RETL", "WEBS", 
    "DFEN", "NAIL",
    "DRV", "KORU", "BNKD", "HIBS", "BULZ", "UTSL",
    "EDZ", "HIBL", "OILU", "OILD", "EDC", "NRGU",
    "CURE", "TYD", "NRGD", "TYO", "PILL", "WANT",
    "MIDU", "FLYD", "TPOR", "DUSL", "EURL", "MEXX",
    "FLYU", "SHNY", "WTIU", "DULL", "WTID", "JETU",
    "CARD", "JETD", "CARU"
]
floatDict = GetAttr("float_shares_outstanding")
etfList = GetETF()
import pandas as pd
df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
cfd = df['Symbol'].values.tolist()

cleanDataDict = {}
for symbol, npArr in dataDict.items():
    if symbol not in floatDict: continue
    if len(npArr) < length: continue
    if floatDict[symbol] > 460825344: continue
    if symbol not in cfd: continue
    if symbol in etfList: continue
    npArr = dataDict[symbol]
    cleanDataDict[symbol] = npArr
dataDict = cleanDataDict

symbolList = Backtest(cleanDataDict, length, 
    sampleArr)
print(symbolList)

res = []
for symbol in symbolList[:37]:
    res.append([symbol,cleanDataDict[symbol][-1][3]])

csvPath = f"{rootPath}/data/ScannerUSOption.csv"
header = ["Symbol","Close"]
dump_result_list_to_csv(res,csvPath,header)