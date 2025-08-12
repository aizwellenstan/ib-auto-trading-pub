rootPath = ".."
import os
import pandas as pd
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import yfinance as yf
from modules.vwap import Vwap
import csv
import sys
from datetime import datetime

def GetExDividendTime(ticker, currency="USD"):
    if currency == "JPY":
        ticker += ".T"
    print(yf.Ticker(ticker).info)
    exdividendTime = yf.Ticker(ticker).info['exDividendDate']
    return pd.to_datetime(exdividendTime, unit='s')

def GetDataWithVolumeDate(ticker, startTime="2021-03-19", market="jp"):
    try:
        ticker = ticker.replace(".","-")
        if market == "AX":
            ticker += ".AX"
        elif market == "tw":
            ticker += ".TW"
        else:
            try:
                int(ticker)
                ticker += ".T"
            except: pass
        df = yf.Ticker(ticker).history(start=startTime)
        df['Date'] = df.index
        date=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(DateStr=date.dt.strftime('%Y-%m-%d'))
        npArr = df[["Open","High","Low","Close","Volume","DateStr"]].to_numpy()
        return npArr
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetVolume(symbol):
    try:
        stockInfo = yf.Ticker(symbol)
        hist = stockInfo.history(period="2d")
        hist = hist.dropna()
        if len(hist) < 1: return
        v = hist.Volume.values
        return v[-2]
    except:
        return 0

def GetDfInside(symbol, currency, update, period="max"):
    folder = f"{rootPath}/backtest/csv/vwap/{currency}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    csvPath = f"{folder}/{symbol}.csv"
    if os.path.exists(csvPath) and not update:
        df = pd.read_csv(csvPath)
    else:
        try:
            if "." in symbol:
                symbol = symbol.replace(".","-")
            if currency != 'JPY':
                stockInfo = yf.Ticker(symbol)
            else:
                stockInfo = yf.Ticker(symbol+'.T')
            hist = stockInfo.history(period=period)
            hist = hist.dropna()
            if len(hist) < 1: return
            v = hist.Volume.values
            h = hist.High.values
            l = hist.Low.values
            hist['Vwap'] = Vwap(v,h,l)
            # hist['Rsi'] = Rsi(hist.Close.values.tolist())
            # hist['Adx'] = Adx(hist)
            hist.to_csv('../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol))
            df = hist
            df['Date'] = df.index
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
            return []
    return df

def GetDf(symbol, currency='USD', update=True, period="7560d"):
    df = GetDfInside(symbol, currency, update, period)
    if df is None:
        return []
    return df

def GetNpData(symbol, currency="USD", update=True):
    df = GetDf(symbol, currency, update)
    if len(df) < 1: return[]
    # weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
    # df=df.assign(Weekday=weekday.dt.dayofweek)
    # df = df[['Open','High','Low','Close','Weekday']]
    df = df[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    return npArr

def GetNpDataVolume(symbol, currency="USD", update=True):
    df = GetDf(symbol, currency, update)
    if len(df) < 1: return[]
    df = df[['Open','High','Low','Close','Volume']]
    npArr = df.to_numpy()
    return npArr

def GetNpDataVolumeWeekday(symbol, currency="USD", update=True):
    df = GetDf(symbol, currency, update)
    if len(df) < 1: return[]
    weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
    df=df.assign(Weekday=weekday.dt.dayofweek)
    df = df[['Open','High','Low','Close','Volume','Weekday']]
    npArr = df.to_numpy()
    return npArr

def GetNpDataDate(symbol, currency="USD", update=True):
    df = GetDf(symbol, currency, update)
    if len(df) < 1: return[]
    date=pd.to_datetime(df.Date, format='%Y-%m-%d')
    # df=df.assign(Weekday=date.dt.dayofweek)
    df=df.assign(DateStr=date.dt.strftime('%Y-%m-%d'))
    # df = df[['Open','High','Low','Close','DateStr','Volume']]
    df = df[['Open','High','Low','Close','DateStr']]
    npArr = df.to_numpy()
    return npArr

def GetNpDataInspection(symbol, currency="USD", update=True):
    df = GetDf(symbol, currency, update, period="562d")
    if len(df) < 1: return[]
    df = df[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    return npArr

def GetNpData25D(symbol, currency, update):
    df = GetDf(symbol, currency, update, period="25d")
    if len(df) < 1: return[]
    # weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
    # df=df.assign(Weekday=weekday.dt.dayofweek)
    # df = df[['Open','High','Low','Close','Weekday']]
    df = df[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    return npArr

def GetDfShort(symbol, currency, update):
    if os.path.exists('../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol)) and not update:
        df = pd.read_csv(r'../backtest/csv/vwap/{}/{}.csv'.format(currency,symbol))
    else:
        try:
            stockInfo = yf.Ticker(symbol)
            hist = stockInfo.history(period="60d")
            hist = hist.dropna()
            if len(hist) < 1: return
            # v = hist.Volume.values
            # h = hist.High.values
            # l = hist.Low.values
            # hist['Vwap'] = Vwap(v,h,l)
            # hist['Rsi'] = Rsi(hist.Close.values.tolist())
            # hist['Adx'] = Adx(hist)
            # hist.to_csv('./csv/vwap/{}/{}.csv'.format(currency,symbol))
            print(symbol)
            df = hist
            # df['Date'] = df.index
        except:
            return []
    return df

def GetNpDataShort(symbol, currency, update):
    df = GetDfShort(symbol, currency, update)
    if len(df) < 1: return[]
    # weekday=pd.to_datetime(df.Date, format='%Y-%m-%d')
    # df=df.assign(Weekday=weekday.dt.dayofweek)
    # df = df[['Open','High','Low','Close','Weekday']]
    df = df[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    return npArr

def CheckHaveOption(symbol, currency='USD'):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
    
        optionChain=list(stockInfo.options)
        haveOptionChain = False
        if len(optionChain) > 0:
            haveOptionChain = True
        return haveOptionChain
    except:
        return False

def GetData(symbol, currency="USD"):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        data = stockInfo.history(period="max")
        return data
    except: return []

def GetDataWithVolume(ticker):
    try:
        ticker = ticker.replace(".","-")
        try:
            int(ticker)
            ticker += ".T"
        except:
            pass
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Volume"]].to_numpy()
        return npArr
    except: return []

def GetDataLts(ticker):
    try:
        ticker = ticker.replace(".","-")
        try:
            int(ticker)
            ticker += ".T"
        except:
            pass
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Volume"]].to_numpy()
        return npArr
    except: return []
    
def GetDataWithDate(ticker):
    try:
        df = yf.Ticker(ticker).history(start="2021-03-19")
        df['Date'] = df.index
        date=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(DateStr=date.dt.strftime('%Y-%m-%d'))
        npArr = df[["Open","High","Low","Close","DateStr"]].to_numpy()
        return npArr
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetDataWithDateTime(symbol):
    try:
        ticker = symbol.replace(".","-")
        df = yf.Ticker(ticker).history(start="2021-03-19")
        df['Date'] = df.index
        npArr = df[["Open","High","Low","Close","Date"]].to_numpy()
        return npArr
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetAllDataWithDate(ticker):
    try:
        df = yf.Ticker(ticker).history(period="max")
        df['Date'] = df.index
        date=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(DateStr=date.dt.strftime('%Y-%m-%d'))
        npArr = df[["Open","High","Low","Close","DateStr"]].to_numpy()
        return npArr
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetDataWithDividends(symbol, currency="USD"):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        data = stockInfo.history(start="2021-03-19")
        df = data[['Open','High','Low','Close','Dividends']]
        return df.to_numpy()
    except: return []

def GetDataWithDividendsLts(ticker):
    try:
        ticker = ticker.replace(".","-")
        try:
            int(ticker)
            ticker += ".T"
        except:
            pass
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Dividends"]].to_numpy()
        return npArr
    except: return []

def GetDividendToPrice(symbol, currency="USD"):
    if currency != 'JPY':
        stockInfo = yf.Ticker(symbol)
    else:
        stockInfo = yf.Ticker(symbol+'.T')
    data = stockInfo.history(start="2021-03-19")
    df = data[['Open','High','Low','Close','Dividends']]
    dividendKey = 'Dividends'
    dividends = df.loc[df['Dividends']>1]['Dividends']
    avg = dividends.quantile(0.99)
    dfLenBefore = len(df)
    dividends = dividends[dividends < avg * 1.0593220338983054]
    dividend = sum(dividends)
    dfLenAfter = len(df[dividendKey])
    if dfLenAfter > 0:
        avgDividend = dividend/dfLenAfter
        dividend += (dfLenBefore-dfLenAfter)*avgDividend
    return dividend/df.iloc[-1]['Close']

def GetDateWithDividends(symbol, currency="USD", update=True):
    try:
        df = GetDf(symbol, currency, update)
        if len(df) < 1: return[]
        date=pd.to_datetime(df.Date, format='%Y-%m-%d')
        df=df.assign(DateStr=date.dt.strftime('%Y-%m-%d'))
        df = df[['Open','High','Low','Close','Dividends','DateStr']]
        return df.to_numpy()
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetDividend(symbol, currency='USD'):
    dividend = 0
    try:
        df = GetData(symbol, currency)
        df = df.loc[df['Dividends'] > 0]
    except: return 0
    df = df.assign(date=df.index.date)
    df = df.assign(previousDate=df.date.shift(1))
    df = df.assign(duration = df.index.date-df.previousDate)
    dividendKey = "Dividends"
    if len(df) < 3: return 0
    maxDur = df.duration.max().days
    if maxDur > 366: return 0
    avg = df[dividendKey].quantile(0.99)
    # if currency == "USD":
    #     df = df.assign(duration = pd.to_datetime(df.paymentDate)-pd.to_datetime(df.previousDate))
    # else:
    df = df[(df.index.date>datetime.strptime('2021-03-18','%Y-%m-%d').date())]
    dfLenBefore = len(df)
    df = df[df[dividendKey] < avg * 1.0593220338983054]
    dividend = df[dividendKey].values
    dividend = sum(dividend)
    dfLenAfter = len(df[dividendKey])
    if dfLenAfter > 0:
        avgDividend = dividend/dfLenAfter
        dividend += (dfLenBefore-dfLenAfter)*avgDividend
    
    return dividend

def GetAdj(market='tw', ticker='2330'):
    ticker += ".TW"
    df = yf.download(ticker)
    return df
