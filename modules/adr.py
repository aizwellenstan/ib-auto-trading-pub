import pandas as pd

def GetGreenADR(df):
    df = df.assign(nextOpen=df.Open.shift(-1))
    df = df.assign(nextClose=df.Close.shift(-1))
    bullCandle = df['nextClose'] > df['nextOpen']

    df = df.assign(dr=abs(df.Close-df.Open))
    greenADR = df.loc[bullCandle, 'dr'].mean()

    return greenADR

def GetRedADR(df):
    df = df.assign(nextOpen=df.Open.shift(-1))
    df = df.assign(nextClose=df.Close.shift(-1))
    bearCandle = df['nextClose'] < df['nextOpen']

    df = df.assign(dr=abs(df.Close-df.Open))
    redADR = df.loc[bearCandle, 'dr'].mean()

    return redADR

def GetVwapGreenADR(df):
    df = df.assign(nextOpen=df.Open.shift(-1))
    df = df.assign(nextClose=df.Close.shift(-1))
    bullCandle = df['nextClose'] > df['nextOpen']

    # df = df.assign(vwapO=df.Vwap.shift(1))
    # df = df.assign(vwapH=max(df.Vwap,df.vwapO))
    # df = df.assign(vwapL=min(df.Vwap,df.vwapO))

    df = df.assign(dr=abs(df.Vwap-df.vwapO))
    greenADR = df.loc[bullCandle, 'dr'].mean()

    return greenADR

def GetVwapRedADR(df):
    df = df.assign(nextOpen=df.Open.shift(-1))
    df = df.assign(nextClose=df.Close.shift(-1))
    bearCandle = df['nextClose'] < df['nextOpen']

    # df = df.assign(vwapO=df.Vwap.shift(1))
    # df = df.assign(vwapH=max(df.Vwap,df.vwapO))
    # df = df.assign(vwapL=min(df.Vwap,df.vwapO))

    df = df.assign(dr=abs(df.Vwap-df.vwapO))
    redADR = df.loc[bearCandle, 'dr'].mean()

    return redADR