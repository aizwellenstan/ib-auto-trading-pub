import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
import numpy as np
from modules.dataHandler.category import GetSymbolList

FOLDER = f"{rootPath}/data/jp/bs"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

LOG_FILE = FOLDER+'error.csv'
def SaveBS(symbol, bs):
    if len(bs) < 1: return 0
    try:
        df = pl.DataFrame(bs)
        columns = ['da', 'current_assets', 'current_liabilities',
                        'non_current_assets', 'non_current_liabilities',
                        'total_assets'
                    ]
        df.columns = columns
    except Exception as e:
        print(symbol, "BS Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        import pandas as pd
        import datetime
        if not os.path.exists(LOG_FILE):
            df = pd.DataFrame([[symbol, e, datetime.datetime.now()]], columns=["Symbol", "Error", "Time"])
            df.to_csv(LOG_FILE, index=False)
        else:
            df = pd.read_csv(LOG_FILE)
            new_row = pd.DataFrame([[symbol, e, datetime.datetime.now()]], columns=["Symbol", "Error", "Time"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(LOG_FILE, index=False)
        return -1
    # df = df.with_columns(
    #     pl.col("da").str.to_datetime("%Y-%m")
    # )
    
    # int_cols = ['current_assets', 'current_liabilities',
    #             'non_current_assets', 'non_current_liabilities',
    #             'total_assets']
    # for col in int_cols:
    #     df = df.with_columns(pl.col(col).cast(pl.UInt64))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)
    return 1

cacheData = {}
def GetBS(symbol, col, da):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]

        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())
        df = df.filter(df['da'] <= da)
        
        item = df.select(col).tail(1).item()
        return item
    except Exception as e:
        # print(symbol, "BS Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return 0

def GetChartDf(symbol, da):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]

        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())
        df = df.filter(df['da'] <= da)
        return df
    except Exception as e:
        # print(symbol, "Chart Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return 0

def GetChartArr(symbol, da=''):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]

        if da != '':
            if isinstance(da, str):
                da = datetime.strptime(da, '%Y-%m-%d')
            else:
                da = datetime.combine(da, datetime.min.time())
        
            df = df.filter(df['da'] <= da)
        item = df.select('*').rows()
        item = [list(row) for row in item]
        return np.array(item)
    except Exception as e:
        # print(symbol, "Chart Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return []

def GetDf(symbol):
    try:
        fname = f"{FOLDER}/{symbol}.parquet"
        df = pl.read_parquet(fname)
        return df
    except: return []

def GetNpArr(symbol):
    df = GetDf(symbol)
    if len(df) < 1: return []
    df = df.with_columns(df['da'].dt.strftime('%Y-%m-%d'))
    df = df[['op', 'hi', 'lo', 'cl', 'vol', 'da', 'mc', 'bias25']]
    npArr = df.to_numpy()
    return npArr

def GetDataDict():
    symbolList = GetSymbolList()
    sampleArr = GetNpArr("7203")
    length = len(sampleArr)
    dataDict = {}
    for symbol in symbolList:
        npArr = GetNpArr(symbol)
        if len(npArr) < length: continue
        dataDict[symbol] = npArr
    return dataDict

if __name__ == '__main__':
    from modules.irbank import GetBS
    symbol = '7203'
    bs = GetBS(symbol)
    print(bs[-1])
    res = SaveBS(symbol, bs)
    print(res)
    # current_assets = GetBS(symbol, 'current_assets', '2024-06-24')
    # print(current_assets)