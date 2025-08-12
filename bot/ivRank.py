rootPath = "..";import sys;sys.path.append(rootPath)
import os
from datetime import datetime
import pandas as pd
from modules.forwardQt import GetForward
from modules.data import GetDataWithVolumeDate


# Function to extract the date from the file name
def extract_date(file_name):
    parts = file_name.split(".")[0].rsplit("-", 3)
    date_str = "-".join(parts[-3:])
    return datetime.strptime(date_str, '%m-%d-%Y')

# Function to find the latest file and date
def find_latest_file(files):
    latest_file = None
    latest_date = None

    for file in files:
        file_date = extract_date(file)
        if latest_date is None or file_date > latest_date:
            latest_date = file_date
            latest_file = file

    return latest_file, latest_date

def sort_iv_rank(data):
    data['IV Rank'] = data['IV Rank'].str.replace('%', '').astype(float)
    data['IV Pctl'] = data['IV Pctl'].str.replace('%', '').astype(float)
    data['Imp Vol'] = data['Imp Vol'].str.replace('%', '').astype(float)

    data = data[(data['IV Rank'] > 50) & (data['IV Pctl'] > 50) & (data['Options Vol'] > 669560)]
    # Sort the DataFrame by "IV Rank" and then by "IV Pctl" in descending order
    sorted_data = data.sort_values(by=['IV Rank', 'IV Pctl', 'Imp Vol'], ascending=[False, False, False])

    # Create a dictionary with Symbol:IV Rank
    result_dict = dict(zip(sorted_data['Symbol'], sorted_data['IV Rank']))

    return result_dict

def get_latest_dfs(directory):
    files = os.listdir(directory)

    # Filter files with specific keywords for stocks and ETFs
    stock_files = [file for file in files if 'stock' in file.lower() and 'iv-rank-and-iv-percentile' in file]
    etf_files = [file for file in files if 'etf' in file.lower() and 'iv-rank-and-iv-percentile' in file]

    # Find the latest stock and ETF files
    latest_stock_file, _ = find_latest_file(stock_files)
    latest_etf_file, _ = find_latest_file(etf_files)

    # Read the latest stock and ETF files into dataframes
    latest_stock_df = pd.read_csv(os.path.join(directory, latest_stock_file)).iloc[:-1]
    latest_etf_df = pd.read_csv(os.path.join(directory, latest_etf_file)).iloc[:-1]
    df_merged = pd.concat([latest_stock_df, latest_etf_df], ignore_index=True)

    return sort_iv_rank(df_merged)

# Example usage
directory = f"{rootPath}/data/iv"
stockDict = get_latest_dfs(directory)

cleanStockDict = {}
for symbol, ivRank in stockDict.items():
    try:
        forward = GetForward(symbol, None, {})[-1][1]
    except: continue
    if forward <= 0: continue
    cleanStockDict[symbol] = ivRank

print(cleanStockDict)
stockDict = dict(sorted(stockDict.items(), key=lambda item: item[1], reverse=True))
print(stockDict)

tradeDict = {}
for symbol, ivRank in stockDict.items():
    close = GetDataWithVolumeDate(symbol)[-1][3]
    tradeDict[symbol] = close
print(tradeDict)

df = pd.DataFrame(tradeDict.items(), columns=["Symbol", "Close"])
df.set_index('Symbol', inplace=True)
df.to_csv(f"{rootPath}/data/iv.csv")
