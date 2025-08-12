rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

# # @njit
def CheckSmaCrossUp(npArr):
    shift = 0
    closeArr = npArr[:,3]
    smaArr25 = SmaArr(closeArr,25)
    smaArr5 = SmaArr(closeArr,5)
    if (
        npArr[-2-shift][3] < smaArr25[-2-shift] and
        npArr[-1-shift][3] < smaArr25[-1-shift] and
        npArr[-2-shift][3] > smaArr5[-2-shift] and
        npArr[-1-shift][3] > smaArr5[-1-shift] and
        npArr[-2-shift][3] > npArr[-2-shift][0] and
        npArr[-1-shift][3] > npArr[-1-shift][0] and
        (npArr[-1-shift][3] - npArr[-1-shift][2]) > (npArr[-2-shift][1] - npArr[-2-shift][2])/2
    ): return True
    return False

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
    
rironkabukaDict = LoadPickle(rironkabukaPath)
dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)
csvPath = f"{rootPath}/data/25ma.csv"
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
        crossUp = CheckSmaCrossUp(npArr)
        if crossUp: 
            passedList.append(symbol)
            print(symbol,"CrossUp")
    else:
        if symbol not in dataDictUS: continue
        npArr = dataDictUS[symbol]
        crossUp = CheckSmaCrossUp(npArr)
        if crossUp: 
            passedList.append(symbol)
            print(symbol,"CrossUp")
print(passedList)