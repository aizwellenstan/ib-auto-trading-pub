rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr, GetHistoricalGain
import yfinance as yf
import pandas as pd
from modules.dict import take
from modules.data import GetNpData
import pickle

def getNpData(symbol):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
    
        df = stockInfo.history(period="12d")
        df = df[['Open','High','Low','Close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def DumpResCsv(resPath, resList):
    df = pd.DataFrame(resList, columns = ['Symbol'])
    df.to_csv(resPath)

closeDict = GetClose()

picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDictAll.p"

update = True
marketCapDict = GetAttr("market_cap_basic")
shareHoldersDict = GetAttr("number_of_shareholders")
gainList = GetHistoricalGain()

dataDict = {}
if not update:
    import pickle, gc
    output = open(picklePath, "rb")
    gc.disable()
    dataDict = pickle.load(output)
    output.close()
    gc.enable()
else:
    for symbol, v in closeDict.items():
        npArr = GetNpData(symbol)
        if len(npArr) < 2: continue
        dataDict[symbol] = npArr
    pickle.dump(dataDict, open(picklePath, "wb"))
    print("pickle dump finished")

period = 1
momentumDict = {}

ignoreList = ['CORZ','EMCF']

shift = 0
for symbol, npArr in dataDict.items():
    if symbol in ignoreList: continue
    if symbol not in gainList: continue
    if symbol not in marketCapDict: continue
    if len(npArr) < 4: continue
    # marketCap = marketCapDict[symbol]
    # if marketCap < 9124279: continue
    # if symbol not in shareHoldersDict: continue
    # shareHolders = shareHoldersDict[symbol]
    # if shareHolders < 189: continue
    if npArr[-1][3] / npArr[-5][3] < 0.49: continue
    if npArr[-1][3] / npArr[-5][3] < 0.58: continue
    if npArr[-1][3] / npArr[-4][3] < 0.55: continue
    if npArr[-1][3] / npArr[-3][3] < 0.56: continue
    if npArr[-1][3] / npArr[-2][3] < 0.69: continue
    if npArr[-1][3] / npArr[-3][3] > 1.02: continue
    if npArr[-1][3] / npArr[-2][3] > 1.71: continue
    momentum = npArr[-1-shift][3]/npArr[-1-period-shift][3]
    momentumDict[symbol] = momentum

momentumDict = dict(sorted(momentumDict.items(), key=lambda item: item[1]))

print(take(10,momentumDict.items()))
reverseList = momentumDict.keys()
resPath = f'{rootPath}/data/Reverse.csv'
DumpResCsv(resPath, reverseList)