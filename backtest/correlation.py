import yfinance as yf
rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.dict import take

def GetData(symbol):
    try:
        stockInfo = yf.Ticker(symbol)
        df = stockInfo.history(period="max")
        df = df[['Open','High','Low','Close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

from numba import jit
@jit(nopython=True)
def checkGain(npArr, signalArr, i , lookback, gainVal, signal2Arr):
    if npArr[i-lookback][3] < 0.01: return 0
    if signalArr[i-lookback][3] < 0.01: return 0
    if signal2Arr[i-lookback][3] < 0.01: return 0
    # if signal3Arr[i-lookback][3] < 0.01: return 0
    gain = npArr[i][3] / npArr[i-lookback][3]
    signalGain = signalArr[i][3] / signalArr[i-lookback][3]
    signal2Gain = signal2Arr[i][3] / signal2Arr[i-lookback][3]
    # signal3Gain = signal3Arr[i][3] / signal3Arr[i-lookback][3]
    if (
        signalGain > gain * (1+gainVal) and
        signal2Gain > gain * (1+gainVal)
        # signal3Gain > gain * (1+gainVal)
    ): return 1
    elif signalGain < gain * (1-gainVal): return -1
    else: return 0


@jit(nopython=True)
def Backtest(npArr, signalArr, lookback, gainVal, signal2Arr):
    total = 1
    for i in range(0, len(npArr)):
        direction = checkGain(npArr, signalArr, i-1, lookback, gainVal, signal2Arr)
        # direction = checkGain(npArr, signalArr, i-1, lookback, gainVal, signal2Arr, signal3Arr)
        if direction > 0:
            if npArr[i-1][0] < 0.01: continue
            profit = npArr[i-1][3] / npArr[i-1][0]
            total *= profit
        # elif direction < 0:
        #     profit = -(npArr[i-1][3] - npArr[i-1][0])
        #     total += profit
    return total


def main():
    import gc
    maxLookBack = 0
    maxGainVal = 0
    maxTotal = 0

    # index = ["QQQ","SPY","^N225","^NDX","^GSPC","^FTSE","^GDAXI"]
    index = ["^N225","^FTSE","^GDAXI",
    'QQQ',
    'SPY',
    'IWM',
    'VTI',
    'DIA',
    'UVXY',
    'SQQQ',
    'SLV',
    'TLT',
    'LQD',
    'VWO',
    'VEA',
    'IAU',
    'XLF',
    'XLE',
    'SOXL',
    'SPXU',
    'TZA',
    'XLU',
    'XLP',
    'XLV',
    'QID',
    'VEA']

    topOption = [
        'SPY','QQQ','DIA','IWM',
        'XLU','XLF','XLE',
        'EWG','EWZ','EEM','VXX','UVXY',
        'TLT','SQQQ',
        'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
        'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
        'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
        'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
        'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
        'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
        'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
        'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
        'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
        'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
        'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
        'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
        'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
        'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
        'CEI','GSAT','WEBR','PBR','BBBY',
        'BABA',
        'GOOG','GOOGL',
        'META','ARKK','GDX','GLD','SLV'
    ]
    perfDict = {}

    dataDict = {}

    import itertools
    comb = list(itertools.combinations(index, 2))

    for option in topOption:
        gc.collect()
        for c in comb:
            if option in c: continue
            if c[0] not in dataDict:
                signalArr = GetData(c[0])
                signalArr = signalArr[-600:]
                dataDict[c[0]] = signalArr
            else:
                signalArr = dataDict[c[0]]
            if c[1] not in dataDict:
                signal2Arr = GetData(c[1])
                signal2Arr = signal2Arr[-600:]
                dataDict[c[1]] = signal2Arr
            else:
                signal2Arr = dataDict[c[1]]
            # if c[2] not in dataDict:
            #     signal3Arr = GetData(c[2])
            #     signal3Arr = signal2Arr[-600:]
            #     dataDict[c[2]] = signal3Arr
            # else:
            #     signal3Arr = dataDict[c[2]]
            if option not in dataDict:
                npArr = GetData(option)
                npArr = npArr[-600:]
                dataDict[option] = npArr
            else:
                npArr = dataDict[option]
            total = 0
            if option not in dataDict:
                npArr = GetData(option)
                npArr = npArr[-600:]
                dataDict[option] = npArr
            else:
                npArr = dataDict[option]

            # lookback = 1
            lookback = 2
            gainVal = 0
            total = Backtest(npArr, signalArr, lookback, gainVal, signal2Arr)
            # total = Backtest(npArr, signalArr, lookback, gainVal, signal2Arr, signal3Arr)

            # print(f"{option} total {total} maxLookBack {maxLookBack} maxGainVal {gainVal}")
            perfDict[c[0]+'_'+c[1]+'_'+option] = total
            # perfDict[c[0]+'_'+c[1]+'_'+c[2]+'_'+option] = total

    perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1], reverse=True))
    print(take(1000,perfDict))
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