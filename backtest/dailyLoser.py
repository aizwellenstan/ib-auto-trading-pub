rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr


from modules.aiztradingview import GetAttr, GetAttrJP

floatShareDict = GetAttr("float_shares_outstanding")

# # @njit
def CheckVolumeDecrease(npArr):
    if (
        len(npArr) > 2 and
        npArr[-1][4] < npArr[-2][4]
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
        crossUp = CheckVolumeDecrease(npArr)
        if crossUp: 
            passedList.append(symbol)
    else:
        if symbol not in floatShareDict: continue
        if symbol not in dataDictUS: continue
        npArr = dataDictUS[symbol]
        crossUp = CheckVolumeDecrease(npArr)
        if crossUp: 
            passedList.append(symbol)
print(passedList)

# checkList = ["ALLR","VBIV"]
# for symbol in checkList:
#     if symbol in passedList:
#         print(symbol, "BUY")

# sys.exit()
from ib_insync import *

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=0)

hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.NYSE,STK.NASDAQ',
                                        scanCode='TOP_PERC_LOSE',
                                        # belowPrice=19.72,
                                        abovePrice=1.05
                                        # marketCapBelow=1276710213.848115
                                        # aboveVolume=''  # <1407
                                        )

scanner = ib.reqScannerData(hot_stk_by_gain, [])

scanList = []
for stock in scanner:
    symbol = stock.contractDetails.contract.symbol
    if symbol not in passedList: continue
    scanList.append(symbol)
print(scanList)