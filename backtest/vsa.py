rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolume

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose
from modules.csvDump import DumpCsv, LoadCsv, DumpDict
import pickle
import pandas as pd

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJPVolume.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolume.p"

update = False
if update:
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpDataVolume(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

    for symbol, close in closeDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpDataVolume(symbol)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    pickle.dump(dataDict, open(picklePath, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(picklePath, "rb")
    dataDict = pickle.load(output)
    output.close()

def Backtest(npArr):
    oriNpArr = npArr
    maxBalance = 0
    maxVal = 0
    period = 1
    while period < 756:
        npArr = oriNpArr[-(756+period):]
        stock_data = pd.DataFrame(npArr, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        high_price = stock_data["High"]
        low_price = stock_data["Low"]
        close_price = stock_data["Close"]
        typical_price = (high_price + low_price + close_price) / 3

        # Calculate the daily volume spread
        daily_volume = stock_data["Volume"]
        prev_close = close_price.shift(1)
        daily_range = high_price - low_price
        daily_range[daily_range == 0] = np.nan
        daily_range_pct = daily_range / prev_close * 100
        daily_volume_pct = daily_volume / daily_volume.mean() * 100
        daily_volume_spread = daily_range_pct * daily_volume_pct

        # Define the buy and sell signals
        buy_signal = (daily_volume_spread > 0) & (daily_volume_spread > daily_volume_spread.shift(1))
        sell_signal = (daily_volume_spread < 0) & (daily_volume_spread < daily_volume_spread.shift(1))

        # Add a moving average to the signals
        signal_period = period
        buy_signal_ma = buy_signal.rolling(signal_period).mean()
        sell_signal_ma = sell_signal.rolling(signal_period).mean()

        # Create a DataFrame with the buy and sell signals
        signals = pd.DataFrame(index=stock_data.index)
        signals["Buy"] = buy_signal_ma
        signals["Sell"] = sell_signal_ma

        # Backtest the strategy by calculating the returns
        daily_returns = close_price.pct_change()
        trade_returns = (daily_returns * buy_signal_ma.shift(1) - daily_returns * sell_signal_ma.shift(1)).fillna(0)
        total_returns = trade_returns.cumsum()
        if total_returns.values[-1] > maxBalance:
            maxBalance = total_returns.values[-1]
            maxVal = period
            print(maxBalance,maxVal)
        period += 1
    return maxBalance

# for symbol, npArr in dataDictJP.items():
#     gain = Backtest(npArr)
#     print(symbol, gain)

for symbol, npArr in dataDict.items():
    if symbol != "TSLA": continue
    gain = Backtest(npArr)
    print(symbol, gain)
