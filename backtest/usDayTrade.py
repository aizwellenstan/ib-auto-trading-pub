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
    stockList):
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
        print(today,i)
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
        print(topSymbol, balance, sampleArrJP[i][5])

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
    ddList.sort()
    print("Daily Draw Down:", ddList[0])
    mddList.sort()
    print("MDD:", mddList[0])

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
    "BRK-B", "SMH", "DIA", "XLE",
    "SPY",
    # "^N225", "^GDAXI", "^GSPC", "^NDX", "^DJI", "^HSI",
    "^XAU", 
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
Backtest(cleanDataDict, length, sampleArr,
stockList)
