rootPath = '..'
import sys
sys.path.append(rootPath)
import os
import pandas as pd
from datetime import date, datetime
import modules.ib as ibc
from modules.aiztradingview import GetCommonStock
from modules.csvDump import DumpCsv, DumpDict, LoadDict
import pickle
from modules.data import GetNpData

import numpy as np

ibc = ibc.Ib()
ib = ibc.GetIB(13)

today = date.today()

topOption = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV',
    # 'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    # 'V','CAT','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    # 'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    # 'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    # 'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    # 'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    # 'VIX',
    # 'COIN',
]

def GetData(symbol, close):
    chains = ibc.GetChains(symbol)
    for optionschain in chains:
        strikeList = optionschain.strikes
        strikeList.sort(reverse=True)
        for strike in strikeList:
            if strike < close - 0.5:
                if len(optionschain.expirations) < 2: 
                    return []
                for expiration in optionschain.expirations:
                    expir = datetime.strptime(expiration, '%Y%m%d').date()
                    dur = (expir-today).days
                    if dur < 1: continue
                    optionContract = ibc.GetOptionPutContract(symbol, expiration, strike)
                    data = ibc.GetData(optionContract)
                    return data
    return []

# @njit
def GetGainPerDay(npArr):
    npArr = npArr[-1082:]
    val = 0.01
    maxBalance = 1
    maxVal = 0
    while val < 1:
        balance = 1
        for i in range(1, len(npArr)):
            if npArr[i][0] < npArr[i-1][3]:
                op = npArr[i][0]
                if op < 0.01: 
                    maxBalance = 0
                    break
                tp = (npArr[i-1][3] - npArr[i][0]) * val + npArr[i][0]
                if tp - op < 0.01: continue
                if tp > npArr[i][1]:
                    tp = npArr[i][3]
                gain = tp / op
                balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
            print(maxBalance,maxVal)
        val += 0.01
    print('MaxBalance',maxBalance)
    res = np.empty(0)
    res = np.append(res, maxBalance/len(npArr))
    res = np.append(res, maxVal)
    return res

def Backtest(dataDict):
    gainPerDayDict = {}
    valDict = {}
    for symbol, npArr in dataDict.items():
        res = GetGainPerDay(npArr)
        gainPerDay = res[0]
        if gainPerDay == 0: continue
        val = res[1]
        if val == 0: continue
        gainPerDayDict[symbol] = gainPerDay
        valDict[symbol] = val
    gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
    print(gainPerDayDict)

    newValDict = {}
    for symbol, v in gainPerDayDict.items():
        newValDict[symbol] = float('{0:.2f}'.format(valDict[symbol]))
    print(newValDict)

def main(update=False):
    optionPath = f"{rootPath}/data/TradableOption.csv"
    if update:
        

        optionPath = f'{rootPath}/data/Options.csv'
        if os.path.exists(optionPath):
            df = pd.read_csv(optionPath)
            optionList = list(df.Symbol.values)
        print(optionList)
        closeDict = GetCommonStock()
        optionDict = {}
        for symbol in optionList:
            if symbol not in closeDict: continue
            # close = closeDict[symbol]
            op = GetNpData(symbol)[-1][0]
            # close = 89.82
            data = GetData(symbol, op)
            df = pd.DataFrame(data)
            df = df.drop_duplicates(subset=["open","close"],keep=False)
            print(symbol, len(df))
            optionDict[symbol] = len(data)
        optionDict = dict(sorted(optionDict.items(), key=lambda item: item[1], reverse=True))
        print(optionDict)
        options = list(optionDict.keys())

        tradable = []
        for k, v in optionDict.items():
            if v < 390: continue
            tradable.append(k)
        print(tradable)
        DumpDict(optionDict,'Length',optionPath)
    else:
        picklePath = "./pickle/pro/compressed/dataDictOption.p"
        optionDict = LoadDict(optionPath,"Length")
        dataDict = {}
        update = False
        if update:
            for symbol, length in optionDict.items():
                if length < 390: continue
                npArr = GetNpData(symbol)
                dataDict[symbol] = npArr
            pickle.dump(dataDict, open(picklePath, "wb"))
        else:
            output = open(picklePath, "rb")
            dataDict = pickle.load(output)
            output.close()
            Backtest(dataDict)

if __name__ == '__main__':
    main()