rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDataWithVolumeDate
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.data import GetDataLts
from modules.csvDump import LoadCsv
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.data import GetDataWithVolumeDate
from datetime import datetime, timedelta
from modules.upDownRatio import GetUpDownRatio
from modules.aiztradingview import GetDayTrade, GetETF
import pickle


dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUSLarge.p"
# dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeJP.p"

dataDictUS = LoadPickle(dataPathUS)
# dataDictJP = LoadPickle(dataPathJP)

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

# @njit
def round_down_to_multiple_of_10(number):
    return (number // 10) * 10

# @njit
def round_up_to_multiple_of_100(number):
    remainder = number % 100
    if remainder == 0:
        return number
    else:
        return number + (100 - remainder)

def calculate_beta(array_a, array_b):
    # Calculate covariance matrix
    cov_matrix = np.cov(array_a.astype(float), array_b.astype(float))

    # Covariance between array_a and array_b
    cov_ab = cov_matrix[0, 1]

    # Variance of array_b
    var_b = cov_matrix[1, 1]

    # Calculate beta
    beta = cov_ab / var_b

    return beta

def Backtest(dataDict, length, sampleArrJP, 
    stockList, attrLimit):
    balance = 1
    maxBalance = 1
    ddList = []
    mddList = []
    attrList = []
    sma25Dict = {}
    
    for i in range(5, length):
        perfDict = {}
        isShort = False
        topPerf = 99
        topSymbol = ""
        today = sampleArrJP[i][5]
        # print(today,i)
        if not isShort:
            for symbol, npArr in dataDict.items():
                try:
                    if npArr[i-1][0] == 0: continue
                    if npArr[i-1][3] > npArr[i-1][1]: continue
                    # if symbol not in gainnerDict[i]: continue
                    if npArr[i-1][3] / npArr[i-3][2] >= 1.5317460317460319: continue
                    if npArr[i-2][4] < 1: continue
                    # if symbol in stockList:
                    #     if npArr[i-1][2] * npArr[i-1][4] < 1593684107: continue
                    if npArr[i-1][3] < npArr[i-2][2]: continue

                    if (
                        npArr[i-3][3] / npArr[i-3][0] > 1.21 and
                        npArr[i-3][4] / npArr[i-4][4] > 7 and
                        npArr[i-3][0] < npArr[i-4][2]
                    ): continue

                    # if (
                    #     abs(npArr[i-1][3] - npArr[i-1][0]) /
                    #     (abs(npArr[i-2][3] - npArr[i-2][0]))
                    # ) >= 8.744564821992382: continue

                    if abs(npArr[i-2][3] - npArr[i-2][0]) > 0:
                        if (
                            abs(npArr[i-1][3] - npArr[i-1][0]) /
                            (abs(npArr[i-2][3] - npArr[i-2][0]))
                        ) >= attrLimit: continue

                    if (
                        (npArr[i-1][1] - npArr[i-1][2]) / 
                        (abs(npArr[i-1][3]-npArr[i-1][0]) + 1)
                    ) >= 151.92919921875: continue

                    if (
                        (npArr[i-1][3] - npArr[i-1][2]) / 
                        (abs(npArr[i-1][3]-npArr[i-1][0]) + 1)
                    ) >= 68.70204960111414: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-3][0]) /
                        (abs(npArr[i-3][3] - npArr[i-5][0]) + 1)
                    ) >= 165.22058251568: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-3][0]) /
                        (abs(npArr[i-4][3] - npArr[i-6][0]) + 1)
                    ) >= 88.06833117614251: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-5][0]) /
                        (abs(npArr[i-2][3] - npArr[i-6][0]) + 1)
                    ) >= 79.0909090909091: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-5][0]) /
                        (abs(npArr[i-4][3] - npArr[i-8][0]) + 1)
                    ) >= 101.7412903636711: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-5][0]) /
                        (abs(npArr[i-6][3] - npArr[i-10][0]) + 1)
                    ) >= 643.1508052708639: continue

                    if (
                        abs(npArr[i-1][3] - npArr[i-6][0]) /
                        (abs(npArr[i-2][3] - npArr[i-7][0]) + 1)
                    ) >= 41.325315739215526: continue

                    if (abs(npArr[i-2][3] - npArr[i-2][0])) > 0:
                        if (
                            abs(npArr[i-1][3] - npArr[i-1][0]) /
                            (abs(npArr[i-2][3] - npArr[i-2][0]))
                        ) >= 9.001526256600833: continue

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

                    deltaPeriod = 3
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
                        if delta >= 113.20631341600902: continue

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
                    # if bias >= 0.7702747072343219: continue

                    try:
                        peArr = np.empty(0)
                        for j in range(2, 8):
                            peArr = np.append(peArr, npArr[i-j][3])
                        avgHighLow = split_list_average_high_low(peArr)
                        if peArr[0]/avgHighLow[1] > 1.61: continue
                    except: pass

                    perf = (
                        abs(npArr[i-1][3] - npArr[i-1][0]) /
                        (abs(npArr[i-2][3] - npArr[i-2][0]) +1)
                    )

                    if perf < topPerf:
                        topPerf = perf
                        topSymbol = symbol
                    perfDict[symbol] = perf
                except Exception as e:
                    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
                    print(e)
                    continue

        if topSymbol == "": continue
        npArr = dataDict[topSymbol]
        # sl = npArr[i][0] * 0.98
        # if npArr[i-1][7] < npArr[i][0]:
        #     sl = npArr[i-1][7]
        sl = npArr[i][0] * 0.95
        close = npArr[i][3]
        if npArr[i][2] < sl: close = sl
        gain = close / npArr[i][0]
        lastBalance = balance
        balance *= gain
        # print(topSymbol, balance, sampleArrJP[i][5])

        # perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1]))
        # tradeList = []
        # count = 0
        # for k, v in perfDict.items():
        #     tradeList.append(k)
        #     count += 1
        #     if count > 1: break
        # tradeListLen = len(tradeList)
        # if tradeListLen < 1: continue
        # vol = balance/tradeListLen
        # lastBalance = balance
        # balance = 0
        # for symbol in tradeList:
        #     npArr = dataDict[symbol]
        #     op = npArr[i][0]
        #     tp = npArr[i][3]
        #     gain = tp / op * vol
        #     balance += gain
        # print(tradeList, balance, sampleArrJP[i][5])
        
        if balance < lastBalance:
            ddList.append(balance/lastBalance)
        if balance > maxBalance:
            maxBalance = balance
        elif balance < maxBalance:
            mddList.append(balance/maxBalance)
    #     if gain < 1:
    #         attr = (
    #             abs(npArr[i-1][3] - npArr[i-1][0]) /
    #             (abs(npArr[i-2][3] - npArr[i-2][0]))
    #         )
    #         if attr not in attrList:
    #             attrList.append(attr)
    # attrList.sort()
    # print(attrList)
    # ddList.sort()
    # print("Daily Draw Down:", ddList[0])
    mddList.sort()
    # print("MDD:", mddList[0])
    return mddList[0]

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

# @njit
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

def HandleBacktestWR(dataDict, symbol):
    npArr = dataDict[symbol]
    wr = BacktestWR(npArr)
    return [symbol, wr]

length = len(dataDictUS["AAPL"])
dataDict = dataDictUS

sampleArrJP = dataDictUS["AAPL"]
sampleArrJP = sampleArrJP[-length:]

cleanDataDict = {}

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


sampleArr = dataDict["AAPL"]

fxList = [
    "EURUSD=X",
    "AUDUSD=X",
    "GBPUSD=X",
    "USDCAD=X",
    "USDCHF=X",
    "USDJPY=X",
    "USDHKD=X",
    "USDSEK=X",
    "USDSGD=X",
    "USDCNH=X",
    "NZDUSD=X",
    "AUDCHF=X",
    "AUDJPY=X",
    "AUDNZD=X",
    "CADCHF=X",
    "CADJPY=X",
    "CHFJPY=X",
    "EURAUD=X",
    "EURCAD=X",
    "EURCHF=X",
    "EURGBP=X",
    "EURJPY=X",
    "EURNZD=X",
    "GBPAUD=X",
    "AUDCAD=X",
    "GBPCAD=X",
    "USDZAR=X",
    "GBPCHF=X",
    "GBPJPY=X",
    "GBPNZD=X",
    "NZDCAD=X",
    "NZDCHF=X",
    "NZDJPY=X",

    "USDEUR=X",
    "USDAUD=X",
    "USDGBP=X",
    "CADUSD=X",
    "CHFUSD=X",
    "JPYUSD=X",
    "HKDUSD=X",
    "SEKUSD=X",
    "SGDUSD=X",
    "CNHUSD=X",
    "USDNZD=X",
    "CHFAUD=X",
    "JPYAUD=X",
    "NZDAUD=X",
    "CHFCAD=X",
    "JPYCAD=X",
    "JPYCHF=X",
    "AUDEUR=X",
    "CADEUR=X",
    "CHFEUR=X",
    "GBPEUR=X",
    "JPYEUR=X",
    "NZDEUR=X",
    "AUDGBP=X",
    "CADAUD=X",
    "CADGBP=X",
    "ZARUSD=X",
    "CHFGBP=X",
    "JPYGBP=X",
    "NZDGBP=X",
    "CADNZD=X",
    "CHFNZD=X",
    "JPYNZD=X"
]
stockList = [
    "AMZN", "AMD", "AXP", "AMGN", 
    "ADI", "AAPL", "AMAT", "T", 
    "AVGO", "BA", "BAC", "BBY", "CSCO", 
    "C", "KO", "GLW", "EBAY", "F", "GE",
    "GS", "GOOG", "GOOGL", "HON", "HPQ", 
    "INTC", "JNJ", "JPM", "MCD", "MRK", "MU", 
    "MSFT", "MSI", "NFLX", "NVDA", "ORCL", 
    "PEP", "PFE", "PG", "QCOM", "RTX", "SBUX", 
    "TXN", "TSLA", "UNH", "ADBE", "WMT", 
    "A", "AIG", "APA", "BIIB", "BMY",
    "BSX", "CHKP", "CIEN", "CRUS", "EOG",
    "SCHW", "LLY", "XOM", "FLEX", "GPS", "GM",
    "HAL", "HD", "INTU", "JBL", "JNPR", "KSS",
    "LMT", "MDT", "QRVO", "SLB", "UPS", "VRSN",
    "VZ", "VIAV", "WMB", "XRX", "IP",
]
symbolList = [
    # "AMZN", "AMD", "AXP", "AMGN", 
    # "ADI", "AAPL", "AMAT", "T", 
    # "AVGO", "BA", "BAC", "BBY", "CSCO", 
    # "C", "KO", "GLW", "EBAY", "F", "GE",
    # "GS", "GOOG", "GOOGL", "HON", "HPQ", 
    # "INTC", "JNJ", "JPM", "MCD", "MRK", "MU", 
    # "MSFT", "MSI", "NFLX", "NVDA", "ORCL", 
    # "PEP", "PFE", "PG", "QCOM", "RTX", "SBUX", 
    # "TXN", "TSLA", "UNH", "ADBE", "WMT", 
    # "A", "AIG", "APA", "BIIB", "BMY",
    # "BSX", "CHKP", "CIEN", "CRUS", "EOG",
    # "SCHW", "LLY", "XOM", "FLEX", "GPS", "GM",
    # "HAL", "HD", "INTU", "JBL", "JNPR", "KSS",
    # "LMT", "MDT", "QRVO", "SLB", "UPS", "VRSN",
    # "VZ", "VIAV", "WMB", "XRX", "IP",
    # "BRK-B", "SMH", "DIA", "XLE",
    "SPY",
    # "^N225", "^GDAXI", "^GSPC", "^NDX", "^DJI", "^HSI",
    # "^XAU", 
]

closeDict = GetDayTrade()

# symbolList += fxList
for symbol, npArr in dataDict.items():
    npArr = dataDict[symbol]
    if len(npArr) < length: continue
    # if symbol in stockList:
    #     if symbol not in closeDict: continue
    if symbol not in symbolList: continue
    cleanDataDict[symbol] = npArr

print(len(cleanDataDict))

attrList = [0.00469940979014604, 0.009010928388046036, 0.014891771691910926, 0.01599121323025747, 0.022345480178882535, 0.025137825246084006, 0.03856811598023337, 0.04392328894357456, 0.046010253789792954, 0.046995264763247904, 0.04795538571107343, 0.05149114421690163, 0.05172050668587698, 0.06183088727170324, 0.06525180428739184, 0.06881895475836111, 0.08050896771106772, 0.08152902361350926, 0.08195962022502053, 0.08435301500878341, 0.08617832042441376, 0.09322574527147019, 0.09569978437116776, 0.09676910879058102, 0.1190418620315087, 0.12395145091107453, 0.125784519734738, 0.12610810837035974, 0.12690348680417174, 0.12946096462829218, 0.14549618154163468, 0.15421376958587513, 0.15726988492473568, 0.16338566131726967, 0.16467828516286717, 0.17421445229143342, 0.17475035790326746, 0.17757115966003081, 0.18000284041976428, 0.18053831744138396, 0.185956770662564, 0.21188056688083895, 0.21215205380333113, 0.21621224243363726, 0.23041438530100944, 0.23337327886786152, 0.24035614663475696, 0.2419275506064558, 0.25323504735295116, 0.2573261925095261,
0.26787775297265226, 0.28340944672333884, 0.307801522176787, 0.33500670980014535, 0.33874778046601034, 0.35471172795496236, 0.36176389299796335, 0.36734555826045756, 0.3678617726079937, 0.3924063703958129, 0.39393715182875705, 0.394457379752455, 0.3973242263928802, 0.39740166484340866, 0.4025584001612295, 0.40687303252885626, 0.41688064926969454, 0.42252318534128985, 0.4249938169013209,
0.42638362671982527, 0.43976010878399013, 0.4439748598677245, 0.44526204476543, 0.4523787747944757, 0.4523832220646421,
0.45321995978526974, 0.46083516430947297, 0.4698108645628241, 0.47383595815200774, 0.4838652395335861, 0.5166639116005239, 0.5273977111377776, 0.5402304661677831, 0.5510717674083576, 0.5518391972615253, 0.5526822773561929, 0.5566454614699071, 0.5651101938576704, 0.5673558117497662, 0.5680312799115074, 0.5698012820879484, 0.5698899774267965, 0.5882310544080656, 0.5931787784963456, 0.5987409330190252, 0.6000014299360253, 0.617456417159668, 0.634164491252986, 0.6536573995691379, 0.6540527668900721, 0.6642686451597296, 0.677225580901242,
0.6842211070005344, 0.688261172353825, 0.706604147468063, 0.7417451767259527, 0.7431575360986634, 0.7984891403647768, 0.8051475950588473, 0.8149736948144788, 0.8253227691458421, 0.8272167474317622, 0.8388829852654858, 0.8498733596729909, 0.8523679469025981, 0.8666585261507815, 0.8732956480181475, 0.883257805314071, 0.9168909837340058, 0.9354941917700335, 0.9481990470261409, 0.9764027392675335, 0.9854513351123103, 0.9999998084158588, 1.0266925572719037, 1.0284474123539231, 1.0568041360048277, 1.066664351727286, 1.0718859472095346, 1.0909134257045137, 1.1023012588273615, 1.1069311519373848, 1.1230367529037761, 1.1265903391961727, 1.1325097950860836, 1.152537001768874, 1.1529458605867682, 1.1818132382593889, 1.1844036147236872, 1.1940210129964777, 1.2293584938332398, 1.2396625706978714, 1.2469105788146757, 1.2475248093751297, 1.269248727906045, 1.3039809114889764, 1.3140971493803029, 1.3254343093548044, 1.3280373808254708, 1.3333333651820292, 1.358083975561304, 1.3908025791919743, 1.3919498790889457, 1.3991539264378337, 1.4047492465383489, 1.4218820899135243, 1.4234886941048572, 1.4283111556676888, 1.4459413374793912, 1.4692657086004697, 1.4930484513088202, 1.503475557026565, 1.5073888122600656, 1.5178201634877384, 1.5230997285889483, 1.5280916213760352, 1.6085383945838778, 1.6835090454516666, 1.7045358769422339, 1.7272654463286428, 1.7603025963199095, 1.9274340421342784, 1.949739148225185, 2.010913479291269, 2.013056388570436, 2.029754865564245, 2.0364785033194686, 2.066681578655736, 2.073464092055791, 2.074997762298694, 2.2291700264824543, 2.2748218532520084, 2.2776238264884836, 2.3333538840937114, 2.3376112015727757, 2.412029113579432, 2.4332011059726324, 2.510442825973962, 2.5551866713720095, 2.592815681130924, 2.620702748889343, 2.740419026549229, 2.810808330372789, 2.91567265169742, 2.9230317425546604, 2.9611669491918833, 3.3525589171339094, 3.539978086981326, 3.7270205144606305, 3.9151262337867823, 4.399755415296916, 4.429615642790993, 4.448068744227905, 4.4856572343004935, 4.486185718509283, 4.838299984551971, 4.895422423979321,
4.9998606495902775, 5.000538444976192, 5.205657497109761, 5.6362880026482856, 5.752671387416207, 6.112743523538247, 6.189655549049793, 7.393564437317426, 7.546614861452594, 8.353858972448789, 8.46103344730549]
# 8.353858972448789
maxBalance = 0
maxAttr = 0
for attrLimit in attrList[::-1]:
    balance = Backtest(cleanDataDict, length, sampleArr,
    stockList, attrLimit)
    if balance > maxBalance:
        maxBalance = balance
        maxAttr = attrLimit
    print(maxBalance, maxAttr, attrLimit)
