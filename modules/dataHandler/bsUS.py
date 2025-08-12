import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import pandas as pd
from datetime import datetime
import numpy as np
from modules.dataHandler.category import GetSymbolList
from modules.parquet_reader import get_col_arr_before_da

FOLDER = f"{rootPath}/data/us/bs/quarter"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

LOG_FILE = FOLDER + 'error.csv'

def SaveBS(symbol, df):
    if len(df) < 1: return 0
    try:
        # Prepare file paths
        filePath = f"{FOLDER}/{symbol}.parquet"
        # If file already exists, read and concatenate data
        if os.path.exists(filePath):
            sourceDf = pd.read_parquet(filePath)
            df = pd.concat([sourceDf, df])
        
        # Remove duplicates based on 'da' column
        df = df.drop_duplicates(subset=['da'])
        
        # Sort by 'da' column
        df = df.sort_values('da')
        
        # Write to Parquet file
        df.to_parquet(filePath, index=False)
        
        return 1
    
    except Exception as e:
        # Error handling and logging
        print(f"{symbol} File Write Error: {e}")
        log_error(symbol, e)
        return -1

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


cacheData = {}
def GetBS(symbol, col, da, shift=0):
    try:
        global cacheData
        
        # Check if symbol data is cached, otherwise load from file
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            df = pd.read_parquet(fname)
            cacheData[symbol] = df
        else:
            df = cacheData[symbol]

        # Convert da to datetime if it's a string
        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())
        
        # Filter DataFrame by date
        df = df[df['da'] <= da]
        
        # Get the last value in the filtered DataFrame for the specified column
        item = df[col].astype(float).iloc[-1-shift]
        
        return item
    except Exception as e:
        # Uncomment for debugging or logging
        # print(symbol, "BS Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return 0  # Return 0 or appropriate default value on error

ignoreSet = set()
def GetBSArr(symbol, col, da):
    try:
        global cacheData, ignoreList
        if symbol in ignoreSet: return[]
        item = get_col_arr_before_da(cacheData, FOLDER, symbol, col, da)
        return item
    except Exception as e:
        # Uncomment for debugging or logging
        print(symbol, "BS Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

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
        print(symbol, "Chart Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
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
    from modules.aizfinviz import GetBSQ
    symbol = 'AAPL'
    bs = GetBSQ(symbol)
    res = SaveBS(symbol, bs)
    print(res)
    # print(bs)
    bs = GetBS(symbol, 'Total Assets', '2024-06-24')
    print(bs)