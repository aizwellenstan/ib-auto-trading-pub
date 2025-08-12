import yfinance as yf
import numpy as np
fPath = "NQ.csv"
# Download historical data for QQQ
data = yf.download("NQ=F", start="2020-03-18", end="2024-10-23")
# data.to_csv(fPath)
# Calculate differences for each day compared to the previous day
npArr = data[['Open', 'High', 'Low']].to_numpy()

highDiff = []
lowDiff = []
for i in range(1, len(npArr)):
    if npArr[i][1] > npArr[i-1][1] and npArr[i][0] < npArr[i-1][1]:
        highDiff.append(npArr[i][1] - npArr[i-1][1])
    if npArr[i][2] < npArr[i-1][2] and npArr[i][0] > npArr[i-1][2]:
        lowDiff.append(npArr[i-1][2] - npArr[i][2])

print(np.max(highDiff), np.max(lowDiff))