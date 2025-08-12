import pandas as pd
import requests
import datetime
from user_agent import generate_user_agent

class DividendCalendar:
    calendars = [] 
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.nasdaq.com/',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': generate_user_agent()
    }

    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.session = requests.Session()
     
    def get_dividends(self, day):
        date_str = f"{self.year}-{self.month:02d}-{day:02d}"
        response = self.session.get(self.url, params={'date': date_str}, headers=self.headers)
        rows = response.json().get('data', {}).get('calendar', {}).get('rows', [])
        calendar = pd.DataFrame(rows)
        self.calendars.append(calendar)
        return calendar

def GetExDividendWithPayment(date):
    month_calendar = DividendCalendar(date.year, date.month)
    concat_df = month_calendar.get_dividends(date.day)
    
    if concat_df.empty or 'companyName' not in concat_df:
        return []
    
    concat_df['exTime'] = pd.to_datetime(concat_df['dividend_Ex_Date']).dt.date
    concat_df = concat_df[(concat_df['exTime'] == date) & (~concat_df['payment_Date'].str.contains("N/A"))]
    concat_df = concat_df[concat_df['payment_Date'] != '1/01/0001']
    concat_df['payDate'] = pd.to_datetime(concat_df['payment_Date']).dt.date
    concat_df['dividend_Rate'] = concat_df['dividend_Rate'].astype(float)
    return concat_df[['symbol', 'dividend_Rate', 'payDate']].to_numpy()

if __name__ == '__main__':
    np_arr = GetExDividendWithPayment(datetime.date(2024, 8, 29))
    print(np_arr)
