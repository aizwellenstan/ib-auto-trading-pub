import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
import pandas as pd
from modules.dataHandler.chart import GetChartDf
import numpy as np
from modules.parquet_reader import get_col_arr_before_da

FOLDER = f"{rootPath}/data/jp/zandaka"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def SaveZandaka(symbol, zandaka):
    if len(zandaka) < 1: return 0
    df = pl.DataFrame(zandaka)
    df.columns = ['da', 'kaizan', 'kaizan_c',
                    'urizan', 'urizan_c',
                    'kashizan', 'kashizan_c',
                    'urikashizan', 'urikashizan_c']
    df = df.with_columns(
        pl.col("da").str.to_datetime("%Y-%m-%d")
    )
    
    int_cols = ['kaizan', 'urizan', 'kashizan', 
                'urikashizan']
    for col in int_cols:
        df = df.with_columns(pl.col(col).cast(pl.UInt64))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

cacheData = {}
def GetZandaka(symbol, col, da, offset=1):
    try:
        global cacheData
        item = get_col_arr_before_da(cacheData, FOLDER, symbol, col, da)
        return item[-1]
    except Exception as e:
        print(symbol, "Zandaka Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -1

def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

def GetZandakaDf(symbol, da):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]
        da = datetime.strptime(da, '%Y-%m-%d')
        df = df.filter(df['da'] <= da)
        return df
    except Exception as e:
        print(symbol, "Zandaka Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetShortPer(symbol, da):
    chart = GetChartDf(symbol, da)
    zandaka = GetZandakaDf(symbol, da)
    df = chart.join(zandaka, on='da', how='left')
    cols = ['kaizan', 'kaizan_c',
                        'urizan', 'urizan_c',
                        'kashizan', 'kashizan_c',
                        'urikashizan', 'urikashizan_c']
    for col in cols:
        df = df.with_columns(
                [pl.col(col).forward_fill()]
        )
    df = df.to_pandas().dropna()
    shortPer = df['per']
    shortPer = shortPer.to_numpy()
    return shortPer

def GetZandakaArr(symbol, col, da, offset=0):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]
        da = datetime.strptime(da, '%Y-%m-%d')
        df = df.filter(df['da'] <= da)
        item = df.select(col).to_numpy()
        item = [row[0] for row in item]
        return item
    except Exception as e:
        print(symbol, "Zandaka Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetZandakaDf(symbol):
    if symbol not in cacheData:
        fname = f"{FOLDER}/{symbol}.parquet"
        df = pd.read_parquet(fname)
        cacheData[symbol] = df
    else:
        df = cacheData[symbol]
    return df

if __name__ == '__main__':
    # urikashizan = GetZandakaZ("6315", "urikashizan", "2024-04-21")
    # print(urikashizan)
    shortPer = GetShortPer('6315', "2024-04-27")
    print(shortPer)
