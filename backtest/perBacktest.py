rootPath = "..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from numba import range, njit
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    if len(high_values) > 0:
        average_high = np.mean(high_values)
    else:
        average_high = average
        
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    if len(low_values) > 0:
        average_low = np.mean(low_values)
    else:
        average_low = average
    
    return np.array([average_high, average_low])

def GetPerHiritsu(symbol, perDict, i):
    if symbol not in perDict: return[symbol, 1]
    per = perDict[symbol]
    per = per[-i+1:]
    try:
        perList = per[:,9].astype(np.float64)
        avgHigh, avgLow = split_list_average_high_low(perList)
        # maList = per[:,8].astype(np.float64)
        # if maList[0] < 0: return[symbol, 1]
        # pbrList = per[:,10].astype(np.float64)
        # avgHigh, avgLow = split_list_average_high_low(pbrList)
        perHiritsu = perList[0] / avgLow
        return [symbol, perHiritsu]
    except:
        return[symbol, 1]

picklePathPerJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictPerJP.p"
dataPathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeDateJP.p"
perDict = LoadPickle(picklePathPerJP)
dataDict = LoadPickle(dataPathJP)

# print(perDict["9101"][0])
# print(len(perDict["9101"]))

length = len(dataDict["9101"])


cleanDataDict = {}
for symbol, npArr in dataDict.items():
    if len(npArr) < length: continue
    cleanDataDict[symbol] = npArr[-100:]

balance = 1
for i in range(0, 100):
    # symbol = "9101"
    # npArr = cleanDataDict[symbol]
    # per = perDict[symbol]
    # perHiritsu = GetPerHiritsu(per)
    # print(perHiritsu)
    topSymbol = ""
    topPerHiritsu = 1
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetPerHiritsu, symbol, perDict, i) for symbol in list(cleanDataDict.keys())]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            perHiritsu = result[1]
            if perHiritsu == 1: continue
            if perHiritsu < topPerHiritsu:
                topPerHiritsu = perHiritsu
                topSymbol = symbol
    if topSymbol == "": continue
    npArr = cleanDataDict[topSymbol]
    op = npArr[i][0]
    close = npArr[i][3]
    gain = close/op
    balance *= gain
    print(balance)


# npArr = npArr[:i]
# perList = npArr[:,9].astype(np.float64)
# avgHigh, avgLow = split_list_average_high_low(perList)