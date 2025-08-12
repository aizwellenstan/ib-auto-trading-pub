import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from modules.rironkabukaFormula import GetRironkabuka
import math
from modules.dict import take
from modules.rci import rciArr
from modules.ichimoku import get_ichimoku
from modules.rsi import get_rsi
from modules.f1score import calculate_f1_score
from modules.obv import GetOBV
from modules.macd import MacdHistorical
from modules.adx import GetADX
from modules.smc import GetFvg
from modules.resample import Resample
from modules.rsi import get_rsi
from modules.bollingerBands import GetBollingerBands
from modules.db_utils import GetFinancial
from modules.corr import GetCorr, GetCorrVolume1, GetCorrCl1, GetCorrCompareVol1, GetCorrCompareC1
from modules.dataHandler.nisshokin import GetNisshokin
from modules.dataHandler.category import GetCategoryDict
from modules.dataHandler.lending import GetLending
from modules.dataHandler.zandaka import GetZandaka
from modules.dataHandler.chart import GetChart

def least_squares(x, y):
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    xy_mean = np.mean(x * y)
    x_sq_mean = np.mean(x**2)

    slope = (xy_mean - x_mean * y_mean) / (x_sq_mean - x_mean**2)
    intercept = y_mean - slope * x_mean

    return slope, intercept

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
plbsPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
plbsDict = LoadPickle(plbsPath)

dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"
dataDictJP = LoadPickle(dataPathJP)

valuepegPath = f"{rootPath}/backtest/pickle/pro/compressed/valuepeg.p"
valuepegDict = LoadPickle(valuepegPath)

marginPath = f"{rootPath}/backtest/pickle/pro/compressed/margin.p"
marginDict = LoadPickle(marginPath)



ryuudoumeyasuPath = f"{rootPath}/backtest/pickle/pro/compressed/ryuudoumeyasu.p"
ryuudoumeyasuDict = LoadPickle(ryuudoumeyasuPath)

zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
zandakaDict = LoadPickle(zandakaPath)

officerHoldPath = f"{rootPath}/backtest/pickle/pro/compressed/officerHold.p"
officerHoldDict = LoadPickle(officerHoldPath)

shortPath = f"{rootPath}/backtest/pickle/pro/compressed/short.p"
shortDict = LoadPickle(shortPath)

shortPath = f"{rootPath}/backtest/pickle/pro/compressed/shortBase.p"
shortBaseDict = LoadPickle(shortPath)

chartPath = f"{rootPath}/backtest/pickle/pro/compressed/chartHistory2.p"
chartDict = LoadPickle(chartPath)

safetyPath = f"{rootPath}/backtest/pickle/pro/compressed/safety.p"
safetyDict = LoadPickle(safetyPath)

sectorPricePathJP = f"{rootPath}/backtest/pickle/pro/compressed/sectorPriceJP.p"
sectorPriceDict = LoadPickle(sectorPricePathJP)

def floor500(number):
    return math.floor(number/500) * 500

# def calculate_beta(array_a, array_b):
#     # Calculate covariance matrix
#     cov_matrix = np.cov(array_a.astype(float), array_b.astype(float))

#     # Covariance between array_a and array_b
#     cov_ab = cov_matrix[0, 1]

#     # Variance of array_b
#     var_b = cov_matrix[1, 1]

#     # Calculate beta
#     beta = cov_ab / var_b

#     return beta

def Backtest(dataDict, length, valuepegDict, 
    categoryDict,
    shortDict, chartDict, plbsDict, 
    totalGainnerList, 
    sectorPriceDict):
    rtnList = np.empty(0)
    hisSigList = np.empty(0)
    gomiDict = {}
    sma5Dict = {}
    sma25Dict = {}
    sma75Dict = {}
    bollingerBandsDict = {}
    bollingerBands3Dict = {}
    rciDict = {}
    rciVolDict = {}
    obvDict = {}
    macdVolDict = {}
    macdDict = {}
    adxDict = {}
    fvgDict = {}
    rsiDict = {}
    rsi7Dict = {}
    rsi6Dict = {}
    lastRsiHighDict = {}
    rsiHighDict = {}
    lastCloseDict = {}
    closeDict = {}
    attrList = np.empty(0)
    ddList = []
    mddList = []

    categoryPerDict = {'機械': 46.44}
    categoryPbrDict = {'電気機器': 3.41}
    
    # defenceSymbol = "9501"
    # defenceSymbol = "1357"
    # defenceSymbol = "8139"
    # defenceNpArr = GetDataWithVolumeDate(defenceSymbol, "2018-01-01")
    # defenceNpArr = defenceNpArr[-len(sampleArr):]

    # upDownRatioNpArr = GetUpDownRatio()
    # upDownRatioNpArr = GetUpDownRatio()[:-1]
    # upDownRatioNpArr = upDownRatioNpArr[-len(sampleArr):]
    
    for i in range(5, length):
        isShort = False
        topPerf = 0
        topSymbol = ""
        perfDict = {}
        today = sampleArr[i][5]
        print(today,i)

        # upDownRatio = upDownRatioNpArr[i-1][1]
        # if upDownRatio <= 74.9: isShort = False
        # if upDownRatio >= 137.2: continue

        today = datetime.strptime(today, "%Y-%m-%d")

        yesterdayStr = sampleArr[i-1][5]
        yesterday = datetime.strptime(yesterdayStr, "%Y-%m-%d")
        
        for symbol, npArr in dataDict.items():
            if npArr[i-1][3] > npArr[i-1][1]: continue
            if npArr[i-2][4] < 1: continue
            if (
                npArr[i-1][4] > npArr[i-6][4] and
                npArr[i-1][4] > npArr[i-5][4] and
                npArr[i-1][3] > npArr[i-1][0]
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
            if (
                npArr[i-3][4] > npArr[i-4][4] and
                npArr[i-2][4] > npArr[i-3][4] and
                npArr[i-1][4] > npArr[i-2][4] * 3 and
                npArr[i-3][1] > npArr[i-4][1] and
                npArr[i-2][1] > npArr[i-3][1] and
                npArr[i-1][1] > npArr[i-2][1]
            ): continue
            
            if npArr[i-1][2] * npArr[i-1][4] < 4778345366: continue
            if npArr[i-1][3] < npArr[i-2][2]: continue
            if (
                npArr[i-1][3] / npArr[i-4][0] <= 0.917262969588551 and
                npArr[i-1][3] / npArr[i-1][0] <= 0.9624589394650399
            ): continue
            if symbol in categoryDict:
                if categoryDict[symbol] in ['情報・通信業']:
                    if npArr[i-1][4] / npArr[i-2][4] > 5: continue

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

            # if symbol not in rsiDict:
            #     rsi = get_rsi(npArr[:,3], 10)
            #     rsiDict[symbol] = rsi
            # else:
            #     rsi = rsiDict[symbol]
            # if (
            #     rsi[i-4] > rsi[i-5] and
            #     rsi[i-3] > rsi[i-4] and
            #     rsi[i-1] < rsi[i-2]
            # ): continue

            # if symbol not in rsi7Dict:
            #     rsi = get_rsi(npArr[:,3], 7)
            #     rsi7Dict[symbol] = rsi
            # else:
            #     rsi = rsi7Dict[symbol]
            # if (
            #     rsi[i-4] > rsi[i-5] and
            #     rsi[i-3] > rsi[i-4] and
            #     # rsi[i-2] < rsi[i-3] and
            #     rsi[i-1] < rsi[i-2]
            # ): continue

            # if symbol not in obvDict:
            #     obv = GetOBV(npArr)
            #     obvDict[symbol] = obv
            # else:
            #     obv = obvDict[symbol]
            # if obv[i-1] <= -95188251: continue

            if symbol not in sma5Dict:
                closeArr = npArr[:,3]
                sma5 = SmaArr(closeArr, 5)
                sma5Dict[symbol] = sma5
            else:
                sma5 = sma5Dict[symbol]
            if npArr[i-1][3] < sma5[i-1]: continue

            if symbol not in sma25Dict:
                closeArr = npArr[:,3]
                sma25 = SmaArr(closeArr, 25)
                sma25Dict[symbol] = sma25
            else:
                sma25 = sma25Dict[symbol]
            bias = (
                (npArr[i-1][3] - sma25[i-1]) / 
                sma25[i-1]
            )
            if bias < -0.2: continue
            if bias >= 0.7702747072343219: continue

            if symbol in categoryDict:
                if categoryDict[symbol] in ['海運業', '電気機器', 'その他製品', '不動産業']:
                    if symbol not in sma75Dict:
                        closeArr = npArr[:,3]
                        sma75 = SmaArr(closeArr, 75)
                        sma75Dict[symbol] = sma75
                    else:
                        sma75 = sma75Dict[symbol]
                    if npArr[i-1][3] < sma75[i-1]:
                        continue
            
            if symbol not in rciVolDict:
                rci = rciArr(npArr[:,4])
                rciVolDict[symbol] = rci
            else:
                rci = rciVolDict[symbol]
            if rci[i-1] <= -95: continue

            if symbol not in rciDict:
                rci = rciArr(npArr[:,3])
                rciDict[symbol] = rci
            else:
                rci = rciDict[symbol]
            if (
                (rci[i-1] - rci[i-2]) / 
                rci[i-2]
            ) <= -14.000000000000046: continue

            if symbol not in macdVolDict:
                macdHist = MacdHistorical(npArr[:,4])
                macdVolDict[symbol] = macdHist
            else:
                macdHist = macdVolDict[symbol]
            if macdHist[i-1] <= -2083575.4696298428: continue

            bullFvg = 0
            bearFvg = 0
            bear = False
            if symbol not in fvgDict:
                fvg = GetFvg(npArr)
                fvgDict[symbol] = fvg
            else:
                fvg = fvgDict[symbol]
            for j in fvg[:i]:
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
                        if j[1] - j[2] < 90: continue
                        if j[3] > i-1 or math.isnan(j[3]):
                            if bearFvg == 0:
                                bearFvg = j[2]
                            elif j[2] < bearFvg:
                                bearFvg = j[2]
                        else:
                            bear = True
                            break
            if bear: continue
            rr = 0
            if bullFvg > 0 and bearFvg > 0:
                rr = (
                    (bearFvg - npArr[i-1][3]) / 
                    (npArr[i-1][3] - bullFvg) 
                )
                if rr <= 2.413793103448276: continue
            
            # npArr2d = Resample(npArr[:i])
            # bear = False
            # fvg = GetFvg(npArr2d)
            # for j in fvg:
            #     if not math.isnan(j[3]):
            #         if j[0] < 0:
            #             if j[2] < npArr[i-1][3]:
            #                 bear = True
            #                 break
            # if bear: continue
            # if bullFvg > 0 and bearFvg > 0:
            #     rr = (
            #         (bearFvg - npArr[i-1][3]) / 
            #         (npArr[i-1][3] - bullFvg) 
            #     )
                # if rr <= 0.09840810419681621: continue

            if symbol not in totalGainnerList[i-1]: continue

            value = valuepegDict[symbol][0]
            idx = 0
            for j in range(0, len(value)):
                dt = datetime.strptime(value[j][0], "%Y/%m")
                if dt <= yesterday: 
                    idx = j
                else: break
            valuePerShare = value[idx][3]
            if valuePerShare == "-": continue
            if symbol in categoryDict:
                if categoryDict[symbol] in ['機械']:
                    if valuePerShare <= 0: continue
            if valuePerShare <= 0: continue
            if npArr[i-1][3] / valuePerShare >= 5.80000000e+02: continue

            # short = shortDict[symbol]
            # idx = 0
            # lastDt = yesterday
            # shortPer = 0
            # for j in range(0, len(short)):
            #     dt = datetime.strptime(short[j][0], "%Y-%m-%d")
            #     if dt > yesterday: break
            #     lastDt = dt
            #     shortPer = short[j][2]
            #     idx = j
            # if idx > 0:
            #     days = (yesterday - lastDt).days
            #     if days >= 287: continue
            
            if symbol in plbsDict:
                plbscfdividend = plbsDict[symbol]
                bs = plbscfdividend[1]
                idx = 0
                for j in range(0, len(bs)):
                    dt = datetime.strptime(bs[j][0], "%Y/%m")
                    if dt <= yesterday:
                        idx = j
                pl = plbscfdividend[0]

                plLength = len(pl[0])
                epsIdx = 6
                if plLength == 7: epsIdx = 4
                elif plLength == 8: epsIdx = 5
                elif plLength == 9: epsIdx = 5
                elif plLength == 10: epsIdx = 6
                elif plLength == 11: epsIdx = 5
                eps = pl[idx][epsIdx]

                roeIdx = 7
                if plLength == 7: roeIdx = 5
                elif plLength == 8: roeIdx = 6
                elif plLength == 9: roeIdx = 6
                elif plLength == 11: roeIdx = 6
                roe = pl[idx][roeIdx]
                if roe == "-": continue
                if roe == "赤字": continue
                if roe <= 15.56: continue
            
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

                    if bsLength in [8, 9]:
                        yuurishifusaihiritsuIdx = 7
                        if bsLength == 8:
                            yuurishifusaihiritsuIdx = 6

                        yuurishifusaihiritsu = bs[idx][yuurishifusaihiritsuIdx]
                        if yuurishifusaihiritsu == "-": continue
                        if idx > 0:
                            yuurishifusaihiritsu2 = bs[idx-1][yuurishifusaihiritsuIdx]
                            if yuurishifusaihiritsu2 == "-": continue
                    
                uriage = pl[idx][1]
                if uriage == "-": continue
                eigyourieki = pl[idx][2]
                if eigyourieki == "-": continue
                if "*" in str(eigyourieki):
                    eigyourieki = int(eigyourieki[1:-1]) * 100000000
                junnrieki = pl[idx][4]
                plLength = len(pl[0])
                if plLength in [9, 10, 11, 12]:
                    eigyouriekiritsuIdx = 9
                    if plLength == 9:
                        eigyouriekiritsuIdx = 8
                    elif plLength == 10:
                        eigyouriekiritsuIdx = 8
                    elif plLength == 11:
                        eigyouriekiritsuIdx = 8
                    eigyouriekiritsu = pl[idx][eigyouriekiritsuIdx]
                    eigyouriekiritsu2 = pl[idx-1][eigyouriekiritsuIdx]
                
                    if eigyouriekiritsu == "-": continue
                    if eigyouriekiritsu2 == "-": continue
                roaIdx = 8
                if plLength == 7: roaIdx = 6
                elif plLength == 8: roaIdx = 7
                elif plLength == 9: roaIdx = 7
                elif plLength == 11: roaIdx = 7
                roa = pl[idx][roaIdx]
                if idx > 0:
                    roa2 = pl[idx-1][roaIdx]

                dividend = plbscfdividend[3]
                idx = 0
                for j in range(0, len(dividend)):
                    if "予" in dividend[j][0]: break
                    dt = datetime.strptime(dividend[j][0], "%Y/%m")
                    if dt <= yesterday: idx = j
                if len(dividend) > 0:
                    dividendLength = len(dividend[0])
                    ichikabuhaitou = dividend[idx][1]
                    haitourimawari = 0
                    if ichikabuhaitou != "-":
                        if "*" in str(ichikabuhaitou): continue
                        haitourimawari = ichikabuhaitou / npArr[i-1][3]

            fscore = 0
            if symbol in plbsDict:
                plbscfdividend = plbsDict[symbol]
                bs = plbscfdividend[1]
                idx = 0
                for j in range(0, len(bs)):
                    dt = datetime.strptime(bs[j][0], "%Y/%m")
                    if dt <= yesterday:
                        idx = j
                if idx > 0:
                    pl = plbscfdividend[0]
                    plLength = len(pl[0])
                    if plLength in [9, 10, 11, 12]:
                        eigyourieki = pl[idx][2]
                        if "*" in str(eigyourieki):
                            eigyourieki = int(eigyourieki[1:-1]) * 100000000
                        eigyourieki2 = pl[idx-1][2]
                        if "*" in str(eigyourieki2):
                            eigyourieki2 = int(eigyourieki2[1:-1]) * 100000000
                        if eigyourieki > eigyourieki2:
                            fscore += 1
                    if plLength in [9, 10, 11, 12]:
                        eigyouriekiritsuIdx = 9
                        if plLength == 9:
                            eigyouriekiritsuIdx = 8
                        elif plLength == 10:
                            eigyouriekiritsuIdx = 9
                        elif plLength == 11:
                            eigyouriekiritsuIdx = 8
                        eigyouriekiritsu = pl[idx][eigyouriekiritsuIdx]
                        eigyouriekiritsu2 = pl[idx-1][eigyouriekiritsuIdx]
                        if eigyouriekiritsu == "赤字": continue
                        if eigyouriekiritsu2 == "赤字":
                            fscore += 1
                        elif eigyouriekiritsu > eigyouriekiritsu2:
                            fscore += 1
                    roaIdx = 8
                    if plLength == 7:
                        junnriekiIdx = 2
                        epsIdx = 4
                        roeIdx = 5
                        roaIdx = 6
                    elif plLength == 8:
                        junnriekiIdx = 3
                        epsIdx = 5
                        roeIdx = 6
                        roaIdx = 7
                    elif plLength == 9:
                        epsIdx = 5
                        roeIdx = 6
                        roaIdx = 7
                    elif plLength == 11:
                        epsIdx = 5
                        roeIdx = 6
                        roaIdx = 7
                    roa = pl[idx][roaIdx]
                    if roa == "赤字": continue
                    roa2 = pl[idx-1][roaIdx]
                    if (
                        roa2 != "-" and
                        roa != "-" 
                    ):
                        if roa2 == "赤字":
                            fscore += 1
                        elif roa > roa2:
                            fscore += 1

                    bsLength = len(bs[0])
                    if bsLength in [8, 9]:
                        yuurishifusaihiritsuIdx = 7
                        if bsLength == 8:
                            yuurishifusaihiritsuIdx = 6
                        yuurishifusaihiritsu = bs[idx][yuurishifusaihiritsuIdx]
                        yuurishifusaihiritsu2 = bs[idx-1][yuurishifusaihiritsuIdx]
                        if yuurishifusaihiritsu < yuurishifusaihiritsu2:
                            fscore += 1

                    if bsLength in [6, 7, 8, 9]:
                        uriage = pl[idx][1]
                        uriage2 = pl[idx-1][1]
                        soushisann = bs[idx][1]
                        soushisann2 = bs[idx-1][1]

                        if (
                            uriage / soushisann >
                            uriage2 / soushisann2
                        ): fscore += 1

                junnriekiIdx = 4
                if plLength == 7: junnriekiIdx = 2
                elif plLength == 8: junnriekiIdx = 3
                junnrieki = pl[idx][junnriekiIdx]

                cf = plbscfdividend[2]
                cfIdx = 0
                for j in range(0, len(cf)):
                    dt = datetime.strptime(cf[j][0], "%Y/%m")
                    if dt <= yesterday: cfIdx = j
                if cfIdx > 0:
                    eigyoucf = cf[cfIdx][1]
                    if eigyoucf > 0:
                        fscore += 1
                    if junnrieki < eigyoucf:
                        fscore += 1
            if fscore < 2: continue

            if symbol in safetyDict:
                safety = safetyDict[symbol]
                safetyShort = safety[0]
                idx = 0
                for j in range(0, len(safetyShort)):
                    dt = datetime.strptime(safetyShort[j][0], "%Y/%m")
                    if dt <= yesterday: idx = j
                gesshoubairitsu = safetyShort[idx][5]
                if gesshoubairitsu != "-":
                    if gesshoubairitsu >= 75.5: continue
            
            if symbol not in zandakaDict: continue
            zandaka = zandakaDict[symbol]
            kaizanC = 0
            urikashizan = 0
            currIdx = 0
            for idx, n in enumerate(zandaka):
                dt = datetime.strptime(n[0], "%Y-%m-%d")
                kaizanC = n[2]
                urizanC = n[4]
                urikashizan = n[7]
                currIdx = idx
                if dt <= yesterday: break
            if currIdx + 1 < len(zandaka):
                if (
                    zandaka[currIdx+1][2] < 0 and
                    kaizanC < 0
                ): continue
                if (
                    kaizanC < 0 and
                    zandaka[currIdx+1][2] > 0 and
                    -kaizanC > zandaka[currIdx+1][2] * 20
                ): continue

            urizan = GetNisshokin(symbol, 'urizan', npArr[i-2][5])
            if urizan > 0:
                kaizan_h = GetNisshokin(symbol, 'kaizan_h', npArr[i-2][5])
                if kaizan_h / urizan >= 1.19090909e+01: continue
                
            f1score = calculate_f1_score(npArr[:i])
            if f1score == -1: continue

            corr = GetCorr(npArr[:i])
            if corr <= -0.26406876: continue
            if npArr[i-1][4] < npArr[i-2][4]:
                if corr >= 0.56198252: continue

            corr = GetCorrVolume1(npArr[:i])
            if npArr[i-1][4] < npArr[i-2][4]:
                if corr >= 4.10438126e-01: continue
            
            corr = GetCorrCl1(npArr[:i])
            if npArr[i-1][3] < npArr[i-2][3]:
                if corr >= 0.20047399: continue

            if urizan == 0: continue
            kaizan_s = GetNisshokin(symbol, 'kaizan_s', npArr[i-2][5])
            if kaizan_s == 0: continue
            
            gyakuhibo = GetNisshokin(symbol, 'gyakuhibo', npArr[i-2][5])
            if gyakuhibo > 0: continue
         
            tentai_s = GetLending(symbol, 'tentai_s', npArr[i-1][5])
            mc = GetChart(symbol, 'mc', npArr[i-1][5])
            if mc == 0: continue

            per = GetChart(symbol, 'per', npArr[i-1][5])
            if per >= 12: continue

            perf = tentai_s / (mc / npArr[i-1][3])
            if perf <= 1.06463296e-03: continue

            urizan_c = GetNisshokin(symbol, "urizan_c", npArr[i-2][5])
            
            perf = urizan_c / (mc / npArr[i-1][3])
            
            if perf > topPerf:
                topPerf = perf
                topSymbol = symbol
        if topSymbol == "": continue
        hisSigList = np.append(hisSigList, topPerf)
        npArr = dataDict[topSymbol]
        sl = npArr[i][0] * 0.96
        close = npArr[i][3]
        if npArr[i][2] < sl: close = sl
        rtn = close / npArr[i][0]
        if rtn < 1:
            # if topSymbol in plbsDict:
            #     plbscfdividend = plbsDict[topSymbol]
            #     pl = plbscfdividend[0]
            #     bs = plbscfdividend[1]
            #     for j in range(0, len(bs)):
            #         dt = datetime.strptime(bs[j][0], "%Y/%m")
            #         if dt <= yesterday:
            #             idx = j
            #     roeIdx = 7
            #     if plLength == 7: roeIdx = 5
            #     elif plLength == 8: roeIdx = 6
            #     elif plLength == 9: roeIdx = 6
            #     elif plLength == 11: roeIdx = 6
            #     roe = pl[idx][roeIdx]
            per = GetChart(topSymbol, 'per', npArr[i-1][5])
            attr = per
            if attr not in attrList:
                attrList = np.append(attrList, attr)
        #     #         
        #     #         plLength = len(pl[0])
        #     #         if plLength in [9, 10, 11, 12]:
        #     #             eigyourieki = pl[idx][2]
        #     #             if "*" in str(eigyourieki):
        #     #                 eigyourieki = int(eigyourieki[1:-1]) * 100000000
        #     #             eigyourieki2 = pl[idx-1][2]
        #     #             if "*" in str(eigyourieki2):
        #     #                 eigyourieki2 = int(eigyourieki2[1:-1]) * 100000000
        #     #             if eigyourieki > eigyourieki2:
        #     #                 fscore += 1
        #     #         if plLength in [9, 10, 11, 12]:
        #     #             eigyouriekiritsuIdx = 9
        #     #             if plLength == 9:
        #     #                 eigyouriekiritsuIdx = 8
        #     #             elif plLength == 10:
        #     #                 eigyouriekiritsuIdx = 9
        #     #             elif plLength == 11:
        #     #                 eigyouriekiritsuIdx = 8
        #     #             eigyouriekiritsu = pl[idx][eigyouriekiritsuIdx]
        #     #             eigyouriekiritsu2 = pl[idx-1][eigyouriekiritsuIdx]
        #     #             if eigyouriekiritsu > eigyouriekiritsu2:
        #     #                 fscore += 1
                    
        #     #         roa = pl[idx][roaIdx]
        #     #         roa2 = pl[idx-1][roaIdx]
        #     #         if (
        #     #             roa2 != "-" and
        #     #             roa != "赤字"
        #     #         ):
        #     #             if roa2 == "赤字":
        #     #                 fscore += 1
        #     #             elif roa > roa2:
        #     #                 fscore += 1

        #     #         bsLength = len(bs[0])
        #     #         if bsLength in [8, 9]:
        #     #             yuurishifusaihiritsuIdx = 7
        #     #             if bsLength == 8:
        #     #                 yuurishifusaihiritsuIdx = 6
        #     #             yuurishifusaihiritsu = bs[idx][yuurishifusaihiritsuIdx]
        #     #             yuurishifusaihiritsu2 = bs[idx-1][yuurishifusaihiritsuIdx]
        #     #             if yuurishifusaihiritsu < yuurishifusaihiritsu2:
        #     #                 fscore += 1

        #     #         if bsLength in [6, 7, 8, 9]:
        #     #             uriage = pl[idx][1]
        #     #             uriage2 = pl[idx-1][1]
        #     #             soushisann = bs[idx][1]
        #     #             soushisann2 = bs[idx-1][1]

        #     #             if (
        #     #                 uriage / soushisann >
        #     #                 uriage2 / soushisann2
        #     #             ): fscore += 1

        #     #     junnriekiIdx = 4
        #     #     if plLength == 7: junnriekiIdx = 2
        #     #     elif plLength == 8: junnriekiIdx = 3
        #     #     junnrieki = pl[idx][junnriekiIdx]

        #     #     cf = plbscfdividend[2]
        #     #     cfIdx = 0
        #     #     for j in range(0, len(cf)):
        #     #         dt = datetime.strptime(cf[j][0], "%Y/%m")
        #     #         if dt <= yesterday: cfIdx = j
        #     #     if cfIdx > 0:
        #     #         eigyoucf = cf[cfIdx][1]
        #     #         if eigyoucf > 0:
        #     #             fscore += 1
        #     #         if junnrieki < eigyoucf:
        #     #             fscore += 1

                
                    
        # #     gyakuhibo = GetNisshokin(symbol, 'gyakuhibo', npArr[i-2][5])
        #     # kaizan_c = GetNisshokin(topSymbol, 'kaizan_c', npArr[i-1][5])
        #     # mc = GetChart(topSymbol, 'mc', npArr[i-1][5])
        #     # if mc > 0:
        #     #     floatShares = mc / npArr[i-1][3]
        #     urizan = GetNisshokin(topSymbol, 'urizan', npArr[i-2][5])
        #     if urizan > 0:
        #         kaizan_h = GetNisshokin(topSymbol, 'kaizan_h', npArr[i-2][5])
                
        #         attr = kaizan_h / urizan
        #         attrList = np.append(attrList, attr)
        rtnList = np.append(rtnList, rtn)
        # if rtn < 0.97:
        #     if topSymbol not in gomiDict:
        #         gomiDict[topSymbol] = 1
        #     else:
        #         gomiDict[topSymbol] += 1
        print(topSymbol, rtn, npArr[i][5])
    attrList.sort()
    print(attrList)
    print(np.mean(rtnList))
    # hisSigList.sort()
    # print(hisSigList)
    # gomiDict = dict(sorted(gomiDict.items(), key=lambda item: item[1]))
    # print(gomiDict)
    return

# def GetSimilarCompanyDict(industryDict, dataDict):
#     grouped_dict = {}
#     for key, value in industryDict.items():
#         if key not in dataDict: continue
#         if value not in grouped_dict:
#             grouped_dict[value] = [key]
#         else:
#             grouped_dict[value].append(key)
#     new_dict = {}
#     for industry, symbols in grouped_dict.items():
#         for symbol in symbols:
#             filtered_symbols = [s for s in symbols if s != symbol and len(symbols) >= 2]
#             if len(filtered_symbols) >= 3:
#                 new_dict.setdefault(symbol, []).extend(filtered_symbols)
#     return new_dict

def BacktestWR(npArr):
    win = 0
    loss = 0
    winList = np.empty(0)
    lossList = np.empty(0)
    for i in range(1, len(npArr)):
        if npArr[i-1][4] >= npArr[i-2][4]: continue
        if npArr[i][3] > npArr[i][0]:
            win += 1
            winList = np.append(winList, npArr[i][3]-npArr[i][0])
        else:
            loss += 1
            lossList = np.append(lossList, npArr[i][0]-npArr[i][3])
    wr = win / (win+loss)
    if wr * np.mean(winList) <= (1-wr) * np.mean(lossList):
        wr = 0
    return wr

group = ""
# group = "US"
# if group == "US":
#     industryDict = GetAttr("industry")
#     length = len(dataDictUS["AAPL"])
#     dataDict = dataDictUS
# else:
# industryDict = GetAttrJP("industry")
length = len(dataDictJP["9101"])
dataDict = dataDictJP

sampleArr = dataDictJP["9101"]
sampleArr = sampleArr[-length:]

# newEventDict = {}
# for symbol, items in eventDict.items():
#     enventDateDict = {}
#     for item in items:
#         if len(item) > 2: continue
#         if item[0] in enventDateDict:
#             enventDateDict[item[0]].append([item[1]])
#         else:
#             enventDateDict[item[0]] = [item[1]]
#     newEventDict[symbol] = enventDateDict
# eventDict = newEventDict

# import itertools
# count = 3945
# industryDict = dict(itertools.islice(industryDict.items(), count))

# similarCompanyDict = GetSimilarCompanyDict(industryDict, dataDict)

def get_unique_values(dictionary):
    unique_values = []
    for value in dictionary.values():
        if value not in unique_values:
            unique_values.append(value)
    return unique_values

def GetShare(npArr):
    total = 0
    for i in npArr:
        total += i[2]
    return total

bibi = ['7686', '6526', '3561', '3561', '3561', '3561', '9107', '8136', '3496', '4487', '7014', '4487', '4570', '4487', '6526', '7388', '4570', '3083', '4176', '3697', '7369', '7369', '7369',
'7369', '3561', '6027', '4570', '7369', '8750', '4487', '6526', '4739', '7369', '7687', '4570', '4570', '2222', '4046', '4570', '7214', '7214', '7014', '6526', '4570', '7369', '4570', '3561', '3399',
'5406']

cleanDataDict = {}
for symbol, npArr in dataDict.items():
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    if npArr[0][1] == npArr[1][2]: continue
    cleanDataDict[symbol] = npArr
dataDict = cleanDataDict

cleanDataDict = {}

totalGainnerList = []
gainnerList = []
for i in range(1, length):
    perfDict = {}
    for symbol, npArr in dataDict.items():
        perfDict[symbol] = npArr[i-1][3] / npArr[i-1][0]
    perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1], reverse=True))
    gainner = take(6, perfDict)
    for g in gainner:
        gainnerList.append(g)
    totalGainnerList.append(gainnerList)

categoryDict = GetCategoryDict()
for symbol, npArr in dataDict.items():
    if symbol in categoryDict:
        if categoryDict in ['石油・石炭製品']: continue
    if symbol not in marginDict: continue
    if symbol not in plbsDict: continue
    if symbol not in chartDict: continue
    if symbol not in shortDict: continue
    if symbol not in zandakaDict: continue
    if symbol not in valuepegDict: continue
    if symbol not in safetyDict: continue
    
    # plbs = plbsDict[symbol]
    # if len(plbs[0]) < 4: continue
    # plIdx = -1
    # plLast = plbs[0][-1][0]
    # if "予" in plLast: plIdx = -2
    # pl = plbs[0][plIdx]
    # pl2 = plbs[0][plIdx-1]
    
    # plLength = len(pl)
    # junnriekiIdx = 4
    # epsIdx = 6
    # roeIdx = 7
    # roaIdx = 8
    
    # roa = pl[roaIdx]
    # if roa == "-": continue

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
    #     if "*" in str(eigyourieki): continue

    #     eigyouriekiritsu = pl[eigyouriekiritsuIdx]
    #     if eigyouriekiritsu == "-": continue
    #     if eigyouriekiritsu == "赤字": continue

    #     eigyourieki2 = 0
    #     if len(plbs[0]) < 3: continue
    #     eigyourieki2 = pl2[eigyouriekiIdx]
    #     if eigyourieki2 == "-": continue
    #     if "*" in str(eigyourieki): continue
        
    # if len(plbs[1]) < 1: continue
    # bs = plbs[1][-1]
    # bsLength = len(bs)

    # junnshisanIdx = 2

    # if bsLength in [6, 7, 8, 9]:
    #     soushisannIdx = 1
    #     kabunushishihonnIdx = 3
    #     jikoushihonritsuIdx = 4
    #     bpsIdx = 8
    #     if bsLength == 8:
    #         bpsIdx = 7
    #     elif bsLength == 7:
    #         bpsIdx = 6
    #     elif bsLength == 6:
    #         bpsIdx = 5

    # if bsLength in [7, 9]:
    #     riekijouyokinIdx = 5

    #     riekijouyokin = bs[riekijouyokinIdx]
    #     if riekijouyokin == "-": continue

    # if len(plbs[2]) < 1: continue
    # cf = plbs[2][-1]
    # cfLength = len(cf)
    # if cfLength == 7: continue
    # gennkinIdx = 6
    # eigyoucfmarginIdx = 7
    # if cfLength == 7:
    #     gennkinIdx = 5
    #     eigyoucfmarginIdx = 6

    # toushicf = cf[2]
    # if toushicf == "-": continue

    # eigyoucfmargin = cf[eigyoucfmarginIdx]
    # if eigyoucfmargin == "-": continue

    # if cfLength == 8:
    #     setsubitoushi = cf[5]
    #     if setsubitoushi == "-": continue
    
    # if len(plbs[3]) < 1: continue
    # dividend = plbs[3][-1]
    # dividendLength = len(dividend)
    # if dividendLength in [3, 6]: continue
    # if dividendLength in [4, 5, 7, 8, 10]:
    #     haitouseikouIdx = 2
    #     haitouseikou = dividend[haitouseikouIdx]
    #     if haitouseikou != "-":
    #         if haitouseikou == "赤字": continue

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

    #     shihyourimawari = dividend[shihyourimawariIdx]
    #     if shihyourimawari == "赤字": continue
    
    if symbol not in ryuudoumeyasuDict: continue
    if ryuudoumeyasuDict[symbol][0] < 200: continue
    # if symbol in officerHoldDict:
    #     hold = officerHoldDict[symbol]
    #     if hold[0] <= 0.007: continue
    #     if hold[0] >= 50.18: continue
    #     if hold[3] >= 24.115: continue
    #     if hold[5] >= 0.735: continue
    #     if hold[1] + hold[2] >= 31.47: continue
    #     if hold[3] + hold[4] <= 0.0: continue

    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    cleanDataDict[symbol] = npArr

# print(len(cleanDataDict))
# print(list(cleanDataDict.keys()))
# import pandas as pd
# df = pd.DataFrame(list(cleanDataDict.keys()), columns=['Symbol'])
# df.to_csv('clean.csv')
# sys.exit()
Backtest(cleanDataDict, length, valuepegDict, 
    categoryDict, 
    shortDict, chartDict, plbsDict, 
    totalGainnerList,
    sectorPriceDict)