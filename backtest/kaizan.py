rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import load_csv_to_dict
from modules.data import GetDataLts
from modules.minkabu import GetPrice
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf
from datetime import datetime
from modules.csvDump import DumpCsv, LoadCsv
import asyncio
import modules.ib as ibc
from modules.aiztradingview import GetAttrJP
import numpy as np
from modules.movingAverage import SmaArr

# today = datetime.now().date()

ibc = ibc.Ib()
ib = ibc.GetIB(2)

avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

# contractDict = {}
# contractSmartDict = {}

# class Trader:
#     def __init__(self, ticker):
#         self.ticker = ticker

#     async def _init(self):
#         print('{} started'.format(self.ticker))
#         close = await self.op()
#         print('{} ended'.format(self.ticker))

#     async def op(self):
#         df = await ib.reqHistoricalDataAsync(
#             contractDict[self.ticker],
#             endDateTime='',
#             durationStr='1 D',
#             barSizeSetting='1 day',
#             whatToShow='TRADES',
#             useRTH=True,
#             formatDate=1)
#         op = 0
#         if len(df) > 0:
#             op = df[-1].open
#             if df[-1].date == today:
#                 priceDict[self.ticker] = op

# async def fetch_tickers(symbolList):
#     return await asyncio.gather(*(asyncio.ensure_future(safe_trader(ticker)) for ticker in symbolList))

# async def safe_trader(ticker):
#     async with sem:
#         t = Trader(ticker)
#         return await t._init()


rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
nisshokinPath = f"{rootPath}/backtest/pickle/pro/compressed/nisshokin.p"
ordinarySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/ordinarySharesJP.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
financialScorePath = f"{rootPath}/backtest/pickle/pro/compressed/financialScore.p"
financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
netIncomePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeJP.p"
treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
# dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"


rironkabukaDict = LoadPickle(rironkabukaPath)
nisshokinDict = LoadPickle(nisshokinPath)
ordinarySharesDict = LoadPickle(ordinarySharesPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
shijouDict = LoadPickle(shijouPath)
gyoushuDict = LoadPickle(gyoushuPath)
financialScoreDict = LoadPickle(financialScorePath)
financialDetailDict = LoadPickle(financialDetailPath)
shuuekiDict = LoadPickle(shuuekiPath)
haitourimawariDict = LoadPickle(haitourimawariPath)
treasurySharesDict = LoadPickle(treasurySharesPath)
zandakaDict = LoadPickle(zandakaPath)
inventoryDict = LoadPickle(inventoryPath)
netIncomeDict = LoadPickle(netIncomePath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
# dataDictUS = LoadPickle(dataPathUS)
dataDictJP = LoadPickle(dataPathJP)

closeDict = GetCloseJP()
industryDict = GetAttrJP("industry")
assetDict = GetAttrJP("total_current_assets")
liabilitiesDict = GetAttrJP("total_liabilities_fy")

ignoreList = [
    "Electronic Production Equipment", 
    "Telecommunications Equipment", 
    "Environmental Services",
    "Computer Peripherals",
    "Biotechnology",
    "Commercial Printing/Forms",
    "Trucks/Construction/Farm Machinery",
    "Auto Parts: OEM",
    "Tools & Hardware",
    "Recreational Products",
    "Metal Fabrication",
    "Forest Products",
    "Industrial Specialties",
    "Other Consumer Specialties",
    "Movies/Entertainment",
    "Medical Specialties",
    "Office Equipment/Supplies",
    "Electronics/Appliances",
    "Pulp & Paper",
    "Electrical Products",
    "Alternative Power Generation"
]
ignoreSector = ["輸送用機器","情報通信",
        "鉱業","繊維",
        "空運","保険","鉄鋼",
        "銀行"]
ignoreSectorFirst = [
    "紙・パルプ",
    "鉱業","繊維",
    "空運","鉄鋼",
    "保険"]

kaizanHiritsuDict = {}
shift = 2
for symbol, close in closeDict.items():
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSectorFirst: continue
    if symbol not in dataDictJP: continue
    if symbol not in treasurySharesDict: continue
    treasuryShares = treasurySharesDict[symbol]
    if len(treasuryShares) < 2: continue
    if symbol not in shisannkachiDict: continue
    if symbol not in shuuekiDict: continue
    if symbol not in shijouDict: continue
    if symbol not in haitourimawariDict: continue
    if haitourimawariDict[symbol] > 0.033: continue
    if symbol not in assetDict: continue
    if symbol not in liabilitiesDict: continue
    if assetDict[symbol] < liabilitiesDict[symbol]/30: continue
    npArr = dataDictJP[symbol]
    
    if npArr[-1-shift][3] / shisannkachiDict[symbol] > 7.8: continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if zandaka[0-shift][1] < 900: continue
    if npArr[-1-shift][4] >= npArr[-2-shift][4]: continue
    # treasuryShares = treasurySharesDict[symbol]
    # if treasuryShares[0] < treasuryShares[1]: continue
    # if shijouDict[symbol] == "東証プライム": continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSector: continue
    if npArr[-1-shift][3] >= rironkabukaDict[symbol] - 5: continue
    if symbol not in financialDetailDict: continue
    # if shuuekiDict[symbol] < 0.02: continue
    if financialDetailDict[symbol][0] != 0:
        if financialDetailDict[symbol][0] < 3:
            continue
    if (
        symbol in netIncomeDict and
        symbol in inventoryDict
    ):
        netIncome = netIncomeDict[symbol]
        inventory = inventoryDict[symbol]
        if (
            len(inventory) > 2 and
            len(netIncome) > 2 and
            inventory[0] > inventory[1] and
            inventory[1] > inventory[2] and
            netIncome[0] < netIncome[1] and
            netIncome[1] < netIncome[2]
        ): continue

    if symbol not in rironkabukaDict: continue
    if symbol not in nisshokinDict: continue
    if symbol not in ordinarySharesDict: continue
    if closeDict[symbol] >= rironkabukaDict[symbol] - 5: continue
    
    # closeArr = npArr[:,3]
    # sma5 = SmaArr(closeArr, 5)
    # if npArr[-1-shift][3] < sma5[-1-shift]: continue
    if npArr[-2-shift][3] < npArr[-3-shift][3]: continue
    if npArr[-1-shift][3] < npArr[-2-shift][3]: continue

    if closeDict[symbol] > avalible_price: continue
    
    if symbol not in ryuudoumeyasuDict: continue
    if ryuudoumeyasuDict[symbol][0] <= 100: continue

    if len(nisshokinDict) < 2: continue
    kaizan = nisshokinDict[symbol][0+shift][1]
    urizan = nisshokinDict[symbol][0+shift][2]
    if urizan != 0: continue
    if kaizan < 1: continue
    kaizanHiritsu = kaizan / ordinarySharesDict[symbol][0]
    kaizanHiritsuDict[symbol] = kaizanHiritsu
kaizanHiritsuDict = dict(sorted(kaizanHiritsuDict.items(), key=lambda item:item[1], reverse=True))
# print(kaizanHiritsuDict)
# ibc.HandleBuyLimitTpTrailWithContract(contractDict[topSymbol], contractSmartDict[topSymbol], 100, int(target))
# print(topSymbol, target, rironkabukaDict[topSymbol])
# for k, v in kaizanHiritsuDict.items():
#     print(k, v)

tradableJPPath = f"{rootPath}/data/Kaizan.csv"
DumpCsv(tradableJPPath,list(kaizanHiritsuDict.keys()))