import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
import numpy as np
from modules.dataHandler.category import GetSymbolList
from modules.parquet_reader import get_col_arr_before_da

FOLDER = f"{rootPath}/data/jp/chart"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def SaveChart(symbol, chart):
    if len(chart) < 1: return 0
    if len(chart[0]) < 11: return 0
    df = pl.DataFrame(chart, infer_schema_length=int(2000))
    columns = ['da', 'op', 'hi', 'lo', 'cl',
                    'change', 'vol', 'mc', 'bias25', 
                    'per', 'pbr'
                ]
    if len(chart[0]) < 11:
        columns = ['da', 'op', 'hi', 'lo', 'cl',
                    'change', 'vol', 'mc', 'bias25']
    df.columns = columns
    df = df.with_columns(
        pl.col("da").str.to_datetime("%Y-%m-%d")
    )
    
    int_cols = ['op', 'hi', 'lo', 'cl', 'vol', 'mc']
    for col in int_cols:
        df = df.with_columns(pl.col(col).cast(pl.UInt64))
    float_cols = ['change', 'bias25', 'per', 'pbr']
    if len(chart[0]) < 11:
        float_cols = ['change', 'bias25']
    for col in float_cols:
        df = df.with_columns(pl.col(col).cast(pl.Float32))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        try:
            df = pl.concat([sourceDf, df])
        except: pass
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

import pyarrow.parquet as pq
from datetime import datetime

cacheData = {}
def GetChart(symbol, col, da):
    try:
        global cacheData
        item = get_col_arr_before_da(cacheData, FOLDER, symbol, col, da)
        return item[-1]
    except Exception as e:
        # Handle exceptions appropriately
        # print(symbol, "Chart Error on line {}".format(sys.exc_info()[-1].tb_lineno))
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
    # GetDataDict()
    mc = GetChart("6315", 'mc', "2024-04-21")
    print(mc)
    epsArr = GetChartArr("6315", 'per', "2024-04-23")
    print(epsArr)