rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
import yfinance as yf
from datetime import datetime
import pandas as pd
start_date = '2020-03-18'
end_date = '2024-03-05'
ticker_symbol = "SPY"
# Initialize an empty DataFrame to store the VWAP results
interday_vwap_combined = pd.DataFrame()

# Loop through one month of data in 7-day chunks
for i in range(0, 30, 7):
    # Calculate the start and end dates for the 7-day chunk
    chunk_start_date = pd.Timestamp(start_date) + pd.DateOffset(days=i)
    chunk_end_date = min(pd.Timestamp(start_date) + pd.DateOffset(days=i+7), pd.Timestamp(end_date))
    
    # Download one week of one-minute data from Yahoo Finance
    try:
        df = yf.download(ticker_symbol, start=chunk_start_date, end=chunk_end_date, interval='1m')
    except: continue
    interday_vwap_combined = pd.concat([interday_vwap_combined, df], axis=0)

df = interday_vwap_combined
df['Date'] = df.index
df = df[['Open','High','Low','Close','Volume','Date']]

dataPath = f"{rootPath}/backtest/pickle/pro/compressed/spyOneMinFull2.p"
import pickle
pickle.dump(df, open(dataPath, "wb"))
# df = LoadPickle(dataPath)
# print(df)