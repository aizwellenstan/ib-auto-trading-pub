rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts
from modules.csvDump import LoadCsv
from modules.aiztradingview import GetAttr, GetAttrJP
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(2)
avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

# @njit
def Backtest(npArr):
    win = 0
    loss = 0
    winList = np.empty(0)
    lossList = np.empty(0)
    for i in range(1, len(npArr)):
        if npArr[i-1][4] >= npArr[i-2][4]: continue
        if npArr[i][3] > npArr[i][0]:
            win += 1
            winList = np.append(winList, npArr[i][3]-npArr[i][0])
        else:
            loss += 1
            lossList = np.append(lossList, npArr[i][0]-npArr[i][3])
    wr = win / (win+loss)
    if wr * np.mean(winList) <= (1-wr) * np.mean(lossList):
        wr = 0
    return wr

def HandleBacktest(dataDict, symbol):
    npArr = dataDict[symbol]
    wr = Backtest(npArr)
    return [symbol, wr]





group = "JP"
# group = "US"
if group == "US":
    dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
    dataDictUS = LoadPickle(dataPathUS)

    length = len(dataDictUS["AAPL"])
    dataDict = dataDictUS
else:
    ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"

    ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
    dataDictJP = LoadPickle(dataPathJP)

    length = len(dataDictJP["9101"])
    dataDict = dataDictJP

cleanDataDict = {}
for symbol, npArr in dataDict.items():
    if len(npArr) < length: continue
    if group == "JP":
        if symbol not in ryuudoumeyasuDict: continue
        if ryuudoumeyasuDict[symbol][0] <= 100: continue
    cleanDataDict[symbol] = npArr

resDict = {}
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleBacktest, cleanDataDict, symbol) for symbol in list(cleanDataDict.keys())]
    for future in as_completed(futures):
        result = future.result()
        if len(result) < 1: continue
        symbol = result[0]
        res = result[1]
        if res <= 0.5: continue
        if cleanDataDict[symbol][-1][0] > avalible_price: continue
        resDict[symbol] = res
resDict = dict(sorted(resDict.items(), key=lambda item:item[1], reverse=True))
print(resDict)

passedList = []
shift = 0
for symbol in resDict.keys():
    npArr = cleanDataDict[symbol]
    if npArr[-1-shift][4] >= npArr[-2-shift][4]: continue
    passedList.append(symbol)
print(passedList)