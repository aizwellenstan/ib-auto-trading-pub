from pathlib import Path
rootPath = Path(__file__).parent.parent
import os
rootPath = os.path.relpath(rootPath, os.path.dirname(os.path.abspath(__file__)))
import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle

from modules.csvDump import LoadCsv, dump_result_list_to_csv
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate
from modules.movingAverage import SmaArr
from datetime import datetime
# from modules.upDownRatio import GetUpDownRatio
from numba import njit
import math
from modules.dict import take
from modules.rci import rciArr
from modules.rsi import get_rsi
from modules.f1score import calculate_f1_score
from modules.obv import GetOBV
from modules.macd import MacdHistorical
from modules.smc import GetFvg
from modules.rironkabukaFormula import GetRironkabuka
from modules.bollingerBands import GetBollingerBands
from modules.corr import GetCorr, GetCorrVolume1, GetCorrCl1, GetCorrCompareVol1, GetCorrCompareC1
from modules.dataHandler.category import GetCategoryDict
from modules.dataHandler.chart import GetDataDict

# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    average_high = np.mean(high_values)
    
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    average_low = np.mean(low_values)
    
    return np.array([average_high, average_low])

plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
shijousizePath = f"{rootPath}/backtest/pickle/pro/compressed/shijousize.p"
growthPath = f"{rootPath}/backtest/pickle/pro/compressed/growth.p"
quarterPath = f"{rootPath}/backtest/pickle/pro/compressed/quarter.p"

marginPath = f"{rootPath}/backtest/pickle/pro/compressed/margin.p"
marginDict = LoadPickle(marginPath)

plbsDict = LoadPickle(plbsPath)
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)
shijousizeDict = LoadPickle(shijousizePath)
growthDict = LoadPickle(growthPath)
# quarterDict = LoadPickle(quarterPath)
dataDictJP = GetDataDict()

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

employeePath = f"{rootPath}/backtest/pickle/pro/compressed/employee.p"
employeeDict = LoadPickle(employeePath)


def Backtest(dataDict, length,  
    shortDict, zandakaDict, chartDict,
    plbsDict, categoryDict, employeeDict):
    
    i = length
    signalDict = {}

    categoryPbrDict = {'電気機器': 3.41}
    
    for symbol, npArr in dataDict.items():
        if npArr[i-1][3] > npArr[i-1][1]: continue
        if npArr[i-2][4] < 1: continue
        # if (
        #     sampleArr[i-3][3] > sampleArr[i-3][0] and
        #     sampleArr[i-2][3] > sampleArr[i-2][0] and
        #     sampleArr[i-1][3] > sampleArr[i-1][0]
        # ):
        #     if (
        #         npArr[i-3][3] < npArr[i-3][0] and
        #         npArr[i-2][3] < npArr[i-2][0] and
        #         npArr[i-1][3] < npArr[i-1][0]
        #     ): continue
        # if (
        #     npArr[i-5][3] / npArr[i-5][0] <
        #     sampleArr[i-5][3] / sampleArr[i-5][0] and
        #     npArr[i-4][3] / npArr[i-4][0] <
        #     sampleArr[i-4][3] / sampleArr[i-4][0] and
        #     npArr[i-3][3] / npArr[i-3][0] <
        #     sampleArr[i-3][3] / sampleArr[i-3][0] and
        #     npArr[i-2][3] / npArr[i-2][0] <
        #     sampleArr[i-2][3] / sampleArr[i-2][0] and
        #     npArr[i-1][3] / npArr[i-1][0] <
        #     sampleArr[i-1][3] / sampleArr[i-1][0]
        # ): continue
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
        if (
            npArr[i-2][1] > npArr[i-3][1] and
            npArr[i-2][3] < npArr[i-3][3] and
            npArr[i-1][1] < npArr[i-2][1]
        ): continue
        if (
            npArr[i-3][4] > npArr[i-4][4] and
            npArr[i-1][4] > npArr[i-2][4] * 3 and
            npArr[i-3][1] > npArr[i-4][1] and
            npArr[i-2][1] > npArr[i-3][1] and
            npArr[i-1][1] > npArr[i-2][1]
        ): continue
        if (
            npArr[i-4][4] > npArr[i-5][4] and
            npArr[i-3][4] > npArr[i-4][4] and
            npArr[i-2][4] > npArr[i-3][4] * 5 and
            npArr[i-4][1] > npArr[i-5][1] and
            npArr[i-3][1] > npArr[i-4][1] and
            npArr[i-2][1] > npArr[i-3][1]
        ): continue
        if npArr[i-2][2] * npArr[i-1][4] < 4778345366: continue
        if npArr[i-1][3] < npArr[i-2][2]: continue
        if symbol in categoryDict:
            if categoryDict[symbol] in ['情報・通信業']:
                if npArr[i-1][4] / npArr[i-2][4] > 5: continue

        if (
            npArr[i-1][3] / npArr[i-4][0] <= 0.917262969588551 and
            npArr[i-1][3] / npArr[i-1][0] <= 0.9624589394650399
        ): continue

        if (
            (npArr[i-1][1] - npArr[i-1][2]) / 
            (abs(npArr[i-1][3]-npArr[i-1][0]) + 1)
        ) >= 151.92919921875: continue

        if (
            abs(npArr[i-1][3] - npArr[i-6][0]) /
            (abs(npArr[i-2][3] - npArr[i-7][0]) + 1)
        ) >= 41.325315739215526: continue

        if npArr[i-1][3] > npArr[i-1][0]:
            if (
                npArr[i-1][2] / npArr[i-1][0]
            ) >= 1: continue
        elif npArr[i-1][3] < npArr[i-1][0]:
            if (
                npArr[i-1][1] / npArr[i-1][0]
            ) <= 1: continue

        if npArr[i-1][3] < npArr[i-2][0]:
            if (
                npArr[i-1][1] / npArr[i-2][0]
            ) >= 1.0652741514360313: continue

        corr = GetCorr(npArr)
        if corr <= -0.26406876: continue
        if npArr[i-1][4] < npArr[i-2][4]:
            if corr >= 0.56198252: continue

        if npArr[i-1][4] < npArr[i-2][4]:
            corr = GetCorrVolume1(npArr)
            if corr >= 4.10438126e-01: continue
        
        if npArr[i-1][3] < npArr[i-2][3]:
            corr = GetCorrCl1(npArr)
            if corr >= 0.20047399: continue

        # if sampleArr[i-1][4] < sampleArr[i-2][4]:
        #     corr = GetCorrCompareVol1(npArr, sampleArr)
        #     if corr >= 1.65848872e-01: continue

        # corr = GetCorrCompareC1(npArr, sampleArr)
        # if sampleArr[i-1][3] < sampleArr[i-2][3]:
        #     if corr >= 2.29588673e-01: continue
        # elif sampleArr[i-1][3] > sampleArr[i-2][3]:
        #     if corr <= -1.93472494e-01: continue

        if symbol in categoryDict:
            if categoryDict[symbol] in ['海運業', '電気機器', 'その他製品', '不動産業']:
                closeArr = npArr[:,3]
                sma75 = SmaArr(closeArr, 75)
                if npArr[i-1][3] < sma75[i-1]: continue

        rsi = get_rsi(npArr[:,3], 10)
        if (
            rsi[i-4] > rsi[i-5] and
            rsi[i-3] > rsi[i-4] and
            rsi[i-1] < rsi[i-2]
        ): continue

        rsi = get_rsi(npArr[:,3], 7)
        if (
            rsi[i-4] > rsi[i-5] and
            rsi[i-3] > rsi[i-4] and
            rsi[i-1] < rsi[i-2]
        ): continue

        bollingerBands = GetBollingerBands(npArr, 2)
        lower = bollingerBands[1]
        if npArr[i-1][3] < lower[i-1]: continue

        obv = GetOBV(npArr)
        if obv[i-1] <= -95188251: continue

        deltaPeriod = 2
        b = 0
        s = 0
        for j in range(i-deltaPeriod, i):
            if npArr[j][3] > npArr[j][0]:
                b += npArr[j][4]
            elif npArr[j][3] < npArr[j][0]:
                s += npArr[j][4]
        b2 = 0
        s2 = 0
        for j in range(i-deltaPeriod-1, i-1):
            if npArr[j][3] > npArr[j][0]:
                b2 += npArr[j][4]
            elif npArr[j][3] < npArr[j][0]:
                s2 += npArr[j][4]

        d2 = b2 - s2
        if d2 != 0:
            delta = ((b-s) - d2) / d2
            if delta >= 27.555973387330056: continue

        closeArr = npArr[:,3]
        sma25 = SmaArr(closeArr, 25)
        bias25 = (npArr[i-1][3] - sma25[i-1]) / sma25[i-1]
        if bias25 < -0.2: continue
        if bias25 >= 0.7702747072343219: continue

        rci = rciArr(npArr[:,3])
        if (
            (rci[i-1] - rci[i-2]) / 
            rci[i-2]
        ) <= -14.000000000000046: continue

        rci = rciArr(npArr[:,4])
        if rci[i-1] <= -95: continue

        macdHist = MacdHistorical(npArr[:,4])
        if macdHist[i-1] <= -2083575.4696298428: continue

        bullFvg = 0
        bearFvg = 0
        bear = False
        fvg = GetFvg(npArr)
        for j in fvg:
            if math.isnan(j[0]): continue
            if j[3] > i-1:
                if j[0] > 0:
                    if j[1] - j[2] < 100: continue
                    if j[2] < npArr[i-1][3] or math.isnan(j[3]):
                        if bullFvg == 0:
                            bullFvg = j[2]
                        elif j[2] > bullFvg:
                            bullFvg = j[2]
                else:
                    if j[1] - j[2] < 100: continue
                    if j[3] > i-1 or math.isnan(j[3]):
                        if bearFvg == 0:
                            bearFvg = j[2]
                        elif j[2] < bearFvg:
                            bearFvg = j[2]
                    else:
                        bear = True
                        break
        if bear: continue
        if bullFvg > 0 and bearFvg > 0:
            rr = (
                (bearFvg - npArr[i-1][3]) / 
                (npArr[i-1][3] - bullFvg) 
            )
            if rr <= 2.413793103448276: continue

        value = valuepegDict[symbol][0]
        valuePerShare = value[-1][3]
        if valuePerShare == "-": continue
        if valuePerShare <= 0: continue
        if npArr[i-1][3] / valuePerShare >= 5.80000000e+02: continue

        chart = chartDict[symbol]
        mc = chart[0][7]
        pbr = chart[0][10]
        if symbol in categoryDict:
            category = categoryDict[symbol]
            if category in categoryPbrDict:
                if pbr >= categoryPbrDict[category]:
                    continue

        plbscfdividend = plbsDict[symbol]
        pl = plbscfdividend[0]
        bs = plbscfdividend[1]
        idx = len(bs) - 2

        plLength = len(pl[0])
        epsIdx = 6
        if plLength == 7: epsIdx = 4
        elif plLength == 8: epsIdx = 5
        elif plLength == 9: epsIdx = 5
        elif plLength == 10: epsIdx = 6
        elif plLength == 11: epsIdx = 5
        eps = pl[idx][epsIdx]
    
        bsLength = len(bs[0])
        if bsLength in [6, 7, 8, 9]:
            jikoushihonhiritsu = bs[idx][4]
            bpsIdx = 8
            if bsLength == 8: bpsIdx = 7
            elif bsLength == 7: bpsIdx = 6
            elif bsLength == 6: bpsIdx = 5

            bps = bs[idx][bpsIdx]
            if bps == "-": continue
            rironkabuka = GetRironkabuka(bps,
            jikoushihonhiritsu, 
            eps, npArr[i-1][3])[0]
            if npArr[i-1][3] / rironkabuka >= 32.783018867924525:
                continue
        
        bsLength = len(bs[0])
        if bsLength in [6, 7, 8, 9]:
            bpsIdx = 8
            if bsLength == 8:
                bpsIdx = 7
            elif bsLength == 7:
                bpsIdx = 6
            elif bsLength == 6:
                bpsIdx = 5

        bps = bs[idx][bpsIdx]
        if bps == "-": continue
        
        yuurishifusaiIdx = 6
        if bsLength == 8:
            yuurishifusaiIdx = 5
        yuurishifusai = bs[idx][yuurishifusaiIdx]
        if yuurishifusai == "-": yuurishifusai = 0

        yuurishifusaiIdx = 6
        if bsLength == 8:
            yuurishifusaiIdx = 5
        yuurishifusai = bs[idx][yuurishifusaiIdx]
        if yuurishifusai == "-": yuurishifusai = 0

        if yuurishifusai > 0:
            terminalValue = yuurishifusai / (yuurishifusai + mc)
            if terminalValue <= 1.2748049414824448e-21: continue

        cf = plbscfdividend[2]
        idx = len(cf) - 1
        freecf = cf[idx][4]
        if freecf == 0: continue

        dividend = plbscfdividend[3]
        idx = len(dividend) - 2
        dividendLength = len(dividend[0])
        if dividendLength in [6, 8, 9, 10]:
            soukanngenngakuIdx = 6
            soukanngennseikouIdx = 7
            if dividendLength == 6:
                soukanngenngakuIdx = 2
                soukanngennseikouIdx = 3
            elif dividendLength == 9:
                soukanngenngakuIdx = 5
                soukanngennseikouIdx = 6

            soukanngenngaku = dividend[idx][soukanngenngakuIdx]
            if soukanngenngaku != "-":
                if soukanngenngaku < 1: continue
                
        if dividendLength in [6, 8, 10]:
            soukanngenngakuIdx = 6
            soukanngennseikouIdx = 7
            if dividendLength == 6:
                soukanngenngakuIdx = 2
                soukanngennseikouIdx = 3

            soukanngennseikou = dividend[idx][soukanngennseikouIdx]
            if soukanngennseikou == "赤字": 
                if categoryDict[symbol] in ['輸送用機器']:
                    continue

        # short = shortDict[symbol]
        # yesterdayStr = sampleArr[i-1][5]
        # yesterday = datetime.strptime(yesterdayStr, "%Y-%m-%d")
        # lastDt = datetime.strptime(short[-1][0], "%Y-%m-%d")
        # days = (yesterday - lastDt).days
        # if days >= 287: continue

        if symbol in employeeDict:
            employee = employeeDict[symbol]
            if employee[-1][1] * employee[-1][2] >= 35923680000: continue

        f1score = calculate_f1_score(npArr)
        if f1score == -1: continue

        # xtvazForward = GetForward(symbol, None, dataDict)[-1]
        # if xtvazForward[9] <= 0.076467: continue
        zandaka = zandakaDict[symbol]
        if len(zandaka) > 1:
            kaizanC = zandaka[0][2]
            kaizanC1 = zandaka[1][2]
            if (
                kaizanC1 < 0 and
                kaizanC < 0
            ): continue
        urikashizan = zandaka[0][7]
        signalDict[symbol] = urikashizan / (mc / npArr[i-1][3])
    signalDict = dict(sorted(signalDict.items(), key=lambda item: item[1], reverse=True))
    return list(signalDict.keys())

group = ""
length = len(dataDictJP["7203"])
dataDict = dataDictJP

cleanDataDict = {}
for symbol, npArr in dataDict.items():
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr
dataDict = cleanDataDict
cleanDataDict = {}

gainnerList = []
for i in range(1, length):
    perfDict = {}
    for symbol, npArr in dataDict.items():
        perfDict[symbol] = npArr[i-1][3] / npArr[i-1][0]
    perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1], reverse=True))
    gainner = take(6, perfDict)
    for g in gainner:
        gainnerList.append(g)

# sampleArr = GetDataWithVolumeDate("^N225")
# sampleArr = sampleArr[-length:]

cleanDataDict = {}
shijousizeList = ['ＰＲＭ大型', 'ＧＲＴ中型', 'ＳＴＤ中型', 'ＰＲＭ中型', 'ＳＴＤ小型', 'ＧＲＴ小型']

for symbol, npArr in dataDict.items():
    if symbol not in shortDict: continue
    if symbol not in zandakaDict: continue
    if symbol not in chartDict: continue
    if symbol not in gainnerList: continue
    # if symbol not in nisshokinDict: continue
    # if symbol not in shijousizeDict: continue
    # shijousize = shijousizeDict[symbol]
    # if shijousize not in shijousizeList: continue
    # if symbol not in plbsDict: continue
    # plbs = plbsDict[symbol]
    # if len(plbs[0]) < 3: continue
    # plIdx = -1
    # plLast = plbs[0][-1][0]
    # if "予" in plLast:
    #     plIdx = -2
    # pl = plbs[0][plIdx]
    # pl2 = plbs[0][plIdx-1]
    
    # plLength = len(pl)
    # if plLength not in [12]: continue
    # junnriekiIdx = 4
    # epsIdx = 6
    # roeIdx = 7
    # roaIdx = 8
    # if plLength == 7:
    #     junnriekiIdx = 2
    #     epsIdx = 4
    #     roeIdx = 5
    #     roaIdx = 6
    # elif plLength == 8:
    #     junnriekiIdx = 3
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7
    # elif plLength == 9:
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7
    # elif plLength == 11:
    #     epsIdx = 5
    #     roeIdx = 6
    #     roaIdx = 7

    # # junnrieki = pl[junnriekiIdx]
    # # if junnrieki < 1: continue

    # roa = pl[roaIdx]
    # if roa == "-": continue
    # # if roa == "赤字": continue
    # # if roa < 2.2: continue

    # # if plLength in [7, 10, 11, 12]:
    # #     uriageIdx = 1
        
    # #     uriage = pl[uriageIdx]
    # #     if uriage < 123000000: continue

    # if plLength in [9, 10, 11, 12]:
    #     eigyouriekiIdx = 2
    #     eigyouriekiritsuIdx = 9
    #     if plLength == 9:
    #         eigyouriekiritsuIdx = 8
    #     elif plLength == 10:
    #         eigyouriekiritsuIdx = 8
    #     elif plLength == 11:
    #         eigyouriekiritsuIdx = 8

    #     eigyourieki = pl[eigyouriekiIdx]
    #     if eigyourieki == "-": continue
    #     if "*" in str(eigyourieki):
    #         eigyourieki = int(eigyourieki[1:-1]) * 100000000

    #     eigyourieki2 = 0
    #     if len(plbs[0]) < 3: continue
    #     pl2 = plbs[0][-3]
    #     eigyourieki2 = pl2[eigyouriekiIdx]
    #     if eigyourieki2 == "-": continue
    #     if "*" in str(eigyourieki): continue
    
    # # if plLength in [8, 9, 10, 11, 12]:
    # #     keijyouriekiIdx = 3
    # #     if plLength == 8:
    # #         keijyouriekiIdx = 2

    # #     keijyourieki = pl[keijyouriekiIdx]
    # #     if keijyourieki == "-": continue

    # # if plLength in [7, 8, 10, 12]:
    # #     houkatsuriekiIdx = 5
    # #     if plLength == 7:
    # #         houkatsuriekiIdx = 3
    # #     elif plLength == 8:
    # #         houkatsurieki = 4

    # #     houkatsurieki = pl[houkatsuriekiIdx]
    # #     if houkatsurieki == "-": continue

    # # if plLength in [11, 12]:
    # #     gennkaritsuIdx = 10
    # #     hannkannhiritsuIdx = 11
    # #     if plLength == 11:
    # #         gennkaritsuIdx = 9
    # #         hannkannhiritsuIdx = 10

    # #     gennkaritsu = pl[gennkaritsuIdx]
    # #     if gennkaritsu == "-": continue

    # #     hannkannhiritsu = pl[hannkannhiritsuIdx]
    # #     if hannkannhiritsu == "-": continue

    # if len(plbs[1]) < 1: continue
    # bs = plbs[1][-1]
    # bsLength = len(bs)
    
    # # junnshisan = bs[2]

    # # if bsLength in [6, 7, 8, 9]:
    # #     soushisannIdx = 1
    # #     kabunushishihonnIdx = 3
    # #     jikoushihonritsuIdx = 4
    # #     bpsIdx = 8
    # #     if bsLength == 8:
    # #         bpsIdx = 7
    # #     elif bsLength == 7:
    # #         bpsIdx = 6
    # #     elif bsLength == 6:
    # #         bpsIdx = 5

    # #     soushisann = bs[soushisannIdx]

    # #     kabunushishihonn = bs[kabunushishihonnIdx]
    # #     if kabunushishihonn == "-": continue
    
    # #     jikoushihonritsu = bs[jikoushihonritsuIdx]

    # #     bps = bs[bpsIdx]

    # if bsLength in [7, 9]:
    #     riekijouyokinIdx = 5

    #     riekijouyokin = bs[riekijouyokinIdx]
    #     if riekijouyokin == "-": continue

    # # if bsLength in [4, 8, 9]:
    # #     yuurishifusaiIdx = 6

    # #     if bsLength == 8:
    # #         yuurishifusaiIdx = 5
    # #     elif bsLength == 4:
    # #         yuurishifusaihiritsuIdx = 3

    # #     yuurishifusai = bs[yuurishifusaiIdx]
    # #     if yuurishifusai == "-": continue
    # #     if yuurishifusai < 58400000: continue

    # # if bsLength in [8, 9]:
    # #     yuurishifusaihiritsuIdx = 7
    # #     if bsLength == 8:
    # #         yuurishifusaihiritsuIdx = 6

    # #     yuurishifusaihiritsu = bs[yuurishifusaihiritsuIdx]

    # # junnshisan = int(bs[2])
    # # junnshisan2 = int(bs2[2])
    # # if junnshisan/junnshisan2 < 0.1: continue
    
    # if len(plbs[2]) < 1: continue
    # cf = plbs[2][-1]
    # cfLength = len(cf)

    # gennkinIdx = 6
    # eigyoucfmarginIdx = 7
    # if cfLength == 7:
    #     gennkinIdx = 5
    #     eigyoucfmarginIdx = 6

    # toushicf = cf[2]
    # if toushicf == "-": continue

    # # gennkin = cf[gennkinIdx]
    # # if gennkin < 47800000: continue

    # eigyoucfmargin = cf[eigyoucfmarginIdx]
    # if eigyoucfmargin == "-": continue

    # if cfLength == 8:
    #     setsubitoushi = cf[5]
    #     if setsubitoushi == "-": continue
    
    # if len(plbs[3]) < 1: continue
    # dividend = plbs[3][-1]
    # dividendLength = len(dividend)

    # if dividendLength in [4, 5, 7, 8, 9, 10]:
    #     haitouseikouIdx = 2
    #     haitouseikou = dividend[haitouseikouIdx]
    #     if haitouseikou != "-":
    #         if haitouseikou == "赤字": continue
    # #         # if haitouseikou < 8.7: continue

    # # # if dividendLength in [5, 7, 9, 10]:
    # # #     jouyokinnhaitouIdx = 3
    # # #     jouyokinnhaitou = dividend[jouyokinnhaitouIdx]

    # if dividendLength in [4, 5, 10]:
    #     junnshisannhaitouritsuIdx = 4
    #     if dividendLength == 4:
    #         junnshisannhaitouritsuIdx = 3
    #     junnshisannhaitouritsu = dividend[junnshisannhaitouritsuIdx]
    #     if junnshisannhaitouritsu == "赤字": continue

    # if dividendLength in [6, 8, 9, 10]:
    #     jishakabukaiIdx = 5
    #     soukanngenngakuIdx = 6
    #     soukanngennseikouIdx = 7
    #     if dividendLength == 6:
    #         jishakabukaiIdx = 1
    #         soukanngenngakuIdx = 2
    #         soukanngennseikouIdx = 3
    #     elif dividendLength == 9:
    #         jishakabukaiIdx = 4
    #         soukanngenngakuIdx = 5
    #         soukanngennseikouIdx = 6

    #     jishakabukai = dividend[jishakabukaiIdx]
    #     if jishakabukai == "赤字": continue

    #     # soukanngenngaku = dividend[soukanngenngakuIdx]

    # #     soukanngennseikou = dividend[soukanngennseikouIdx]

    #     if len(plbs[3]) > 1:
    #         dividend2 = plbs[3][-2]
    #         jishakabukai2 = dividend2[jishakabukaiIdx]
    #         if jishakabukai2 == "赤字": continue

    # if dividendLength in [3, 6, 7, 9, 10]:
    #     kabunushisourimawariIdx = 8
    #     shihyourimawariIdx = 9
    #     if dividendLength == 3:
    #         kabunushisourimawariIdx = 1
    #         shihyourimawariIdx = 2
    #     elif dividendLength == 6:
    #         kabunushisourimawariIdx = 4
    #         shihyourimawariIdx = 5
    #     elif dividendLength == 7:
    #         kabunushisourimawariIdx = 5
    #         shihyourimawariIdx = 6
    #     elif dividendLength == 9:
    #         kabunushisourimawariIdx = 7
    #         shihyourimawariIdx = 8

    # #     kabunushisourimawari = dividend[kabunushisourimawariIdx]
    # #     if kabunushisourimawari == "-": continue
    
    #     shihyourimawari = dividend[shihyourimawariIdx]
    # #     if shihyourimawari == "-": continue
    #     if shihyourimawari == "赤字": continue
        
    if symbol in ryuudoumeyasuDict:
        if ryuudoumeyasuDict[symbol][0] < 200: continue

    # if symbol in growthDict:
    #     growth = growthDict[symbol][0]
    #     if len(growth) < 4: continue
    #     uriageseichouritsu5y = growth[0][1]
    #     if uriageseichouritsu5y < 0.0058: continue

    if symbol in officerHoldDict:
        hold = officerHoldDict[symbol]
        if hold[0] <= 0.007: continue
        if hold[5] >= 0.735: continue
    #     if hold[3] + hold[4] <= 0.0: continue
    
    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    cleanDataDict[symbol] = npArr

print(len(cleanDataDict))
symbolList = Backtest(cleanDataDict, length, 
    shortDict, zandakaDict, chartDict, 
    plbsDict, categoryDict, employeeDict)
print(symbolList)

res = []
for symbol in symbolList:
    res.append([symbol,cleanDataDict[symbol][-1][3]])
csvPath = f"{rootPath}/data/ScannerJP.csv"
header = ["Symbol","Close"]
dump_result_list_to_csv(res,csvPath,header)