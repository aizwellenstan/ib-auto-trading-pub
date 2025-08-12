import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import duckdb
from modules.dataHandler.price import GetDf

FOLDER = f"{rootPath}/data/jp/supertrend"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def calculate_supertrend(df, period=10, multiplier=3):
    df['TR'] = np.maximum(df['High'], df['Close'].shift(1)) - np.minimum(df['Low'], df['Close'].shift(1))
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['UpperBand'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
    df['LowerBand'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']
    df['Supertrend'] = None
    df['Position'] = None

    for i in range(1, len(df)):
        if df['Close'][i] > df['UpperBand'][i - 1]:
            df['Supertrend'][i] = df['LowerBand'][i]
        elif df['Close'][i] < df['LowerBand'][i - 1]:
            df['Supertrend'][i] = df['UpperBand'][i]
        else:
            df['Supertrend'][i] = df['Supertrend'][i - 1]

    df['Position'] = df['Close'] - df['Supertrend']
    
    return df

def calculate_returns(df, symbol):
    df['Position'] = df['Position'].shift(1)
    df['Signal'] = 0
    df.loc[df['Position'] > 0, 'Signal'] = 1
    df.loc[df['Position'] < 0, 'Signal'] = -1
    df_resampled = df.resample('D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'Signal': 'last'
    }).dropna()
    df_resampled['Previous_Signal'] = df_resampled['Signal'].shift(1)
    df_resampled['Close1'] = df_resampled['Close'].shift(1)
    df_resampled['Rtn'] = df_resampled.apply(lambda row: row['Close'] / row['Open'] if (row['Previous_Signal'] == -1 and row['Open'] > row['Close1']) else 1, axis=1)
    df_resampled['NAV'] = df_resampled['Rtn'].cumprod()
    df_resampled['code'] = symbol
    return df_resampled
    
    df['Returns'] = df['Close'].pct_change() * df['Signal'].shift(1)
    return df['Returns'], df['Signal']

def calculate_nav(df):
    df['Returns'], df['Signal'] = calculate_returns(df)
    df['NAV'] = (1 + df['Returns']).cumprod()
    return df['NAV'], df['Signal']

def GetRtnSignal(symbol):
    # end_date = datetime.now()
    # start_date = end_date - timedelta(days=59)

    # df = yf.download(symbol, start=start_date, end=end_date, interval='5m')
    df = GetDf("jp", symbol)
    df = calculate_supertrend(df)
    nav, signal = calculate_nav(df)
    nav = nav.iloc[-1]
    signal = signal.iloc[-1]
    return nav, signal

def GetReturnDf(market, symbol):
    df = GetDf(market, symbol)
    df = calculate_supertrend(df)
    df = calculate_returns(df, symbol)
    return df

def SaveReturnDf(market, symbol):
    filePath = f"{FOLDER}/{symbol}.parquet"
    df = GetReturnDf(market, symbol)
    if len(df) < 1: return - 1
    if os.path.exists(filePath):
        source_df = pd.read_parquet(filePath)
        df = pd.concat([source_df, df])
        df = df[~df.index.duplicated(keep='last')]
    df.to_parquet(filePath)
    print("SAVING", symbol)
    return df

import pandas as pd
df = pd.read_csv(f"{rootPath}/data/ib_cfd_jp.csv")
cfd = df['Symbol'].values.tolist()

def GetReturn(da):
    try:
        fname = f"{FOLDER}/????.parquet"
        sqlstr = f"""
        SELECT Datetime AS da, code, NAV, Signal, Close, code FROM '{fname}' 
        where da == '{da}' and NAV > 1.003797 
        and Signal > 0
        order by NAV desc
        """
        df = duckdb.query(sqlstr).df()
        return df
    except: return []

def GetSignal(da):
    try:
        fname = f"{FOLDER}/????.parquet"
        sqlstr = f"""
        SELECT Datetime AS da, code, NAV, Signal FROM '{fname}' 
        where da == '{da}'  and NAV > 1 
        and Signal < 0
        order by NAV desc
        """
        df = duckdb.query(sqlstr).df()
        return df['code'].to_list()
    except: return []

def GetRtn(da, codes):
    codes = ','.join(codes)
    try:
        fname = f"{FOLDER}/????.parquet"
        sqlstr = f"""
        SELECT Datetime AS da, Close, Open FROM '{fname}' 
        where da == '{da}' and code in ('{codes}')
        """
        df = duckdb.query(sqlstr).df()
        return df
    except: return []

def ViewDf(symbol):
    import pandas as pd
    fname = f"{FOLDER}/{symbol}.parquet"
    df = pd.read_parquet(fname)
    print(df)

if __name__ == '__main__':
    # nav, signal = GetRtnSignal('3778')
    # print(nav, signal)
    # df = SaveReturnDf('3778')
    # print(df)
    # ViewDf('1384')
    # df = GetReturn('2024-04-11')
    # print(df)
    # codes = df['code'].to_list()
    # codes = [code for code in codes if code in cfd]
    # print(codes)
    signal = GetSignal("2024-04-17")
    print(signal)