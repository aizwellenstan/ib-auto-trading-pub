import sys
sys.path.append('.')

from modules.portfolio import GetSharpeSortino
from modules.aiztradingview import GetDividends, GetAll
import pandas as pd
import os
import numpy as np
from modules.data import GetNpData

portfolioPath = "./data/NoDividends.csv"
ignorePath = "./data/Ignore.csv"
noTradePath = "./data/NoTrade.csv"

def CheckSharpeSortino(npArr):
    if npArr[0][3] < 0.01: return False
    if npArr[0][2] < -15.51: return False
    # if npArr[0][2] < -61.93: return False
    if npArr[0][0] < 0.01 or npArr[0][1] < 0.01: return False
    if npArr[0][0] >= npArr[1][0]:
        # if npArr[0][3] >= npArr[1][3]:
        return True
    return False

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
    if len(dataDict) > 1:
        df = pd.DataFrame()
        df['Symbol'] = dataDict.keys()
        v = np.array(list(dataDict.values()))
        df['Sharpe'] = v[:, 0]
        df['Sortino'] = v[:, 1]
        df.to_csv(portfolioPath)
    df = pd.DataFrame(ignoreList, columns = ['Symbol'])
    df.to_csv(ignorePath)
    df = pd.DataFrame(noTradeList, columns = ['Symbol'])
    df.to_csv(noTradePath)
    print("dump")

dataDict = {}
ignoreList = []
noTradeList = []
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    df = df[['Symbol', 'Sharpe', 'Sortino']]
    dataDict = df.set_index('Symbol').T.to_dict('list')

if os.path.exists(ignorePath):
    df = pd.read_csv(ignorePath)
    ignoreList = list(df.Symbol.values)

if os.path.exists(noTradePath):
    df = pd.read_csv(noTradePath)
    noTradeList = list(df.Symbol.values)

for symbol in dataDict:
    npArr = GetNpData(symbol)
    if len(npArr) > 553:
        print(symbol)