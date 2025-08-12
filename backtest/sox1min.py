import yfinance as yf

from ib_insync import *
import pandas as pd

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=7)

def GetData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df[['open','high','low','close']]
    npArr = df.to_numpy()
    
    return npArr

def GetDf(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    return df

df = GetDf('SPY')
soxxdf = GetDf('SOXX')
df['soxxOpen'] = df.date.map(soxxdf.set_index('date')['open'].to_dict())
df['soxxClose'] = df.date.map(soxxdf.set_index('date')['close'].to_dict())
df.to_csv('soxx.csv')

# def GetData(symbol):
#     try:
#         stockInfo = yf.Ticker(symbol)
#         df = stockInfo.history(period="max")
#         df = df[['Open','High','Low','Close']]
#         npArr = df.to_numpy()
#         return npArr
#     except: return []

from numba import jit
@jit(nopython=True)
def checkGain(npArr, soxNpArr, i , lookback, gainVal):
    gain = npArr[i][3] / npArr[i-lookback][3]
    soxGain = soxNpArr[i][3] / soxNpArr[i-lookback][3]
    if soxGain > gain * (1+gainVal): return 1
    elif soxGain < gain * (1-gainVal): return -1
    else: return 0


@jit(nopython=True)
def Backtest(npArr, soxNpArr, lookback, gainVal, testArr):
    total = 1
    for i in range(0, len(npArr)):
        direction = checkGain(npArr, soxNpArr, i-1, lookback, gainVal)
        if direction > 0:
            profit = testArr[i-1][3] / testArr[i-1][0]
            total *= profit
            # print(profit)
        # elif direction < 0:
        #     profit = -(npArr[i-1][3] - npArr[i-1][0])
        #     total += profit
    return total


def main():
    maxLookBack = 0
    maxGainVal = 0
    maxTotal = 0

    npArr = GetData('SPY')
    soxNpArr = GetData('SOXX')
    testArr = GetData('QQQ')
    # soxNpArr = GetData('SOXX')

    npArr = npArr[-600:]
    soxNpArr = soxNpArr[-600:]
    testArr = testArr[-600:]

    lookback = 1
    gainVal = 0
    total = Backtest(npArr, soxNpArr, lookback, gainVal, testArr)

    if total > maxTotal:
        maxTotal = total
        maxLookBack = lookback
        maxGainVal = gainVal

        print(f"total {total} maxLookBack {maxLookBack} maxGainVal {gainVal}")

    # lookback = 0
    # while lookback < 60:
    #     lookback += 1
    #     gainVal = 0
    #     while gainVal < 2:
            
    #         total = Backtest(npArr, soxNpArr, lookback, gainVal)

    #         if total > maxTotal:
    #             maxTotal = total
    #             maxLookBack = lookback
    #             maxGainVal = gainVal

    #             print(f"total {total} maxLookBack {maxLookBack} maxGainVal {gainVal}")
    #         gainVal += 0.01

main()