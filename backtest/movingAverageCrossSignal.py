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
csvPath = f"{rootPath}/data/movingAverage.csv"
dataDict = load_csv_to_dict(csvPath)
print(dataDict)
closeDictJP = GetCloseJP()

passedList = []
for symbol, v in dataDict.items():
    if symbol in closeDictJP:
        if symbol not in rironkabukaDict: continue
        close = closeDictJP[symbol]
        rironkabuka = rironkabukaDict[symbol]
        if close >= rironkabuka: continue
        npArr = dataDictJP[symbol]
        crossUp = CheckSmaCrossUp(npArr, v[1])
        if crossUp: 
            passedList.append(symbol)
            print(symbol,"CrossUp")
    else:
        if symbol not in dataDictUS: continue
        npArr = dataDictUS[symbol]
        crossUp = CheckSmaCrossUp(npArr, v[1])
        if crossUp: 
            passedList.append(symbol)
            print(symbol,"CrossUp")
print(passedList)