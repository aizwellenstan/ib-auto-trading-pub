rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
import numpy as np
from modules.csvDump import DumpDict

dataDict = {}

shift = 0

symbolDict = {'HCP': 66, 'JAKK': 3, 'VTNR': 3, 'SEAT': 39, 'EE': 4,
'HOOD': 24, 'NRDS': 89, 'TSLA': 2, 'GFS': 50, 'EXFY': 23, 
'COUR': 99, 'COIN': 48, 'TASK': 87, 'PTGX': 68, 'AI': 99, 
'PLTR': 79, 'CRSR': 13, 'BILL': 77, 'CPRX': 80, 'TMDX': 24, 'RCUS': 7, 'CARG':
8, 'RVNC': 70, 'LQDA': 4, 'MAXN': 9, 'DSEY': 49, 
'PUBM': 49, 'PD': 8, 'SNOW': 11, 'DKNG': 49, 'VERX': 36, 'ACAD': 7, 'PINS': 35, 'ALGM': 93,
'XM': 98, 'NAPA': 8, 'MRNA': 2, 'SKYT': 5, 'SGML': 6, 'ROKU': 9, 'RRC': 8, 
'CDNA': 8, 'PETS': 7, 'HP': 2, 'HNI': 7, 'XP': 99, 'FREY': 74, 'BYD': 22, 'TITN': 4, 'LVS': 52, 'FNB': 15, 'VITL': 36, 'GPS': 7, 'EWBC': 8, 'SHOP': 7, 'STNE': 28, 'BBIO': 5, 'DVN': 2, 'GNE': 26, 'ITCI': 3, 'FF': 9, 'NVDA': 90, 'MGNI': 6, 'ASRT': 2, 'RNR': 9, 'GME': 87, 'MDB': 10, 'STLD': 97, 'DOCU': 34, 
'TER': 88, 'CRWD': 61, 'PYPL': 45, 'SSD': 42, 'DLX': 79, 
'HIMS': 89, 'MCHP': 39, 'ASTS': 99, 'MAT': 34, 'CARA': 2, 'LEVI': 6, 'ACGL': 14, 'RUSHA': 11, 'LITE': 45, 'XOM': 2, 'OXY': 3, 'QCOM': 9, 'NTRS': 73, 'KBAL': 20, 'CIEN': 98, 'ETN': 10, 'AGCO': 35, 'LEG': 4, 'STNG': 3, 'MTN': 15, 'META': 90, 'DIS': 81, 
'GIII': 5, 'HRZN': 36, 'SMAR': 79,
'PGR': 3, 'UBER': 31, 'AMD': 2, 'HAS': 8, 'AAL': 27, 'AXP': 58, 'STLA': 41, 'ET': 2, 'TH': 8, 'CCL': 16, 'RIG': 2, 'GOOGL': 50, 'GE': 27, 'GAIN': 19, 'COF': 7, 'GWRE': 27, 'TGT': 18, 'CHGG': 3, 'T': 20, 
'BNS': 64, 'UHAL': 5, 'F':
4, 'VIRT': 28, 'AMZN': 57, 'JOE': 25, 'AAPL': 3, 'CSX': 20, 'MSFT': 9, 'IDCC': 5, 'CDNS': 88, 'NFLX': 6, 'EQH': 90, 'YUM': 3, 'TAP': 15, 'EXTR': 4, 'UNH': 9, 'EVH':
20, 'AEE': 4, 'ATVI': 6, 'KO': 22, 'WM': 16, 'ANGO': 3, 'AMGN': 9, 'PM': 15, 'CPB': 2, 'CL': 10, 'UAL': 2, 'SMG': 3, 
'ALK': 2, 'NEE': 3, 'MDLZ': 3, 'TTC': 3, 'MRK': 5, 'CAT': 3, 'MGNX': 20, 'BMY': 5, 'INTC': 9, 'PEP': 4, 'RDFN': 2, 'JNJ': 2}

minLength = 1058
signals = ["IWM","HYG","AAPL","XLP","^N225","^GDAXI","QQQ","SPY","SQQQ","UVXY"]
oriLengthArr = np.empty(0, dtype=int)
for symbol in signals:
    npArr = GetNpData(symbol)
    dataDict[symbol] = npArr
    oriLengthArr = np.append(oriLengthArr,len(npArr))
rironDict = {}
for symbol, attr in symbolDict.items():
    if symbol in dataDict:
        npArr = dataDict[symbol]
    else:
        npArr = GetNpData(symbol)
    if len(npArr) < 2: continue
    lenArr = np.append(oriLengthArr, len(npArr))
    minLength = min(lenArr)
    print("minLength",minLength)
    signalValDict = {}
    avgSignalValDict = {}
    npArr = npArr[-minLength:]
    for signal in signals:
        signalNpArr = dataDict[signal][-minLength:]
        signalVal = npArr[:,3]/signalNpArr[:,3]
        signalValDict[signal] = signalVal
        avgSignalValDict[signal] = np.sum(signalVal[minLength-attr:minLength])/attr

    last = len(npArr)
    tpQQQ = dataDict["QQQ"][-1][3] * avgSignalValDict["QQQ"]
    tpSPY = dataDict["SPY"][-1][3] * avgSignalValDict["SPY"]
    if (
        signalValDict["IWM"][-1] < avgSignalValDict["IWM"] and
        signalValDict["HYG"][-1] < avgSignalValDict["HYG"] and
        signalValDict["AAPL"][-1] < avgSignalValDict["AAPL"] and
        signalValDict["XLP"][-1] < avgSignalValDict["XLP"] and
        signalValDict["^N225"][-1] < avgSignalValDict["^N225"] and
        signalValDict["^GDAXI"][-1] < avgSignalValDict["^GDAXI"] and
        signalValDict["SQQQ"][-1] < avgSignalValDict["SQQQ"] and
        signalValDict["UVXY"][-1] < avgSignalValDict["UVXY"]
    ):
        rironDict[symbol] = min(tpQQQ, tpSPY)
        print(symbol,  min(tpQQQ, tpSPY))

rironPath = f"{rootPath}/data/RironRefined.csv"
DumpDict(rironDict, "riron", rironPath)
