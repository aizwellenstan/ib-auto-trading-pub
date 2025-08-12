import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import polars as pl
import numpy as np
from modules.data import GetDataWithVolumeDate
import duckdb
from sqlalchemy import create_engine, text
engine = create_engine("duckdb:///:memory:")

FOLDER = f"{rootPath}/data/jp/price"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

FOLDER5MINJP = f"{rootPath}/data/jp/price/15min"
ensure_directory_exists(FOLDER5MINJP)

def SaveMinPrice(market, symbol):
    FOLDER = f"{rootPath}/data/{market}/price/15min"
    filePath = f"{FOLDER}/{symbol}.parquet"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=59)
    ticker = str(symbol)
    if market == "jp": ticker += ".T"
    try:
        print("DOWNLOAD", symbol)
        df = yf.download(ticker, start=start_date, interval='15m')
        if len(df) < 1: return - 1
        if os.path.exists(filePath):
            source_df = pd.read_parquet(filePath)
            df = pd.concat([source_df, df])
            df = df[~df.index.duplicated(keep='last')]
        df.to_parquet(filePath)
        print("SAVING", symbol)
    except: return -1

def GetDf(market, symbol):
    FOLDER = f"{rootPath}/data/{market}/price/15min"
    filePath = f"{FOLDER}/{symbol}.parquet"
    df = pd.read_parquet(filePath)
    return df

def SavePrice(symbol, price):
    if len(price) < 1: return 0
    df = pl.DataFrame(price, infer_schema_length=int(1000))

    df.columns = ['open', 'high', 'low', 'close', 'vol', 'date']
    
    # numeric_cols = ['open', 'high', 'low', 'close']
    # for col in numeric_cols:
    #     df = df.with_columns(pl.col(col).cast(pl.Float32))
    # df = df.with_columns(pl.col('vol').cast(pl.UInt64))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

def SaveNpArr(symbol):
    npArr = GetDataWithVolumeDate(symbol)
    df = pl.DataFrame({
        'op': npArr[:, 0].astype(np.int32),
        'hi': npArr[:, 1].astype(np.int32),
        'lo': npArr[:, 2].astype(np.int32),
        'cl': npArr[:, 3].astype(np.int32),
        'vol': npArr[:, 3].astype(np.int32),
        'da': npArr[:, 5].astype(str)
    }, infer_schema_length=int(1000))

    df = df.with_columns(
        pl.col("da").str.to_datetime("%Y-%m-%d", strict=False)
    )
   
    numeric_cols = ['op', 'hi', 'lo', 'cl', 'vol']
    for col in numeric_cols:
        df = df.with_columns(pl.col(col).cast(pl.UInt64))
    filePath = f"{FOLDER}/{symbol}.parquet"
    if os.path.exists(filePath):
        sourceDf = pl.read_parquet(filePath)
        df = pl.concat([sourceDf, df])
        df = df.unique(subset=['da'])
        df = df.sort('da')
    df.write_parquet(filePath)

def GetNpArr(symbol):
    fname = f"{FOLDER}/{symbol}.parquet"
    df = pl.read_parquet(fname)
    return df.to_numpy()

def get_market_index_das(market, code):

    fname = f"{FOLDER}/{code}.parquet"

    sql = f"select da from '{fname}' order by da asc"

    df = duckdb.query(sql).df()

    das = df['da'].dt.date

    return das

if __name__ == '__main__':
    SaveMinPrice("jp", "6315")