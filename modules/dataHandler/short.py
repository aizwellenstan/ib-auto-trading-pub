import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import pandas as pd
from datetime import datetime
import numpy as np
from modules.parquet_reader import get_col_arr_before_da

FOLDER = f"{rootPath}/data/jp/short"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

LOG_FILE = FOLDER + 'error.csv'

def SaveShort(symbol, npArr):
    if len(npArr) < 1: return 0
    try:
        filePath = f"{FOLDER}/{symbol}.parquet"
        df = pd.DataFrame(npArr)
        df.columns = ['da', 'kikann', 'percentage']
        df['da'] = pd.to_datetime(df['da'])
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
ignoreSet = set()
def GetShortArr(symbol, col, da):
    try:
        global cacheData, ignoreList
        if symbol in ignoreSet: return[]
        # Check if symbol data is cached, otherwise load from file
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            try:
                df = pd.read_parquet(fname)
            except:
                ignoreSet.add(symbol)
                print(ignoreList)
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
        item = df[col].astype(float).tolist()
        return item
    except Exception as e:
        # Uncomment for debugging or logging
        # print(symbol, "Short Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        # print(e)
        return []

import pyarrow.parquet as pq
from datetime import datetime, timedelta

# Initialize cache dictionary
cacheData = {}

def GetShort(symbol, da, shift=0):
    try:
        global cacheData
        
        # Check if symbol data is cached, otherwise load from file
        if symbol not in cacheData:
            fname = f"{FOLDER}/{symbol}.parquet"
            # Read Parquet file into a table
            table = pq.read_table(fname)
            # Convert table to list of records (dictionaries)
            data = table.to_pandas().to_dict(orient='records')
            cacheData[symbol] = data
        else:
            data = cacheData[symbol]

        # Convert 'da' to a datetime object if it's a string
        if isinstance(da, str):
            da = datetime.strptime(da, '%Y-%m-%d')
        else:
            da = datetime.combine(da, datetime.min.time())

        # Calculate the date 6 months before 'da'
        date_6_months_before = da - timedelta(days=6*30)  # Roughly 6 months

        # Filter data based on date range and deduplicate based on 'kikann'
        unique_data = {}
        total_percentage = 0
        
        for record in data:
            record_date = record['da']
            if date_6_months_before < record_date < da:
                kikann = record['kikann']
                # Update record if it's the last occurrence
                unique_data[kikann] = record

        # Sum up the 'percentage' field from unique records
        total_percentage = sum(record['percentage'] for record in unique_data.values())

        return total_percentage

    except Exception as e:
        # Handle exceptions appropriately
        # print(f"Error processing symbol {symbol}: {e}")
        return -1  # Return 0 or appropriate default value on error


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
    # from modules.irbank import GetShort
    symbol = "7003"
    # short = GetShort(symbol)
    # SaveShort(symbol, short)
    short = GetShort(symbol, '2024-07-21')