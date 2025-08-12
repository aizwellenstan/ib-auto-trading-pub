import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from ib_insync import *
import pandas as pd
from modules.movingAverage import Sma, Ema, SmaArr, EmaArr
import math

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=30)

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

def Get1mData(symbol, day):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr=f"{day} D",
        barSizeSetting='1 min', whatToShow='ASK', useRTH=True)
    df = pd.DataFrame(data)
    
    return df

def GetCustomData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    contract = Stock('SPY', 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    spydf = pd.DataFrame(data)
    contract = Stock('NVDA', 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    nvdadf = pd.DataFrame(data)

    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    
    spydf['date'] = pd.to_datetime(spydf['date'], format="%Y-%m-%d %H:%M:%S")
    df['spyOpen'] = df.date.map(spydf.set_index('date')['open'].to_dict())
    df['spyHigh'] = df.date.map(spydf.set_index('date')['high'].to_dict())
    df['spyLow'] = df.date.map(spydf.set_index('date')['low'].to_dict())
    df['spyClose'] = df.date.map(spydf.set_index('date')['close'].to_dict())
    nvdadf['date'] = pd.to_datetime(nvdadf['date'], format="%Y-%m-%d %H:%M:%S")
    df['nvdaOpen'] = df.date.map(nvdadf.set_index('date')['open'].to_dict())
    df['nvdaHigh'] = df.date.map(nvdadf.set_index('date')['high'].to_dict())
    df['nvdaLow'] = df.date.map(nvdadf.set_index('date')['low'].to_dict())
    df['nvdaClose'] = df.date.map(nvdadf.set_index('date')['close'].to_dict())
    df = df[['open','high','low','close','spyOpen','spyHigh','spyLow','spyClose','nvdaOpen','nvdaHigh','nvdaLow','nvdaClose']]
    npArr = df.to_numpy()
    
    return npArr

def GetSmaData(symbol, x, y):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    closeArr = []
    for d in data:
        closeArr.append(d.close)
    smaXArr = SmaArr(closeArr, x)
    smaYArr = SmaArr(closeArr, y)
    smaX = smaXArr
    smaY = smaYArr
    ema100 = Ema(closeArr, 100)
    ema500 = Ema(closeArr, 500)
    df['smaX'] = smaX
    df['smaY'] = smaY
    df['ema100'] = ema100
    df['ema500'] = ema500
    df = df[['open','high','low','close','smaX','smaY','ema100','ema500']]
    npArr = df.to_numpy()
    
    return npArr

def GetEmaData(symbol, x, y):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='5 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    closeArr = []
    for d in data:
        closeArr.append(d.close)
    emaXArr = EmaArr(closeArr, x)
    emaYArr = EmaArr(closeArr, y)
    ema100 = Ema(closeArr, 100)
    ema500 = Ema(closeArr, 500)
    df['emaX'] = emaXArr
    df['emaY'] = emaYArr
    df['ema100'] = ema100
    df['ema500'] = ema500
    df = df[['open','high','low','close','emaX','emaY','ema100','ema500']]
    npArr = df.to_numpy()
    
    return npArr

def GetEmaDataDf(symbol, x, y):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='5 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    closeArr = []
    for d in data:
        closeArr.append(d.close)
    emaXArr = EmaArr(closeArr, x)
    emaYArr = EmaArr(closeArr, y)
    ema100 = Ema(closeArr, 100)
    ema500 = Ema(closeArr, 500)
    df['emaX'] = emaXArr
    df['emaY'] = emaYArr
    df['ema100'] = ema100
    df['ema500'] = ema500
    # df = df[['open','high','low','close','emaX','emaY','ema100','ema500']]
    # npArr = df.to_numpy()
    
    return df

def GetClasicData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    closeArr = []
    for d in data:
        closeArr.append(d.close)
    ema9 = Ema(closeArr, 9)
    ema21 = Ema(closeArr, 21)
    ema100 = Ema(closeArr, 100)
    ema500 = Ema(closeArr, 500)
    df['ema9'] = ema9
    df['ema21'] = ema21
    df['ema100'] = ema100
    df['ema500'] = ema500
    df = df[['open','high','low','close','ema9','ema21','ema100','ema500']]
    npArr = df.to_numpy()
    
    return npArr

def GetVolume(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    ticker=ib.reqMktData(contract, '', False, False)
    if math.isnan(ticker.volume): return 0
    return ticker.volume*100