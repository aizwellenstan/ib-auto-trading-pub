rootPath = ".."
import sys
sys.path.append(rootPath)
# from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.threadPool import ThreadPool
from modules.loadPickle import LoadPickle
from modules.irbank import GetPer
from modules.aiztradingview import GetCloseJP
import numpy as np
from numba import njit
import pickle


# def UpdateData(dataDict, symbolList):
#     results = ThreadPool(symbolList, GetPer)

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


closeDictJP = GetCloseJP()
symbolList = list(closeDictJP.keys())

update = False
picklePathPerJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictPerJP.p"
if update:
    dataDict = ThreadPool(symbolList, GetPer)
    pickle.dump(dataDict, open(picklePathPerJP, "wb"))
    print("pickle dump finished")
else:
    dataDict = LoadPickle(picklePathPerJP)

# for symbol, npArr in dataDict.items():
#     print(symbol, npArr)

def CheckPer(symbol):
    try:
        npArr = dataDict[symbol]
        if len(npArr[0]) < 10: return[]
        perList = npArr[:,9].astype(np.float64)
        avgHigh, avgLow = split_list_average_high_low(perList)
        if perList[0] < avgLow: return [1]
        else: return [0]
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        print('ERR',symbol)
        print(len(npArr[0]))
        for i in npArr:
            if len(i)<9:
                print(i)

# symbolList = ['9101','5838','8887']
def main():
    symbolList = list(dataDict.keys())
    results = ThreadPool(symbolList, CheckPer)
    passedList = []
    for symbol, res in results.items():
        if res[0] < 1: continue
        passedList.append(symbol)
    print(passedList)

if __name__ == '__main__':
    main()
# print(perList)
# perList = [sublist[9] for sublist in npArr]

# avgHigh, avgLow = split_list_average_high_low(perList)
# print(perList[0], avgHigh, avgLow)
# middle = avgJ
# if perList[0]
