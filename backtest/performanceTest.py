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
netIncomeDict = GetAttr("net_income")
length = len(dataDictUS["AAPL"])
# length = len(dataDictJP["9101"])

dataDict = {}
for symbol, npArr in dataDictUS.items():
    if symbol not in floatShareDict: continue
    # if symbol not in netIncomeDict: continue
    if len(npArr) < length: continue
    dataDict[symbol] = dataDictUS[symbol]


# attrList = list(reversed(list(floatShareDict.values())))

# 5375322
maxBalance = 1
maxPeriod = 1
period = 3
while period < length - 2:
    balance = 1
    for i in range(period, length):
        topVolChange = 1
        topSymbol = ""
        for symbol, npArr in dataDict.items():
            if symbol not in floatShareDict: continue
            volChange = npArr[i-1][3] / npArr[i-period][3]
            
            if volChange > topVolChange:
                topVolChange = volChange
                topSymbol = symbol

        npArr = dataDict[topSymbol]
        gain = npArr[i][3] / npArr[i][0]
        balance *= gain
        # print(balance)
    if balance > maxBalance:
        maxBalance = balance
        maxPeriod = period
        print(maxBalance, maxPeriod)
    period += 1
# passedList = []
# for symbol, v in dataDict.items():
#     if symbol in closeDictJP:
#         if symbol not in rironkabukaDict: continue
#         close = closeDictJP[symbol]
#         rironkabuka = rironkabukaDict[symbol]
#         if close >= rironkabuka: continue
#         npArr = dataDictJP[symbol]
#         crossUp = CheckSmaCrossUp(npArr, v[1])
#         if crossUp: 
#             passedList.append(symbol)
#             print(symbol,"CrossUp")
#     else:
#         if symbol not in dataDictUS: continue
#         npArr = dataDictUS[symbol]
#         crossUp = CheckSmaCrossUp(npArr, v[1])
#         if crossUp: 
#             passedList.append(symbol)
#             print(symbol,"CrossUp")
# print(passedList)