rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.movingAverage import SmaArr
from modules.data import GetNpData
import numpy as np
from numba import range, njit
import pickle
from modules.csvDump import DumpCsv, LoadCsv

options = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'ARKK','GDX','GLD','SLV',
    'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    'V','MRNA','CLAR','SE','ZM','DOCU','SPLK',
    'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    'VIX',
    'COIN'
]

dataPath = "./pickle/pro/compressed/dataDictOption2.p"
dataArr = {}
update = False
if update:
    for symbol, close in closeDict.items():
        npArr = GetNpData(symbol)
        if len(npArr) < 1: continue
        dataArr[symbol] = npArr
        print(symbol)
    pickle.dump(dataArr, open(dataPath, "wb"))
    print("pickle dump finished")
else:
    output = open(dataPath, "rb")
    dataArr = pickle.load(output)
    output.close()
    signalArr = ["QQQ","SPY","DIA","IWM","BRK.B","HYG"]
    for symbol in options:
        if symbol not in dataArr:
            print(symbol)

# @njit
def Backtest(signalArr, npArr):
    npArr = npArr[-1058:]
    val = 0.01
    maxBalance = 1
    correlation_threshold = 1
    maxRetraceVal = 0
    maxVal = 0
    retraceVal = 1
    while correlation_threshold > 0.1 and retraceVal > 0.01:
        balance = 1
        for i in range(1, len(npArr)):
            if npArr[i][0] < npArr[i-1][3]:
                correlation = np.corrcoef(signalArr[:,3][:i], npArr[:,3][:i])[0, 1]
                # if npArr[i][0] < npArr[i-1][3]:
                if correlation < correlation_threshold:
                    op = npArr[i][0]
                    if op < 0.01: 
                        maxBalance = 0
                        break
                    tp = (npArr[i-1][3] - npArr[i][0]) * retraceVal + npArr[i][0]
                    if tp - op < 0.01: continue
                    if tp > npArr[i][1]:
                        tp = npArr[i][3]
                    gain = tp / op
                    balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxVal = correlation_threshold
            maxRetraceVal = retraceVal
        retraceVal -= 0.01
        if retraceVal <= 0.01:
            correlation_threshold -= 0.01
            retraceVal = 1
    if maxBalance <= 1:
        maxBalance = 0
    res = np.array([maxBalance/len(npArr), maxVal, maxRetraceVal])
    return res

signalSymbol = "QQQ"
signalArr = dataArr[signalSymbol]
signalArr = signalArr[-1058:]

gainPerDayDict = {}
valDict = {}
retraceValDict = {}
for signalSymbol, close in dataArr.items():
    signalArr = dataArr[signalSymbol]
    signalArr = signalArr[-1058:]
    if len(signalArr) < 1058: continue
    for symbol, close in dataArr.items():
        if symbol == signalSymbol: continue
        # if symbol not in options: continue
        npArr = dataArr[symbol]
        res = Backtest(signalArr, npArr)
        gainPerDay = res[0]
        if gainPerDay <= 0: continue
        val = res[1]
        if val == 0: continue
        retraceVal = res[2]
        if retraceVal == 0: continue
        gainPerDayDict[signalSymbol+"_"+symbol] = gainPerDay
        print(signalSymbol+"_"+symbol, gainPerDay)
        valDict[signalSymbol+"_"+symbol] = val
        retraceValDict[signalSymbol+"_"+symbol] = retraceVal
gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
print(gainPerDayDict)

newGainPerDayDict = {}
count = 0
for symbol, gainPerDay in gainPerDayDict.items():
    if gainPerDay == 0: continue
    newGainPerDayDict[symbol] = gainPerDay
    count += 1
    if count > 100: break
print(newGainPerDayDict)

newValDict = {}
for symbol, v in newGainPerDayDict.items():
    newValDict[symbol] = float('{0:.2f}'.format(valDict[symbol]))
print(newValDict)

newRetraceValDict = {}
for symbol, v in newGainPerDayDict.items():
    newRetraceValDict[symbol] = float('{0:.2f}'.format(retraceValDict[symbol]))
print(newRetraceValDict)