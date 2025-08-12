rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr


# # @njit
def CheckSmaCrossUp(npArr, period):
    closeArr = npArr[:,3]
    smaArr = SmaArr(closeArr, period)
    if (
        closeArr[-2] < smaArr[-2] and
        closeArr[-1] > smaArr[-1]
    ): return True
    return False

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    
rironkabukaDict = LoadPickle(rironkabukaPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)

# dataDict = dataDictUS
# dataDict.update(dataDictJP)
from modules.aiztradingview import GetAttr, GetAttrJP

floatShareDict = GetAttr("float_shares_outstanding")
assetDict = GetAttr("total_assets")
length = len(dataDictUS["AAPL"])
# length = len(dataDictJP["9101"])

dataDict = {}
for symbol, npArr in dataDictUS.items():
    if symbol not in floatShareDict: continue
    if len(npArr) < length: continue
    dataDict[symbol] = dataDictUS[symbol]

topPbr = 1
topSymbol = ""
for symbol, npArr in dataDict.items():
    if symbol not in floatShareDict: continue
    if symbol not in assetDict: continue
    pbr = npArr[-1][3]*floatShareDict[symbol]/assetDict[symbol]
    if pbr < topPbr:
        topPbr = pbr
        topSymbol = symbol
print(topSymbol, topPbr)