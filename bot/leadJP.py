rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.data import GetNpData
import numpy as np
import csv

def CheckSignal(signalArr, signalPeriod):
    i = len(signalArr) - signalPeriod - 1
    signalCloseArr = signalArr[i:i+signalPeriod][:,3]
    highest_index = np.argmax(signalCloseArr)
    lowesest_index = np.argmin(signalCloseArr)
    if highest_index > lowesest_index:
        return True
    return False

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'signal'])
        for symbol, signal in result_list:
            writer.writerow([symbol, signal])

def main():
    dataDict = {}
    csvPath = f"{rootPath}/data/leadJP.csv"
    result_dict = load_csv_to_dict(csvPath)
    tradeList = []
    for symbol, attr in result_dict.items():
        signal = attr[0]
        period = int(float(attr[1]))
        # if symbol not in dataDict:
        #     npArr = GetNpData(symbol)
        #     dataDict[symbol] = npArr
        # else:
        #     npArr = dataDict[symbol]
        if signal not in dataDict:
            signalArr = GetNpData(signal, 'JPY')
            dataDict[signal] = signalArr
        else:
            signalArr = dataDict[signal]
        res = CheckSignal(signalArr, period)
        if not res: continue
        print(symbol, signal)
        tradeList.append([symbol, signal])
    print(tradeList)
    csvPath = f"{rootPath}/data/LeadJPTrade.csv"
    dump_result_list_to_csv(tradeList, csvPath)

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()','output.dat')

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()
    
    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()