import yfinance as yf

def GetData(symbol):
    try:
        stockInfo = yf.Ticker(symbol)
        df = stockInfo.history(period="max")
        df = df[['Open','High','Low','Close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def checkSignal(signalArr, signal2Arr, signal3Arr, baseArr):
    shift = -1
    val = 0.00
    signalGain = signalArr[-1+shift][3] / signalArr[-2+shift][3]
    signal2Gain = signal2Arr[-1+shift][3] / signal2Arr[-2+shift][3]
    signal3Gain = signal3Arr[-1+shift][3] / signal3Arr[-2+shift][3]
    baseGain = baseArr[-1+shift][3] / baseArr[-2+shift][3]
    if (
        signalGain > baseGain*(1+val) and
        signal2Gain > baseGain*(1+val) and
        signal3Gain > baseGain*(1+val)
    ): return 1
    elif (
        signalGain < baseGain*(1-val) and
        signal2Gain < baseGain*(1-val) and
        signal3Gain < baseGain*(1-val)
    ): return -1
    else: return 0

signalArr = GetData("SPY")
signal2Arr = GetData("QQQ")
signal3Arr = GetData("IWM")
baseArr = GetData("DIA")

signal = checkSignal(signalArr, signal2Arr, signal3Arr, baseArr)
print(signal)