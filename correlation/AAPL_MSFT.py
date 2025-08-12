import yfinance as yf

def GetData(symbol):
    try:
        stockInfo = yf.Ticker(symbol)
        df = stockInfo.history(period="max")
        df = df[['Open','High','Low','Close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def checkSignal(soxArr, spyArr):
    shift = -2
    val = 0.00
    soxGain = soxArr[-1+shift][3] / soxArr[-2+shift][3]
    spyGain = spyArr[-1+shift][3] / spyArr[-2+shift][3]
    if soxGain > spyGain*(1+val): return 1
    elif soxGain < spyGain*(1-val): return -1
    else: return 0

soxArr = GetData("AAPL")
spyArr = GetData("MSFT")

signal = checkSignal(soxArr, spyArr)
print(signal)