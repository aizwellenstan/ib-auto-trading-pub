rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
import yfinance as yf
from datetime import datetime

# df = yf.download(tickers="SPY", period="7d", interval="1m")

# df['Date'] = df.index
# df = df[['Open','High','Low','Close','Volume','Date']]

dataPath = f"{rootPath}/backtest/pickle/pro/compressed/spyOneMinFull.p"
# import pickle
# pickle.dump(df, open(dataPath, "wb"))
df = LoadPickle(dataPath)
# vwap = df.resample('D').apply(lambda x: (x['Close'] * x['Volume']).sum() / x['Volume'].sum())
# npArr = df.to_numpy()
# print(npArr)
df['Timestamp'] = df['Date']

# Extract date from timestamp
df['Date'] = df['Timestamp'].dt.date

# Group by date
grouped = df.groupby('Date')

# Calculate cumulative volume and cumulative value traded
df['CumulativeVolume'] = grouped['Volume'].cumsum()
df['CumulativeValue'] = df['Close'] * df['Volume']
df['CumulativeValue'] = grouped['CumulativeValue'].cumsum()

# Calculate VWAP
df['VWAP'] = df['CumulativeValue'] / df['CumulativeVolume']

# Select only the last row of each date to get the daily VWAP
# interday_vwap = df.groupby('Date').tail(1)[['Date', 'VWAP']].reset_index(drop=True)

print(df['VWAP'].to_csv("spyOneMin.csv"))
# vwapClean = df['VWAP'].between_time('09:30', '17:00')
df = df['VWAP']
filtered_df = df[df.index.strftime('%H:%M:%S%z') == '09:30:00-0500']
filtered_df['Date'] = filtered_df.index.date

# Reset index to make 'Date' a regular column
filtered_df.reset_index(drop=True, inplace=True)
filtered_df.to_csv("spyOneMinD.csv", index=False)
# print(vwap)