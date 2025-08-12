import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
import pandas as pd
from modules.dataHandler.category import GetCategoryDict
from modules.dataHandler.chart import GetChartArr
from modules.icir import GetICIR, DumpICIRData
from datetime import datetime
from modules.movingAverage import SmaArr
from modules.loadPickle import LoadPickle

def main(update=False):
    todayStr = datetime.today().strftime('%Y-%m-%d')
    cachePath = f"{rootPath}/backtest/data/icir/cache/{todayStr}_us.parquet"
    if update:
        dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
        dataDictUS = LoadPickle(dataPathUS)
        symbolList = list(dataDictUS.keys())
        df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
        cfd = df['Symbol'].values.tolist()
        symbolList = [symbol for symbol in symbolList if symbol in cfd]
        dataDict = {}
        for symbol in symbolList:
            dataDict[symbol] = dataDictUS[symbol]

        factorDict = {}
        for symbol, npArr in dataDict.items():
            volArr = npArr[:,4]
            volSma5 = SmaArr(volArr, 5)
            volSma30 = SmaArr(volArr, 30)
            for i in range(31, len(npArr)):
                if symbol not in factorDict:
                    factorDict[symbol] = []

                signal = 1
                if npArr[i-1][3] > npArr[i-1][0]: signal = -1
                if npArr[i-1][3] > npArr[i-2][2]: signal = -1
                if npArr[i-1][3] > npArr[i-3][2]: signal = -1
                if (
                    npArr[i-2][4] < npArr[i-4][4] and
                    npArr[i-1][4] > npArr[i-2][4]
                ): signal = -1

                diff = abs(npArr[i-1][3] - npArr[i-1][0])
                if diff > 0:
                    if (
                        npArr[i-1][1] > npArr[i-2][1] and
                        npArr[i-1][3] < npArr[i-2][3] and
                        (
                            (npArr[i-1][1]-npArr[i-1][3]) / 
                            diff
                        ) > 7.9
                    ): signal = -1
                
                if volSma5[i-1] < volSma30[i-1]: signal = -1
                factorDict[symbol].append([datetime.strptime(npArr[i][5], "%Y-%m-%d"),symbol,npArr[i][3],signal])
        
        factorList = []
        for symbol, factor in factorDict.items():
            for f in factor:
                factorList.append(f)

        df = pd.DataFrame(factorList, columns=['date','symbol', 'close', 'factor'])
        df.to_parquet(cachePath)
    else:
        factorList = pd.read_parquet(cachePath).values.tolist()

    quantiles = 2
    period = 1
    factor_bins_returns, ic_summary = GetICIR(factorList, quantiles=quantiles, periods=[period])

    """
    quantiles 1.0 must < 0
    quantiles 2.o must > 0
    """
    # print(factor_bins_returns, ic_summary)

    folder = f'{rootPath}/backtest/data/icir'
    DumpICIRData(factor_bins_returns, ic_summary, 
        f"{folder}/us_1_diff_{quantiles}_{period}_icir_rtn.json", 
        f"{folder}/us_1_diff_{quantiles}_{period}_icir_stats.json")

if __name__ == '__main__':
    main(True)
    # main(False)