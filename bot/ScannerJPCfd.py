import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.dataHandler.chart import GetChart
from modules.dataHandler.lending import GetLending
from modules.loadPickle import LoadPickle
from modules.csvDump import LoadCsv, dump_result_list_to_csv
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate
from modules.movingAverage import SmaArr
from datetime import datetime
import math
from modules.dict import take, rank_by_quantile
from modules.rsi import get_rsi
from modules.f1score import calculate_f1_score
from modules.obv import GetOBV
from modules.macd import MacdHistorical
from modules.smc import GetFvg
from modules.rironkabukaFormula import GetRironkabuka
from modules.dataHandler.category import GetCategoryDict
from modules.dataHandler.nisshokin import GetNisshokin
from modules.rsi import GetRsi

def rankRironkabuka(dataDict, plbsDict):
    rironkabukaDict = {}
    for symbol, npArr in dataDict.items():
        plbscfdividend = plbsDict[symbol]
        pl = plbscfdividend[0]
        plLength = len(pl[0])
        epsIdx = 6
        if plLength == 7: epsIdx = 4
        elif plLength == 8: epsIdx = 5
        elif plLength == 9: epsIdx = 5
        elif plLength == 10: epsIdx = 6
        elif plLength == 11: epsIdx = 5
        eps = pl[-1][epsIdx]
        if eps == "-": continue
        if eps == 0: continue
        if eps == "赤字": continue

        bs = plbscfdividend[1]
        bsLength = len(bs[0])
        jikoushihonhiritsu = bs[-1][4]
        if jikoushihonhiritsu == 0: continue
        bpsIdx = 8
        if bsLength == 8: bpsIdx = 7
        elif bsLength == 7: bpsIdx = 6
        elif bsLength == 6: bpsIdx = 5
        bps = bs[-1][bpsIdx]
        if bps == "-": continue
        rironkabuka = GetRironkabuka(bps,
            jikoushihonhiritsu, 
            eps, npArr[-1][3])[0]
        rironkabukaDict[symbol] = rironkabuka
    rank = rank_by_quantile(rironkabukaDict, 10)
    return rank

plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
quarterPath = f"{rootPath}/backtest/pickle/pro/compressed/quarter.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
dataDictJP = LoadPickle(dataPathJP)

marginPath = f"{rootPath}/backtest/pickle/pro/compressed/margin.p"
marginDict = LoadPickle(marginPath)

plbsDict = LoadPickle(plbsPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
shijousizeDict = LoadPickle(shijousizePath)

growthPath = f"{rootPath}/backtest/pickle/pro/compressed/growth.p"
growthDict = LoadPickle(growthPath)
# quarterDict = LoadPickle(quarterPath)


valuepegPath = f"{rootPath}/backtest/pickle/pro/compressed/valuepeg.p"
valuepegDict = LoadPickle(valuepegPath)

nisshokinPath = f"{rootPath}/backtest/pickle/pro/compressed/nisshokin.p"
nisshokinDict = LoadPickle(nisshokinPath)

zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
zandakaDict = LoadPickle(zandakaPath)

officerHoldPath = f"{rootPath}/backtest/pickle/pro/compressed/officerHold.p"
officerHoldDict = LoadPickle(officerHoldPath)

shortPathJP = f"{rootPath}/backtest/pickle/pro/compressed/short.p"
shortDict = LoadPickle(shortPathJP)

chartPath = f"{rootPath}/backtest/pickle/pro/compressed/chart.p"
chartDict = LoadPickle(chartPath)

categoryDict = GetCategoryDict()

def Backtest(dataDict, length, sampleArr, 
    shortDict, zandakaDict, chartDict,
    plbsDict, categoryDict):

    rironkabukaRank = rankRironkabuka(dataDict, plbsDict)

    safetyPath = f"{rootPath}/backtest/pickle/pro/compressed/safety.p"
    safetyDict = LoadPickle(safetyPath)
    
    i = length
    today = sampleArr[i-1][5]
    perfDict = {}
    categoryPbrDict = {'電気機器': 3.41}
    hhCount = 0
    llCount = 0

    for symbol, npArr in dataDict.items():
        if npArr[i-1][3] > npArr[i-1][0]: continue
        if npArr[i-1][3] > npArr[i-2][2]: continue
        if npArr[i-1][3] > npArr[i-3][2]: continue
        if npArr[i-1][3] > npArr[i-2][1]: continue
        if npArr[i-1][4] < npArr[i-2][4]: continue
        if (
            npArr[i-2][4] < npArr[i-4][4] and
            npArr[i-1][4] > npArr[i-2][4]
        ): continue

        diff = abs(npArr[i-1][3] - npArr[i-1][0])
        if diff > 0:
            if (
                npArr[i-1][1] > npArr[i-2][1] and
                npArr[i-1][3] < npArr[i-2][3] and
                (
                    (npArr[i-1][1]-npArr[i-1][3]) / 
                    diff
                ) > 7.9
            ): continue

        volArr = npArr[:,4]
        volSma5 = SmaArr(volArr, 5)
        volSma30 = SmaArr(volArr, 30)
        if volSma5[i-1] < volSma30[i-1]: continue

        rsi = GetRsi(npArr[:,3])
        if (
            rsi[i-1] < 50 or
            rsi[i-1] > 80
        ): continue

        if symbol not in plbsDict: continue
        plbscfdividend = plbsDict[symbol]
        pl = plbscfdividend[0]
        
        plLength = len(pl[0])
        epsIdx = 6
        roeIdx = 7
        roaIdx = 8
        if plLength == 7: 
            epsIdx = 4
            roeIdx = 5
            roaIdx = 6
        elif plLength == 8: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
        elif plLength == 9: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
        elif plLength == 10: epsIdx = 6
        elif plLength == 11: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
        eps = pl[-1][epsIdx]
        plLast = pl[-1][0]
        if "予" in plLast:
            if pl[-1][epsIdx] != "-":
                eps = min(pl[-1][epsIdx], pl[-2][epsIdx])
            else:
                eps = pl[-2][epsIdx]
        if eps == 0: continue
        if eps == "赤字": continue

        cf = plbscfdividend[2]
        cfIdx = len(cf) - 1
        if len(cf) < 1: continue

        if len(plbscfdividend[0]) < 2: continue
        bs = plbscfdividend[1]
        bsLength = len(bs[0])
        if bsLength not in [6, 7, 8, 9]: continue
        jikoushihonhiritsu = bs[-1][4]
        if jikoushihonhiritsu == 0: continue
        bpsIdx = 8
        if bsLength == 8: bpsIdx = 7
        elif bsLength == 7: bpsIdx = 6
        elif bsLength == 6: bpsIdx = 5

        bps = bs[-1][bpsIdx]
        if bps == "-": continue

        if bsLength in [8, 9]:
            yuurishifusaihiritsuIdx = 7
            if bsLength == 8:
                yuurishifusaihiritsuIdx = 6

            yuurishifusaihiritsu = bs[-1][yuurishifusaihiritsuIdx]
            if yuurishifusaihiritsu == "-": continue
        rironkabuka = GetRironkabuka(bps,
        jikoushihonhiritsu, 
        eps, npArr[i-1][3])[0]
        # if max(npArr[:,1][:i]) >= rironkabuka: continue
        # if npArr[i-1][3] >= rironkabuka: continue

        # if plLength in [7, 10, 11, 12]:
        #     uriage2 = pl[-2][1] 
        #     uriage = pl[-1][1] 
        #     if uriage == "-": 
        #         uriage = uriage2
        #     if uriage < uriage2: continue

        if plLength in [9, 10, 11, 12]:
            eigyouriekiritsuIdx = 9
            if plLength == 9:
                eigyouriekiritsuIdx = 8
            elif plLength == 10:
                eigyouriekiritsuIdx = 8
            elif plLength == 11:
                eigyouriekiritsuIdx = 8
            eigyourieki2 = pl[-2][2]
            eigyourieki = pl[-1][2]
            # if eigyourieki == "-": 
            #     eigyourieki = eigyourieki2
            # if eigyourieki < eigyourieki2: continue
            
            # eigyouriekiritsu2 = pl[-2][eigyouriekiIdx]
            # eigyouriekiritsu = pl[-1][eigyouriekiIdx]
            # if eigyouriekiritsu == "-":
            #     eigyouriekiritsu = eigyouriekiritsu2
            # if eigyouriekiritsu < eigyouriekiritsu2:
            #     continue

        # if plLength in [8, 9, 10, 11, 12]:
        #     keijyouriekiIdx = 3
        #     if plLength == 8:
        #         keijyouriekiIdx = 2
        #     keijyourieki2 = pl[-2][keijyouriekiIdx]
        #     keijyourieki = pl[-1][keijyouriekiIdx]
        #     if keijyourieki == "-":
        #         keijyourieki = keijyourieki2
        #     if keijyourieki < keijyourieki2: continue

        toukirieki2 = pl[-2][4]
        toukirieki = pl[-1][4]
        if toukirieki == "-":
            toukirieki = toukirieki2
        if toukirieki < toukirieki2:
            continue

        roaIdx = 8
        if plLength == 7: 
            epsIdx = 4
            roeIdx = 5
            roaIdx = 6
        elif plLength == 8: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
        elif plLength == 9: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7
        elif plLength == 10: epsIdx = 6
        elif plLength == 11: 
            epsIdx = 5
            roeIdx = 6
            roaIdx = 7

        # eps2 = pl[-2][epsIdx]
        # eps = pl[-1][epsIdx]
        # if eps == "-": eps = eps2
        # if eps < eps2: continue

        # roe2 = pl[-2][roeIdx]
        # roe = pl[-1][roeIdx]
        # if roe == "-": roe = roe2
        # if roe == "赤字": continue
        # if roe2 != "赤字":
        #     if roe < roe2: continue

        # roa2 = pl[-2][roaIdx]
        # roa = pl[-1][roaIdx]
        # if roa == "-": roa = roa2
        # if roa == "赤字": continue
        # if roa2 != "赤字":
        #     if roa < roa2: continue

        # dividend = plbscfdividend[3]
        # ichikabuhaitou2 = dividend[-2][1]
        # ichikabuhaitou = int(str(dividend[-1][1]).replace("*",""))
        # if ichikabuhaitou < ichikabuhaitou2:
        #     continue

        if symbol in safetyDict:
            safety = safetyDict[symbol]
            safetyShort = safety[0]
            safetyIdx = len(safetyShort) - 1
            gesshoubairitsu = safetyShort[safetyIdx][5]
            if gesshoubairitsu != "-":
                if gesshoubairitsu >= 75.5: continue

        mc = GetChart(symbol, 'mc', npArr[i-1][5])
        if mc == 0: continue

        kaizan = GetNisshokin(symbol, "kaizan", npArr[i-1][5])
        floatShares = mc / npArr[i-1][3]
        if kaizan / floatShares < 3.15208914e-10: continue

        kaizan_s = GetNisshokin(symbol, "kaizan_s", npArr[i-1][5])
        kaizan_h = GetNisshokin(symbol, "kaizan_h", npArr[i-1][5])
        if (kaizan_s - kaizan_h) / floatShares < -1.42857143e+02: continue

        perfDict[symbol] = rironkabuka / npArr[i-1][3]

    perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1], reverse=True))
    print(perfDict)
    
    categoryList = []
    tradeList = []
    for symbol in list(perfDict.keys()):
        # category = categoryDict[symbol]
        # if category in categoryList: continue
        # categoryList.append(category)
        tradeList.append(symbol)
        if len(tradeList) > 1: break
    return tradeList

group = ""
length = len(dataDictJP["9101"])
dataDict = dataDictJP

cleanDataDict = {}
for symbol, npArr in dataDict.items():
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr
dataDict = cleanDataDict
cleanDataDict = {}

sampleArr = dataDict["^N225"]
sampleArr = sampleArr[-length:]

import pandas as pd
df = pd.read_csv(f"{rootPath}/data/ib_cfd_jp.csv")
cfd = df['Symbol'].values.tolist()

cleanDataDict = {}
shijousizeList = ['ＰＲＭ大型', 'ＰＲＭ中型', 'ＳＴＤ中型']
for symbol, npArr in dataDict.items():
    if symbol not in categoryDict: continue
    if categoryDict[symbol] in [
        '精密機器', '輸送用機器', 
        '電気・ガス業', '銀行業']: continue
    # if symbol not in shortDict: continue
    # if symbol not in zandakaDict: continue
    # if symbol not in chartDict: continue
    if symbol not in cfd: continue
    # if symbol not in gainnerList: continue
    # if symbol not in nisshokinDict: continue
    if symbol in shijousizeDict:
        shijousize = shijousizeDict[symbol]
        if shijousizeDict[symbol] in ['ＧＲＴ中型', 'ＳＴＤ小型', 'ＧＲＴ小型']:
            continue
    # if shijousize not in shijousizeList: continue
    # if symbol not in plbsDict: continue
    plbs = plbsDict[symbol]
    if len(plbs[0]) < 3: continue
    plIdx = -1
    plLast = plbs[0][-1][0]
    if "予" in plLast: plIdx = -2
    pl = plbs[0][plIdx]
    pl2 = plbs[0][plIdx-1]
    
    plLength = len(pl)
    epsIdx = 6
    roeIdx = 7
    roaIdx = 8
    if plLength == 7: 
        epsIdx = 4
        roeIdx = 5
        roaIdx = 6
    elif plLength == 8: 
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
    elif plLength == 9: 
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
    elif plLength == 10: epsIdx = 6
    elif plLength == 11: 
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7

    eps = pl[epsIdx]
    if eps == "赤字": continue

    roa = pl[roaIdx]
    if roa == "-": continue

    if plLength in [7, 10, 11, 12]:
        uriage = pl[1]
        if uriage == "-": continue
        if uriage < 123000000: continue

    if plLength in [9, 10, 11, 12]:
        eigyouriekiIdx = 2
        eigyouriekiritsuIdx = 9
        if plLength == 9:
            eigyouriekiritsuIdx = 8
        elif plLength == 10:
            eigyouriekiritsuIdx = 8
        elif plLength == 11:
            eigyouriekiritsuIdx = 8

        eigyourieki = pl[eigyouriekiIdx]
        if "*" in str(eigyourieki): continue

    bs = plbs[1][-1]
    bs2 = plbs[1][-2]
    bsLength = len(bs)

    junnshisan = int(bs[2])
    junnshisan2 = int(bs2[2])
    if junnshisan/junnshisan2 < 0.1: continue

    if bsLength not in [4, 8, 9]: continue
    yuurishifusaiIdx = 6
    if bsLength == 8: yuurishifusaiIdx = 5

    yuurishifusai = bs[yuurishifusaiIdx]
    if yuurishifusai == "-": continue
    
    cf = plbs[2][-1]
    cfLength = len(cf)

    toushicf = cf[2]
    if toushicf == "-": continue
    
    if len(plbs[3]) > 0:
        dividend = plbs[3][-1]
        dividendLength = len(dividend)

        if dividendLength in [6, 8, 9, 10]:
            jishakabukaiIdx = 5
            if dividendLength == 6: jishakabukaiIdx = 1
            elif dividendLength == 9: jishakabukaiIdx = 4

            jishakabukai = dividend[jishakabukaiIdx]
            if jishakabukai == "赤字": continue

            if len(plbs[3]) > 1:
                dividend2 = plbs[3][-2]
                jishakabukai2 = dividend2[jishakabukaiIdx]
                if jishakabukai2 == "赤字": continue

    if symbol not in ryuudoumeyasuDict: continue
    if ryuudoumeyasuDict[symbol][0] < 5001: continue

    if symbol in growthDict:
        growth = growthDict[symbol][0]
        if len(growth) < 1: continue

    if symbol in officerHoldDict:
        hold = officerHoldDict[symbol]
        if hold[5] >= 0.735: continue
    
    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    cleanDataDict[symbol] = npArr

print(len(cleanDataDict))
symbolList = Backtest(cleanDataDict, length, 
    sampleArr, shortDict, zandakaDict, chartDict, 
    plbsDict, categoryDict)
print(symbolList)

res = []
for symbol in symbolList:
    res.append([symbol,cleanDataDict[symbol][-1][3]])
csvPath = f"{rootPath}/data/ScannerJP.csv"
header = ["Symbol","Close"]
dump_result_list_to_csv(res,csvPath,header)