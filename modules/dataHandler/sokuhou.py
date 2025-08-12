import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
from scipy import stats

FOLDER = f"{rootPath}/data/jp/sokuhou"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def SaveSokuhou(symbol, sokuhou):
    if len(sokuhou) < 1: return 0
    df = pl.DataFrame(sokuhou)
    df.columns = ['da', 'kaizan', 'kaizan_c',
                    'kaizan_s', 'kaizan_h',
                    'urizan', 'urizan_c',
                    'urizan_s', 'urizan_h',
                    'bairitsu']
    df = df.with_columns(
        pl.col("da").str.to_datetime("%Y/%m/%d")
    )
    
    int_cols = ['kaizan', 
                    'kaizan_s', 'kaizan_h',
                    'urizan', 
                    'urizan_s', 'urizan_h']
    for col in int_cols:
        df = df.with_columns(pl.col(col).cast(pl.UInt64))
    float_cols = ['bairitsu']
    for col in float_cols:
        df = df.with_columns(pl.col(col).cast(pl.Float32))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

cacheData = {}
def GetSokuhou(symbol, col, da, offset=0):
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
        item = df.select(col).tail(1).item()
        return item
    except Exception as e:
        print(symbol, "Sokuhou Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return 0

def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z

cacheDataZ = {}
import pandas as pd
def GetSokuhouZ(symbol, col, da, offset=0):
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
    fname = f"{FOLDER}/{symbol}.parquet"
    df = pl.read_parquet(fname)
    print(df)

if __name__ == '__main__':
    # npArr = GetSokuhou('6315', 'kaizan_c', '2024-04-14')
    # npArr = GetSokuhou('6315', 'kaizan_c', '2024-04-14', 1)
    # npArr = GetSokuhouZ('6232', 'urizan', '2024-04-15')
    # print(npArr)
    df = GetDf('6315')
    print(df)
    # GetDf('6232')