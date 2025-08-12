rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.ib_data import Get1mData

from ib_insync import *
from datetime import datetime as dt, timedelta
import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=31)
def FrequencyCheck1mShift(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    end = dt.strptime(str('2023-02-10 06:00:00'), '%Y-%m-%d %H:%M:%S')
    data = ib.reqHistoricalData(
        contract, endDateTime=end, durationStr='1 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["open","close"],keep=False)
    print(len(df))
    print(df)
    print(df.iloc[-1].close)
    if len(df) < 213: return False
    return True

def FrequencyCheck1m(symbol):
    df = Get1mData(symbol,1)
    df = df.drop_duplicates(subset=["open","close"],keep=False)
    print(len(df))
    if len(df) < 35: return False
    return True



if __name__ == '__main__':
    # res = FrequencyCheck1m('HIVE')
    # res = FrequencyCheck1m('CELZ')
    # FrequencyCheck1mShift('CELZ')
    FrequencyCheck1mShift('QQQ')
    # FrequencyCheck1mShift('TSLA')
    # print(res)