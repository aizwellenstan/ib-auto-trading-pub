import sys
sys.path.append('.')

from modules.portfolio import GetSharpeSortino
from modules.aiztradingview import GetDividends, GetAll
import pandas as pd
import os
import numpy as np

portfolioPath = "./data/NoDividends.csv"
ignorePath = "./data/Ignore.csv"
noTradePath = "./data/NoTrade.csv"

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
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV',
    'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    'V','CAT','MRNA','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    'VIX',
    'COIN',
]

def CheckSharpeSortino(npArr):
    return npArr[0][2]

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
    # if len(dataDict) > 1:
    #     df = pd.DataFrame()
    #     df['Symbol'] = dataDict.keys()
    #     v = np.array(list(dataDict.values()))
    #     df['Sharpe'] = v[:, 0]
    #     df['Sortino'] = v[:, 1]
    #     df.to_csv(portfolioPath)
    # df = pd.DataFrame(ignoreList, columns = ['Symbol'])
    # df.to_csv(ignorePath)
    # df = pd.DataFrame(noTradeList, columns = ['Symbol'])
    # df.to_csv(noTradePath)
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

divs = GetAll()

sharpeDict = {}
sortinoDict = {}
count = 0
# dataDict = {}
# ignoreList = []
# noTradeList = []
benchmarkList = ['BRK.A']
ddDict = {}
dump = False
for symbol in topOption:
    if dump:
        DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False 
    # if symbol in ignoreList: continue
    # if symbol in noTradeList: continue
    print(symbol)
    # if symbol in dataDict:
    #     sharpeDict[symbol] = dataDict[symbol][0]
    #     sortinoDict[symbol] = dataDict[symbol][1]
    #     print(symbol)
    # else:
    npArr = []
    for benchmark in benchmarkList:
        # if symbol in ignoreList: continue
        # if symbol in noTradeList: continue
        npArr = GetSharpeSortino(benchmark, symbol)
        if len(npArr) > 1:
            ddDict[symbol] = npArr[0][2]
    #     if len(npArr) < 2: 
    #         ignoreList.append(symbol)
    #         dump = True
    #         npArr = []
    #         continue
    #     if not CheckSharpeSortino(npArr):
    #         noTradeList.append(symbol)
    #         dump = True
    #         npArr = []
    #         continue

    # if len(npArr) > 1:
    #     sharpeDict[symbol] = npArr[0][0]
    #     sortinoDict[symbol] = npArr[0][1]
    #     dataDict[symbol] = [npArr[0][0],npArr[0][1]]
    #     print(symbol)
            

# DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)

ddDict = dict(sorted(ddDict.items(), key=lambda item: item[1]))
# sortinoDict = dict(sorted(sortinoDict.items(), key=lambda item: item[1], reverse=True))

print(ddDict)
# print(sortinoDict)