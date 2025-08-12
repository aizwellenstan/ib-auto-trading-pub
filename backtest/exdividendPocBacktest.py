rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr
from modules.data import GetDf
from modules.businessday import GetBusinessDays
from modules.dividendCalendar import GetExDividendByDate
import pickle
from modules.dividend import GetDividend
import numpy as np
from datetime import datetime, timedelta
from modules.dict import take
# from modules.dividendCalendar import GetExDividend
# import pandas as pd
# import os

dividendCalendarDict = {}
picklePath = "./pickle/pro/compressed/dividendCalendar.p"
update = True
if update:
    startDate = '2021-03-18'
    endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
    dates = GetBusinessDays(startDate, endDate)
    for date in dates:
        exDivList = GetExDividendByDate(date)
        if len(exDivList) < 1: continue
        dateStr = datetime.strftime(date,'%Y-%m-%d')
        dividendCalendarDict[dateStr] = exDivList
    pickle.dump(dividendCalendarDict, open(picklePath, "wb"))
else:
    import gc
    output = open(picklePath, "rb")
    gc.disable()
    dividendCalendarDict = pickle.load(output)
    output.close()
    gc.enable()

dataDict = {}
picklePath = "./pickle/pro/compressed/dataDictDividends.p"
update = True
if update:
    closeDict = GetClose()
    for symbol, close in closeDict.items():
        df = GetDf(symbol)
        if len(df) < 1: continue
        df = df.assign(Date=df.index.date.astype(str),format='%Y-%m-%d')
        df = df[['Open','High','Low','Close','Dividends','Date']]
        npArr = df.to_numpy()
        print(symbol)
        dataDict[symbol] = npArr
    pickle.dump(dataDict, open(picklePath, "wb"))
else:
    import gc
    output = open(picklePath, "rb")
    # gc.disable()
    dataDict = pickle.load(output)
    output.close()
    # gc.enable()