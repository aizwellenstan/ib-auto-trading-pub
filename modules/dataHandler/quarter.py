import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import polars as pl
from datetime import datetime
from scipy import stats
import numpy as np
from modules.parquet_reader import get_col_before_da

FOLDER = f"{rootPath}/data/jp/quarter"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

LOG_FILE = FOLDER + 'error.csv'

def log_error(symbol, error):
    try:
        if not os.path.exists(LOG_FILE):
            error_df = pd.DataFrame([[symbol, str(error), datetime.now()]], columns=["Symbol", "Error", "Time"])
            error_df.to_csv(LOG_FILE, index=False)
        else:
            error_df = pd.read_csv(LOG_FILE)
            new_row = pd.DataFrame([[symbol, str(error), datetime.now()]], columns=["Symbol", "Error", "Time"])
            error_df = pd.concat([error_df, new_row], ignore_index=True)
            error_df.to_csv(LOG_FILE, index=False)
            
    except Exception as e:
        print(f"Error while logging error: {e}")

def SaveQuarter(symbol, quarter):
    try:
        if len(quarter) < 1: return 0
        filePath = f"{FOLDER}/{symbol}.parquet"
        df = pl.DataFrame(quarter)
        columns = ['da', 'quarter', 'uriage',
                        'eigyourieki', 'keijyourieki',
                        'junnrieki', 'houkatsurieki']
        if len(quarter[0]) == 6:
            columns = ['da', 'quarter', 'uriage',
                        'eigyourieki', 'keijyourieki',
                        'junnrieki']
        df.columns = columns
        
        uint_cols = ['quarter']
        for col in uint_cols:
            df = df.with_columns(pl.col(col).cast(pl.UInt64))
        
        int_cols = ['uriage',
                        'eigyourieki', 'keijyourieki',
                        'junnrieki', 'houkatsurieki']
        if len(quarter[0]) == 6:
            int_cols = ['uriage',
                        'eigyourieki', 'keijyourieki',
                        'junnrieki']
        for col in int_cols:
            df = df.with_columns(pl.col(col).cast(pl.Int64))

        if os.path.exists(filePath):
            sourceDf = pl.read_parquet(filePath)
            df = pl.concat([sourceDf, df])
            df = df.unique(subset=['da'])
            df = df.sort('da')
        df.write_parquet(filePath)
    except Exception as e:
        print(f"{symbol} Quarter Error: {e}")
        log_error(symbol, e)
        return -1

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
        q = df.select('quarter').tail(offset + 1).to_series().item(0)
        item = df.select(col).tail(offset + 1).to_series().item(0)
        return [q, item]
    except Exception as e:
        # print(symbol, "Quarter Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return []

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
        df = df.unique(subset=['uriage', 'eigyourieki', 'keijyourieki', 'junnrieki'], keep='first', maintain_order=True)
        item = df.select(col)
        item = [list(row) for row in item]
        item = np.array(item)[0]
        quarter = df.select('quarter')
        quarter = [list(row) for row in quarter]
        quarter = np.array(quarter)[0]
        res = np.empty(0)
        pq = 0
        for i in range(0, len(quarter)):
            if i == 0:
                if quarter[i] != 1:
                    q = item[i] / quarter[i]
            elif quarter[i] == 1:
                q = item[i]
                pq = q
            else:
                q = item[i] - pq
                pq = item[i]
            res = np.append(res, q)
        return res
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
    # junnrieki = GetQuarter('6315', 'junnrieki', '2024-07-09')
    # print(junnrieki)
    junnrieki = GetQuarterArr('6315', 'junnrieki', '2024-07-09')
    print(junnrieki)