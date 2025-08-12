import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime

FOLDER = f"{rootPath}/data/jp/lending"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def SaveLending(symbol, lending):
    if len(lending) < 1: return 0
    print("SAVING", symbol)
    df = pl.DataFrame(lending)
    df.columns = ['da', 'kashizan', 'kashizan_c',
                    'kashizan_s', 'jikouzan',
                    'jikouzan_c', 'jikouzan_s',
                    'tentai', 'tentai_c',
                    'tentai_s']
    df = df.with_columns(
        pl.col("da").str.to_datetime("%Y-%m-%d")
    )
    
    int_cols = ['kashizan', 'kashizan_s', 
                'jikouzan', 'jikouzan_s',
                'tentai', 'tentai_s']
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
def GetLending(symbol, col, da, offset=0):
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
        # print(symbol,"Lending Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return 0

def GetDf(symbol):
    fname = f"{FOLDER}/{symbol}.parquet"
    df = pl.read_parquet(fname)
    print(df)

def GetLendingList():
    from os import listdir
    from os.path import isfile, join
    print(FOLDER)
    files = [f for f in listdir(FOLDER)]
    return files

if __name__ == '__main__':
    tentai_s = GetLending("6315", 'tentai_s', "2024-04-21")
    print(tentai_s)