import pandas as pd
import yfinance as yf

def GetExDividendTime(ticker, currency="USD"):
    if currency == "JPY":
        ticker += ".T"
    print(yf.Ticker(ticker).info)
    exdividendTime = yf.Ticker(ticker).info['exDividendDate']
    return pd.to_datetime(exdividendTime, unit='s')