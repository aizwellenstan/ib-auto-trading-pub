rootPath = "."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetCloseJP
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr
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

today = datetime.now().date()

ibc = ibc.Ib()
ib = ibc.GetIB(1)

avalible_cash = ibc.GetAvailableCash() - 1737
avalible_price = int(avalible_cash)/100
print(avalible_price)

contractDict = {}
contractSmartDict = {}

class Trader:
    def __init__(self, ticker):
        self.ticker = ticker

    async def _init(self):
        print('{} started'.format(self.ticker))
        close = await self.op()
        print('{} ended'.format(self.ticker))

    async def op(self):
        df = await ib.reqHistoricalDataAsync(
            contractDict[self.ticker],
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        op = 0
        if len(df) > 0:
            op = df[-1].open
            if df[-1].date == today:
                priceDict[self.ticker] = op

async def fetch_tickers(symbolList):
    return await asyncio.gather(*(asyncio.ensure_future(safe_trader(ticker)) for ticker in symbolList))

async def safe_trader(ticker):
    async with sem:
        t = Trader(ticker)
        return await t._init()


# ignoreSymbolPath = f"{rootPath}/data/IgnoreJPLts.csv"
# ignoreSymbolList = LoadCsv(ignoreSymbolPath)


def GetSimilarCompanyDict(industryDict, dataDict):
    grouped_dict = {}
    for key, value in industryDict.items():
        if key not in dataDict: continue
        if value not in grouped_dict:
            grouped_dict[value] = [key]
        else:
            grouped_dict[value].append(key)
    new_dict = {}
    for industry, symbols in grouped_dict.items():
        for symbol in symbols:
            filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
            if len(filtered_symbols) >= 4:
                new_dict.setdefault(symbol, []).extend(filtered_symbols)
    return new_dict

# similarCompanyDict = load_csv_to_dict(f"{rootPath}/data/SimilarCompanyJP.csv")

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
plPath = f"{rootPath}/backtest/pickle/pro/compressed/pl.p"
shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
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
plDict = LoadPickle(plPath)
shisannkachiDict = LoadPickle(shisannkachiPath)
shijouDict = LoadPickle(shijouPath)
gyoushuDict = LoadPickle(gyoushuPath)
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

# dataDict = dataDictUS
# dataDict.update(dataDictJP)


industryDict = GetAttrJP("industry")
netIncomeDict = GetAttrJP("net_income")
epsDict = GetAttrJP("basic_eps_net_income")
last_annual_revenueDict = GetAttrJP("last_annual_revenue")
price_revenue_ttmDict = GetAttrJP("price_revenue_ttm")
assetDict = GetAttrJP("total_current_assets")
liabilitiesDict = GetAttrJP("total_liabilities_fy")
length = len(dataDictJP["9101"])

count = 3945
import itertools
industryDict = dict(itertools.islice(industryDict.items(), count))

dataDict = dataDictJP
similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)


dataDict = {}
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

ignoreList = []
for symbol, industry in industryDict.items():
    if symbol not in plDict: continue
    pl = plDict[symbol]
    if len(pl) < 9: continue
    uriage = pl[0]
    if len(uriage) < 1: continue
    keijyourieki = pl[2]
    if len(keijyourieki) < 1: continue
    if keijyourieki[1] < -511260000: continue
    junnshisan = pl[5]
    junnshisanChange = junnshisan[0]
    if junnshisanChange == "±0": continue
    if junnshisanChange == "赤転": continue
    if (
        junnshisanChange != "大幅増" and
        junnshisanChange != "黒転" and
        junnshisanChange != "赤拡"
    ):
        if junnshisanChange < -0.2621: continue
    cash = pl[8]
    if cash[1] < 61000000: continue
    if symbol in ignoreList: continue
    if symbol not in netIncomeDict: continue
    if netIncomeDict[symbol] < -494355000: continue
    if symbol not in epsDict: continue
    if epsDict[symbol] < -104.8953: continue
    if symbol not in last_annual_revenueDict: continue
    if last_annual_revenueDict[symbol] < 794621000: continue
    if symbol not in price_revenue_ttmDict: continue
    if price_revenue_ttmDict[symbol] > 11.75388472: continue
    # if symbol in ignoreSymbolList: continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSectorFirst: continue
    if symbol not in dataDictJP: continue
    if symbol not in similarCompanyDict: continue
    if symbol not in rironkabukaDict: continue
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
    if len(npArr) < length: continue
    if npArr[-1][3] / shisannkachiDict[symbol] > 7.8: continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if zandaka[0][1] < 900: continue
    # if npArr[-1][3] >= rironkabukaDict[symbol] - 5: continue
    # if npArr[-1][3] * npArr[-1][4] < 315601: continue
    dataDict[symbol] = npArr
    contractDict[symbol] = ibc.GetStockContractQuickJP(symbol)
    contractSmartDict[symbol] = ibc.GetStockContractSmartJP(symbol)

fetchList = list(dataDict.keys())
priceDict = {}
sem = asyncio.Semaphore(int(len(fetchList))/3)
loop = asyncio.get_event_loop()
results = loop.run_until_complete(fetch_tickers(fetchList))
# with ThreadPoolExecutor(max_workers=100) as executor:
#     futures = [executor.submit(HandleGetPrice, symbol) for symbol in list(dataDict.keys())]
#     for future in as_completed(futures):
#         result = future.result()
#         if result[1] < 1: continue
#         symbol = result[0]
#         price = result[1]
#         if price < 1: 
#             ignoreSymbolList.append(symbol)
#             continue
#         # if price >= rironkabukaDict[symbol] - 5: continue
#         priceDict[symbol] = price
#         print(symbol, price)

# DumpCsv(ignoreSymbolPath, ignoreSymbolList)

# priceDict = {}
# for symbol in list(dataDict.keys()):
#     # ask, bid = ibc.GetAskBidJP(symbol)
#     # ask = ibc.GetAskJP(symbol)
#     price = GetPrice(symbol)
#     priceDict[symbol] = price
#     print(symbol, price)
print(priceDict)

topPefToAvg = 1
topSymbol = ""
topSimilarCompanyAvg = 1
for symbol, npArr in dataDict.items():
    if symbol not in priceDict: continue
    if priceDict[symbol] > avalible_price: continue
    if symbol not in ryuudoumeyasuDict: continue
    if ryuudoumeyasuDict[symbol][0] <= 100: continue
    treasuryShares = treasurySharesDict[symbol]
    if treasuryShares[0] < treasuryShares[1]: continue
    if shijouDict[symbol] == "東証プライム": continue
    if symbol not in gyoushuDict: continue
    if gyoushuDict[symbol] in ignoreSector: continue
    if priceDict[symbol] >= rironkabukaDict[symbol] - 5: continue
    if symbol not in priceDict: continue
    if npArr[-1][4] >= npArr[-2][4]: continue
    if npArr[-1][3] < 327: continue
    if npArr[-1][3] / npArr[-1][0] < 0.8540462428: continue
    if npArr[-1][3] / npArr[-2][3] < 0.7722095672: continue
    if (
        npArr[-1][4] <= npArr[-2][4] and
        npArr[-2][4] <= npArr[-3][4] and
        npArr[-3][4] <= npArr[-4][4] and
        npArr[-1][3] <= npArr[-1][0] and
        npArr[-2][3] <= npArr[-2][0] and
        npArr[-3][3] / npArr[-4][0] > 1.1
    ): continue
    if (
        npArr[-3][3] / npArr[-3][0] > 1.21 and
        npArr[-3][4] / npArr[-4][4] > 7 and
        npArr[-3][0] < npArr[-4][2]
    ): continue
    if symbol not in financialDetailDict: continue
    if shuuekiDict[symbol] < 0.02: continue
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
    similarPerfomanceList = np.empty(0)
    similarCompanyList = similarCompanyDict[symbol]
    similarPerfomanceList = np.array([priceDict[t] / dataDict[t][-1][3] for t in similarCompanyList if t in priceDict])
    # try:
    #     res = split_list_average_low(similarPerfomanceList)
    # except: continue
    # similarCompanyAvg = res[0]
    if len(similarPerfomanceList) < 1: continue
    similarCompanyAvg = np.min(similarPerfomanceList)
    # print(similarCompanyAvg)
    performance = priceDict[symbol] / npArr[-1][3]
    pefToAvg = performance/similarCompanyAvg
    if npArr[-1][3] * similarCompanyAvg - priceDict[symbol] < 18: continue
    if pefToAvg < topPefToAvg:
        topPefToAvg = pefToAvg
        topSymbol = symbol
        topSimilarCompanyAvg = similarCompanyAvg
target = dataDict[topSymbol][-1][3] * topSimilarCompanyAvg
ibc.HandleBuyLimitTpTrailWithContract(contractDict[topSymbol], contractSmartDict[topSymbol], 100, int(target))
print(topSymbol, target, rironkabukaDict[topSymbol])