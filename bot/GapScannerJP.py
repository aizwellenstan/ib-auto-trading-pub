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

sem = None
priceDict = {}

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
        # print('{} started'.format(self.ticker))
        close = await self.op()
        # print('{} ended'.format(self.ticker))

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

def main(DEBUG=False):
    global sem, priceDict, contractDict
    rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
    shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
    plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
    sharePath = f"{rootPath}/backtest/pickle/pro/compressed/share.p"
    eventPath = f"{rootPath}/backtest/pickle/pro/compressed/event.p"
    # shisannkachiPath = f"{rootPath}/backtest/pickle/pro/compressed/shisannkachi.p"
    shijouPath = f"{rootPath}/backtest/pickle/pro/compressed/shijou.p"
    gyoushuPath = f"{rootPath}/backtest/pickle/pro/compressed/gyoushu.p"
    financialDetailPath = f"{rootPath}/backtest/pickle/pro/compressed/financialDetail.p"
    # shuuekiPath = f"{rootPath}/backtest/pickle/pro/compressed/shuueki.p"
    haitourimawariPath = f"{rootPath}/backtest/pickle/pro/compressed/haitourimawari.p"
    # zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
    # inventoryPath = f"{rootPath}/backtest/pickle/pro/compressed/inventoryJP.p"
    # netIncomeQPath = f"{rootPath}/backtest/pickle/pro/compressed/netIncomeQJP.p"
    # treasurySharesPath = f"{rootPath}/backtest/pickle/pro/compressed/treasurySharesJP.p"
    # dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
    dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
        
    rironkabukaDict = LoadPickle(rironkabukaPath)
    shijousizeDict = LoadPickle(shijousizePath)
    shareDict = LoadPickle(sharePath)
    eventDict = LoadPickle(eventPath)
    plbsDict = LoadPickle(plbsPath)
    # shisannkachiDict = LoadPickle(shisannkachiPath)
    shijouDict = LoadPickle(shijouPath)
    gyoushuDict = LoadPickle(gyoushuPath)
    financialDetailDict = LoadPickle(financialDetailPath)
    # shuuekiDict = LoadPickle(shuuekiPath)
    haitourimawariDict = LoadPickle(haitourimawariPath)
    # treasurySharesDict = LoadPickle(treasurySharesPath)
    # zandakaDict = LoadPickle(zandakaPath)
    # inventoryDict = LoadPickle(inventoryPath)
    # netIncomeQDict = LoadPickle(netIncomeQPath)
    # dataDictUS = LoadPickle(dataPathUS)
    dataDictJP = LoadPickle(dataPathJP)

    # dataDict = dataDictUS
    # dataDict.update(dataDictJP)


    industryDict = GetAttrJP("industry")
    epsDict = GetAttrJP("basic_eps_net_income")
    last_annual_revenueDict = GetAttrJP("last_annual_revenue")
    assetDict = GetAttrJP("total_current_assets")
    liabilitiesDict = GetAttrJP("total_liabilities_fy")
    length = len(dataDictJP["9101"])

    count = 3945
    import itertools
    industryDict = dict(itertools.islice(industryDict.items(), count))

    dataDict = dataDictJP
    similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

    from modules.data import GetDataWithVolumeDate
    sampleArrJP = GetDataWithVolumeDate("9101")
    sampleArrJP = sampleArrJP[-length:]

    newEventDict = {}
    for symbol, items in eventDict.items():
        enventDateDict = {}
        for item in items:
            if len(item) > 2: continue
            if item[0] in enventDateDict:
                enventDateDict[item[0]].append([item[1]])
            else:
                enventDateDict[item[0]] = [item[1]]
        newEventDict[symbol] = enventDateDict
    eventDict = newEventDict

    eventIgnoreList = []
    ignoreDict = {}
    for i in range(length-150, length):
        btoday = sampleArrJP[i][5]
        for symbol, npArr in dataDict.items():
            if symbol in eventIgnoreList: continue
            if symbol not in eventDict:
                eventIgnoreList.append(symbol)
                continue
            ignore = False
            if symbol in ignoreDict:
                if ignoreDict[symbol] < 18: ignore = True
                ignoreDict[symbol] += 1
            if ignore: continue
            noTrade = False
            events = eventDict[symbol].get(btoday,0)
            if events != 0:
                eventLength = len(events)
                sell = False
                for event in events:
                    if "再IN" in event:
                        sell = True
                    elif "5%ルール" in event:
                        sell = True
                    elif "について" in event:
                        sell = True
                    elif "変更" in event:
                        sell = True
                if sell:
                    ignoreDict[symbol] = 0

    for symbol, v in ignoreDict.items():
        if v < 18:
            eventIgnoreList.append(symbol)



    dataDict = {}
    ignoreList = [
        "Electronic Production Equipment", 
        "Telecommunications Equipment", 
        "Environmental Services",
        "Biotechnology",
        "Commercial Printing/Forms",
        "Trucks/Construction/Farm Machinery",
        "Auto Parts: OEM",
        "Tools & Hardware",
        "Metal Fabrication",
        "Medical Specialties",
        "Electronics/Appliances",
        "Pulp & Paper",
        "Electrical Products"
    ]

    ignoreSector = [
        "紙・パルプ",
        "鉱業",
        "繊維",
        "保険",
        "建設",
        "海運",
        "銀行",
        "情報通信",
        "精密",
        "電力・ガス",

        "鉄鋼",
        
        # "電機",
        # "機械",
        # "不動産",
        # "その他製造",
        # "医薬品",
        # "化学",
        # "食品",
        # "ゴム",
        "証券",
        # "窯業",
        # "金属製品"

        # "空運"
        # "その他金融"
    ]

    shijousizeList = ['ＰＲＭ大型', 'ＧＲＴ中型', 'ＳＴＤ中型', 'ＰＲＭ中型', 'ＳＴＤ小型', 'ＧＲＴ小型']

    for symbol, industry in industryDict.items():
        if symbol not in shijousizeDict: continue
        shijousize = shijousizeDict[symbol]
        if shijousize not in shijousizeList: continue
        if symbol in eventIgnoreList: continue
        if industry in ignoreList: continue
        if symbol not in plbsDict: continue
        plbs = plbsDict[symbol]
        if len(plbs[0]) < 2: continue
        pl = plbs[0][-2]
        keijyouriekiIdx = 3
        junnriekiIdx = 4
        hokatsuriekiIdx = 5
        epsIdx = 6
        roeIdx = 7
        roaIdx = 8

        eigyouriekiritsuIdx = 9
        gennkaritsuIdx = 10
        hankannhiritsuIdx = 11
        
        plLength = len(pl)
        uriage = 0
        eigyourieki = 0
        keijyourieki = 0
        eigyouriekiritsu = 0
        if plLength == 7: continue
        # if plLength == 10: continue
        if plLength == 11: continue
        if plLength == 8:
            keichoushuekiIdx = 1
            keichoushueki = pl[keichoushuekiIdx]
            # if keijyourieki < 1110000000000: continue
            junnriekiIdx = 3
            hokatsuriekiIdx = 4
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
            keijyouriekiIdx = 2
            keijyourieki = pl[keijyouriekiIdx]
        elif plLength == 9:
            eigyoushuekiIdx = 1
            eigyoushueki = pl[eigyoushuekiIdx]
            if eigyoushueki == "-": continue
            # if eigyoushueki < 1310000000000: continue
            junnriekiIdx = 3
            hokatsuriekiIdx = 4
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
            eigyouriekiritsuIdx = 8
            eigyouriekiIdx = 2
            eigyourieki = pl[eigyouriekiIdx]
            eigyouriekiritsuIdx = 8
            eigyouriekiritsu = pl[eigyouriekiritsuIdx]
        elif plLength != 10:
            uriageIdx = 1
            uriage = pl[uriageIdx]
            eigyouriekiIdx = 2
            eigyourieki = pl[eigyouriekiIdx]
            keijyouriekiIdx = 3
            keijyourieki = pl[keijyouriekiIdx]
            junnriekiIdx = 4
            eigyouriekiritsuIdx = 9
            eigyouriekiritsu = pl[eigyouriekiritsuIdx]
            gennkaritsuIdx = 10
            gennkaritsu = pl[gennkaritsuIdx]
            if gennkaritsu == "-": continue
            # if gennkaritsu > 95.34: continue
            # hankannhiritsuIdx = 11
            # hankannhiritsu = pl[hankannhiritsuIdx]
        keijyourieki = pl[keijyouriekiIdx]
        junnrieki = pl[junnriekiIdx]
        hokatsurieki = pl[hokatsuriekiIdx]
        eps = pl[epsIdx]
        roe = pl[roeIdx]
        roa = pl[roaIdx]
        if keijyourieki == "-": continue
        # if hokatsurieki != "-":
        #     if int(hokatsurieki) < -133000000000: continue
        if eps == "-": continue
        if eps == "赤字": continue

        if len(plbs[1]) < 2: continue
        bs = plbs[1][-1]
        bs2 = plbs[1][-2]
        bsLength = len(bs)
        if bsLength != 7 and bsLength != 9: continue
        soushisannIdx = 1
        soushisann = bs[soushisannIdx]
        # if soushisann < 120000000000: continue
        junnshisanIdx = 2
        kabunushishihonnIdx = 3
        riekijouyokinIdx = 5
        junnshisan = int(bs[junnshisanIdx])
        junnshisan2 = int(bs2[junnshisanIdx])
        if junnshisan/junnshisan2 < 0.1: continue
        kabunushishihonn = bs[kabunushishihonnIdx]
        if kabunushishihonn == "-": continue
        riekijouyokin = bs[riekijouyokinIdx]
        if riekijouyokin == "-": continue

        cf = plbs[2][-1]
        cfLength = len(cf)
        if cfLength != 8: continue
        eigyoucf = int(cf[1])
        if eigyoucf < -13000000000: continue
        toushicf = cf[2]
        if toushicf == "-": continue
        gennkin = cf[6]
        if gennkin < 47800000: continue
        cf2 = plbs[2][-2]
        gennkin2 = cf2[6]
        if gennkin2 < 47800000: continue
        eigyoucfmargin = cf[7]
        if eigyoucfmargin == "-": continue

        if len(plbs[3]) < 1: continue
        dividend = plbs[3][-1]
        dividendLength = len(dividend)
        if dividendLength == 2: continue
        if dividendLength == 3: continue
        if dividendLength == 6: continue
        if dividendLength == 7: continue
        if dividendLength == 8: continue

        if dividendLength in [6, 10]:
            jishakabukaiIdx = 5
            soukanngennkeikouIdx = 7
            if dividendLength == 6:
                jishakabukaiIdx = 1
                soukanngennkeikouIdx = 3

            jishakabukai = dividend[jishakabukaiIdx]
            if jishakabukai == "赤字": continue
            if "*" in str(jishakabukai): continue

            soukanngennkeikou = dividend[soukanngennkeikouIdx]
            if (
                soukanngennkeikou != "-" and
                soukanngennkeikou != 0 and
                soukanngennkeikou != "赤字"
            ):
                if soukanngennkeikou > 99.8: continue

        if dividendLength in [3, 6, 7, 10]:
            kabunushisourimawariIdx = 9
            shihyourimawariIdx = 9
            if dividendLength == 3:
                kabunushisourimawariIdx = 1
                shihyourimawariIdx = 2
            elif dividendLength == 6:
                kabunushisourimawariIdx = 4
                shihyourimawariIdx = 5
            elif dividendLength == 7:
                kabunushisourimawariIdx = 5
                shihyourimawariIdx = 6
            kabunushisourimawari = dividend[kabunushisourimawariIdx]
            shihyourimawari = dividend[shihyourimawariIdx]
            if shihyourimawari == "赤字": continue

        if dividendLength in [4, 10]:
            junnshisanhaitouritsuIdx = 4
            if dividendLength == 4:
                junnshisanhaitouritsuIdx = 3

            haitouseikouIdx = 2
            haitouseikou = dividend[haitouseikouIdx]

            junnshisanhaitouritsu = dividend[junnshisanhaitouritsuIdx]
            if junnshisanhaitouritsu == "赤字": continue

        jishakabukaiIdx = 5
        if dividendLength in [5, 6, 7, 10]:
            if dividendLength == 5:
                jishakabukaiIdx = 2
            elif dividendLength == 6:
                jishakabukaiIdx = 1
            elif dividendLength == 7:
                jishakabukaiIdx = 2

            jishakabukai = dividend[jishakabukaiIdx]
            if jishakabukai == "赤字": continue
            if "*" in str(jishakabukai): continue

        if symbol in ignoreList: continue
        if symbol not in epsDict: continue
        if epsDict[symbol] < -104.8953: continue
        if symbol not in last_annual_revenueDict: continue
        if last_annual_revenueDict[symbol] < 794621000: continue
        # if symbol in ignoreSymbolList: continue
        if symbol not in gyoushuDict: continue
        if gyoushuDict[symbol] in ignoreSector: continue
        if symbol not in dataDictJP: continue
        if symbol not in similarCompanyDict: continue
        if symbol not in rironkabukaDict: continue
        # if symbol not in shisannkachiDict: continue
        if symbol not in shijouDict: continue
        if symbol not in haitourimawariDict: continue
        if haitourimawariDict[symbol] > 0.032: continue
        if symbol not in shareDict: continue
        npArr = dataDictJP[symbol]
        if len(npArr) < length: continue
        # if npArr[-1][3] / shisannkachiDict[symbol] > 7.8: continue
        dataDict[symbol] = npArr
        contractDict[symbol] = ibc.GetStockContractQuickJP(symbol)
        contractSmartDict[symbol] = ibc.GetStockContractSmartJP(symbol)

    fetchList = list(dataDict.keys())
    sem = asyncio.Semaphore(int(len(fetchList))/3)
    if not DEBUG:
        while(ib.sleep(2)):
            currentTime = ib.reqCurrentTime()
            hour = currentTime.hour
            minute = currentTime.minute
            sec = currentTime.second
            print(hour, minute, sec)
            if hour == 0 and minute >= 0 and sec >= 5:
                break
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(fetch_tickers(fetchList))

    topPefToAvg = 1
    topSymbol = ""
    topSimilarCompanyAvg = 1
    for symbol, npArr in dataDict.items():
        if symbol not in priceDict: continue
        # if not DEBUG:
        if priceDict[symbol] > avalible_price: continue
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
        if financialDetailDict[symbol][0] != 0:
            if financialDetailDict[symbol][0] < 3:
                continue
        
        similarPerfomanceList = np.empty(0)
        similarCompanyList = similarCompanyDict[symbol]
        similarPerfomanceList = np.array([priceDict[t] / dataDict[t][-1][3] for t in similarCompanyList if t in priceDict])
    
        if len(similarPerfomanceList) < 1: continue
        similarCompanyAvg = np.min(similarPerfomanceList)
        performance = priceDict[symbol] / npArr[-1][3]
        pefToAvg = performance/similarCompanyAvg
        if npArr[-1][3] * similarCompanyAvg - priceDict[symbol] < 18: continue
        if pefToAvg < topPefToAvg:
            topPefToAvg = pefToAvg
            topSymbol = symbol
            topSimilarCompanyAvg = similarCompanyAvg
    print(priceDict)
    target = dataDict[topSymbol][-1][3] * topSimilarCompanyAvg
    if not DEBUG:
        ibc.HandleBuyLimitTpTrailWithContract(contractDict[topSymbol], contractSmartDict[topSymbol], 100, int(target))
    print(topSymbol, target, rironkabukaDict[topSymbol])

if __name__ == "__main__":
    main()
    # main(DEBUG=True)