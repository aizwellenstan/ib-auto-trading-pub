import holidays
import pytz
from datetime import datetime, timedelta
import pandas as pd

HOLIDAYS_US = holidays.US()

def GetNextBusinessDay(days=1):
    now = datetime.now(pytz.timezone('America/Chicago'))
    print(now.hour)
    if (
        now.hour >= 15 or 
        now.hour < 5
    ): days += 1
    oneDay = timedelta(days=1)
    next_day = now.date()
    for i in range(0, days):
        next_day += oneDay
        while next_day.weekday() in holidays.WEEKEND or next_day in HOLIDAYS_US:
            next_day += timedelta(days=1)
    return next_day

def GetBusinessDays(start, end):
    startTime = datetime.strptime(start, '%Y-%m-%d')
    endTime = datetime.strptime(end, '%Y-%m-%d')
    dates = pd.date_range(startTime,endTime,freq='D')

    res = []
    for date in dates:
        if date.weekday() in holidays.WEEKEND or date in HOLIDAYS_US:
            continue
        res.append(date)
    return res

if __name__ == '__main__':
    dates=GetBusinessDays('2020-03-18','2023-01-19')
    print(dates)