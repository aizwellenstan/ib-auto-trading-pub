import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from modules.dataHandler.category import GetSymbolList
from modules.irbank import GetShort
from modules.dataHandler.short import SaveShort
import numpy as np

def generate_date_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime('%Y-%m-%d')
        current_date += timedelta(days=1)

def HandleGetShort(symbol, dateList):
    for da in dateList:
        short = GetShort(symbol, da)
        SaveShort(symbol, short)
    return [symbol, short]

def CheckFileExist(symbol):
    fPath = f'{rootPath}/data/jp/short/{symbol}.parquet'
    if not os.path.exists(fPath):
        return False
    return True

def CheckLengthGood():
    dataDict = GetDataDict()
    miss = np.empty(0)
    for symbol, npArr in dataDict.items():
        if len(npArr) >= 747:
            miss = np.append(miss, symbol)
    return miss

def cleanUp(symbolList):
    for symbol in symbolList:
        fPath = f'{rootPath}/data/jp/short/{symbol}.parquet'
        os.remove(fPath)

def main():
    symbolList = GetSymbolList()
    # good = CheckLengthGood()
    # symbolList = list(set(symbolList)-set(good))

    # cleanList = np.empty(0)
    # for symbol in symbolList:
    #     if not CheckFileExist(symbol):
    #         cleanList = np.append(cleanList, symbol)
    # symbolList = cleanList

    start_date = datetime(2020, 3, 1)
    end_date = datetime.now()

    date_list = list(generate_date_range(start_date, end_date))
    
    download = []
    for i in range(0, len(date_list), 10):
        download.append(date_list[i])
    download.append(date_list[-1])
    print(download)
    # import pandas as pd
    # df = pd.read_csv("backtest_symbols.csv")
    # df.columns = ['index', 'symbol']
    # symbolList = df['symbol'].values.tolist()
    # print(symbolList)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(HandleGetShort, symbol, download) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()

if __name__ == '__main__':
    main()
    # fileExist = CheckFileExist('6315')
    # print(fileExist)
    # miss = CheckLength()
    # print(miss, len(miss))