import pandas as pd

def GetCorr(npArr):
    df = pd.DataFrame(npArr, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    df['CloseC'] = df['Close'].pct_change()
    df['VolumeC'] = df['Volume'].pct_change()
    correlation = df['CloseC'].corr(df['VolumeC'])
    return correlation

def GetCorrVolume1(npArr):
    df = pd.DataFrame(npArr, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    df['Volume1'] = df['Volume'].shift(1)
    df['CloseC'] = df['Close'].pct_change()
    df['VolumeC'] = df['Volume1'].pct_change()
    correlation = df['CloseC'].corr(df['VolumeC'])
    return correlation

def GetCorrCl1(npArr):
    df = pd.DataFrame(npArr, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    df['Close1'] = df['Close'].shift(1)
    df['CloseC'] = df['Close'].pct_change()
    df['CloseC1C'] = df['Close1'].pct_change()
    correlation = df['CloseC'].corr(df['CloseC1C'])
    return correlation

def GetCorrCompareVol1(npArr, benchmark):
    benchmark = pd.DataFrame(benchmark, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    benchmark['Volume1'] = benchmark['Volume'].shift(1)
    benchmark['VolumeC'] = benchmark['Volume1'].pct_change()
    df = pd.DataFrame(npArr, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    df['CloseC'] = df['Close'].pct_change()
    correlation = df['CloseC'].corr(benchmark['VolumeC'])
    return correlation

def GetCorrCompareC1(npArr, benchmark):
    benchmark = pd.DataFrame(benchmark, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    benchmark['Close1'] = benchmark['Close'].shift(1)
    benchmark['Close1C'] = benchmark['Close1'].pct_change()
    df = pd.DataFrame(npArr, columns=["Open", "High", "Low", "Close", "Volume", "Date"])
    df['CloseC'] = df['Close'].pct_change()
    correlation = df['CloseC'].corr(benchmark['Close1C'])
    return correlation
