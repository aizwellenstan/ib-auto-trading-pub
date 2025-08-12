import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))

print("CALLED")
def main():
    import numpy as np
    from modules.aiztradingview import GetLiquidETF
    liquidEtfs = GetLiquidETF()
    alpha_list = []
    def Backtest(dataDict, length, sampleArr):
        for symbol1 in liquidEtfs:
            for symbol2 in liquidEtfs:
                if symbol1 == symbol2: continue
                if symbol1 not in dataDict: continue
                if symbol2 not in dataDict: continue
                if len(dataDict[symbol1]) != len(dataDict[symbol2]): continue
                chanceUp = np.empty(0)
                optimizedChanceUp = np.empty(0)
                balanceOptimize = 1
                for i in range(3, length-1):
                    today = sampleArr[i][5]
                    for symbol, npArr in dataDict.items():
                        diff = length - len(npArr)
                        if symbol != symbol2: continue
                        if npArr[i][3] > npArr[i][0]: chanceUp = np.append(chanceUp, 1)
                        else: chanceUp = np.append(chanceUp, 0)
                        if (
                            # dataDict[symbol1][i-3][3] < dataDict[symbol1][i-3][0] and
                            # dataDict[symbol1][i-2][3] < dataDict[symbol1][i-2][0] and
                            dataDict[symbol1][i-1][3] < dataDict[symbol1][i-1][0]
                        ):
                            if npArr[i][3] > npArr[i][0]: optimizedChanceUp = np.append(optimizedChanceUp, 1)
                            else: optimizedChanceUp = np.append(optimizedChanceUp, 0)
                            balanceOptimize *= ((npArr[i+1][0] - npArr[i][0]) / npArr[i][0] * 0.5 + 1)
                            
                        # balance *= ((npArr[i][3] - npArr[i][0]) / npArr[i][0] * 0.5 + 1)
                    # print(balanceOptimize, balance)
                print(symbol1, symbol2, np.mean(optimizedChanceUp) * 100, np.mean(chanceUp) * 100)
                has_alpha = np.mean(optimizedChanceUp) * 100 > np.mean(chanceUp) * 100
                print(symbol1, symbol2, has_alpha)
                if has_alpha: 
                    alpha_list.append([symbol1, symbol2, balanceOptimize])
                if len(alpha_list) < 1: continue
                df = pd.DataFrame(alpha_list)
                df.columns = ["symbol1", "symbol2", "balance"]
                df = df.sort_values(by='balance', ascending=False)
                df.to_csv("chance.csv")

    from modules.loadPickle import LoadPickle
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
    from modules.csvDump import LoadDict
    import multiprocessing
    num_processes = multiprocessing.cpu_count()
    print("num_processes", num_processes)

    dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
    dataDictUS = LoadPickle(dataPathUS)

    optionPath = f"{rootPath}/data/tradableOption.csv"
    optionDict = LoadDict(optionPath, "Length")

    length = len(dataDictUS["AAPL"])
    dataDict = dataDictUS

    sampleArr = dataDictUS["AAPL"]
    sampleArr = sampleArr[-length:]

    import pandas as pd
    df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
    cfd = df['Symbol'].values.tolist()

    sampleArr = dataDict["AAPL"]

    length = len(sampleArr)
    cleanDataDict = {}
    liquidEtfs = GetLiquidETF()
    for symbol, npArr in dataDict.items():
        npArr = dataDict[symbol]
        if symbol not in cfd: continue
        if symbol not in liquidEtfs: continue
        cleanDataDict[symbol] = npArr
    cleanDataDict["XLE"] = dataDict["XLE"]
    cleanDataDict["GBTC"] = dataDict["GBTC"]
    cleanDataDict["XOP"] = dataDict["XOP"]
    cleanDataDict["GLD"] = dataDict["GLD"]
    cleanDataDict["TSM"] = dataDict["TSM"]
    cleanDataDict["DIA"] = dataDict["DIA"]
    cleanDataDict["SPY"] = dataDict["SPY"]
    cleanDataDict["SCHD"] = dataDict["SCHD"]
    cleanDataDict["QQQ"] = dataDict["QQQ"]
    cleanDataDict["SMH"] = dataDict["SMH"]
    del dataDict
    print(len(cleanDataDict))
    Backtest(cleanDataDict, length, sampleArr)

if __name__ == "__main__":
    main()
