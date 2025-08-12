import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
from scipy import stats
import numpy as np

FOLDER = f"{rootPath}/data/jp/quarter"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def SaveQuarter(symbol, quarter):
    if len(quarter) < 1: return 0
    df = pl.from_pandas(quarter)
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

cacheData = {}
def GetQuarter(symbol, col, da, offset=0):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]
        da = datetime.strptime(da, '%Y-%m-%d')
        df = df.filter(df['da'] < da)
        item = df.select(col).tail(offset + 1).to_series().item(0)
        return item
    except Exception as e:
        # print(symbol, "Quarter Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return -1

def GetQuarterArr(symbol, col, da):
    try:
        global cacheData
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pl.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]
        da = datetime.strptime(da, '%Y-%m-%d')
        df = df.filter(df['da'] < da)
        item = df.select(col)
        item = [list(row) for row in item]
        return np.array(item)[0]
    except Exception as e:
        # print(symbol, "Quarter Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return []

def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

cacheDataZ = {}
import pandas as pd
def GetQuarterZ(symbol, col, da, offset=0):
    try:
        global cacheDataZ
        if symbol not in cacheDataZ:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pd.read_parquet(fname)
            # for col in df.columns[1:]:
            df['urizan'] = zscore(df['urizan'],10)
            df['tentai'] = zscore(df['tentai',5])
            cacheDataZ[symbol] = df
        else:
            df = cacheDataZ[symbol]

        da = datetime.strptime(da, '%Y-%m-%d')
        df = df[df['da'] < da]
        item = df[col].tail(1).to_list()[0]
        return item
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetDf(symbol):
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        # df = pl.concat([sourceDf, df])
        # df = df.unique(subset=['da'])
        # df = df.sort('da')
        print(sourceDf)


if __name__ == '__main__':
    GetDf('6319')