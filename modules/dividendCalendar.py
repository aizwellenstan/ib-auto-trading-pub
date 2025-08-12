rootPath = '..'
import sys
sys.path.append(rootPath)
import pandas as pd
import requests
import datetime
import calendar
from datetime import date, timedelta
from modules.businessday import GetNextBusinessDay
from user_agent import generate_user_agent

# https://www.nasdaq.com/market-activity/dividends
class dividend_calendar:
    #class attributes 
    calendars = [] 
    url = 'https://api.nasdaq.com/api/calendar/dividends'
    hdrs =  {'Accept': 'application/json, text/plain, */*',
                #  'DNT': "1",
                 'Origin': 'https://www.nasdaq.com/',
                 'Sec-Fetch-Mode': 'cors',
                 'User-Agent': generate_user_agent()}
    def __init__(self, year, month):
        '''
        Parameters
        ----------
        year : year int
        month : month int
        
        Returns
        -------
        Sets instance attributes for year and month of object.
        
        '''
        #instance attributes
        self.year = int(year)
        self.month = int(month)
     
    def date_str(self, day):
        date_obj = datetime.date(self.year, self.month, day)
        date_str = date_obj.strftime(format='%Y-%m-%d')     
        return date_str
    def scraper(self, date_str):
        ''' 
        Scrapes JSON object from page using requests module.
        
        Parameters
        - - - - - 
        url : URL string
        hdrs : Header information
        date_str: string in yyyy-mm-dd format
            
        Returns
        - - - -
        dictionary : Returns a JSON dictionary at a given URL.
        
        '''
        # params = {'date': date_str}
        # print(params)
        page=requests.get(self.url+'?date='+date_str,headers=self.hdrs)
        dictionary = page.json()
        return dictionary
    
    def dict_to_df(self, dicti):
        ''' 
        Converts the JSON dictionary into a pandas dataframe
        Appends the dataframe to calendars class attribute         
        
        Parameters
        ----------
        dicti : Output from the scraper method as input.
        
        Returns
        -------
        calendar : Dataframe of stocks with that exdividend date
        
        Appends the dataframe to calendars class attribute
        
        If the date is formatted correctly, it will append a 
        dataframe to the calendars list (class attribute).  
        Otherwise, it will return an empty dataframe.         
        '''
        
        rows = dicti.get('data').get('calendar').get('rows')
        calendar = pd.DataFrame(rows)
        self.calendars.append(calendar)
        return calendar
   
            
    def calendar(self, day):
        '''
        Combines the scrape and dict_to_df methods
        
        Parameters
        ----------
        day : day of the month as string or number.
        
        Returns
        -------
        dictionary : Returns a JSON dictionary with keys 
        dictionary.keys() => data, message, status
        
        Next Levels: 
        dictionary['data'].keys() => calendar, timeframe
        dictionary['data']['calendar'].keys() => headers, rows
        dictionary['data']['calendar']['headers'] => column names
        dictionary['data']['calendar']['rows'] => dictionary list

        '''
        day = int(day)
        date_str = self.date_str(day)
        dictionary = self.scraper(date_str)
        dictionary = self.dict_to_df(dictionary)          
        return dictionary

def GetExDividend(day=1):
    tomorrow = GetNextBusinessDay(day)
    year = tomorrow.year
    month = tomorrow.month
    print(tomorrow)
    
#get number of days in month
#     days_in_month = calendar.monthrange(year, month)[1]
# #create calendar object    
    month = dividend_calendar(year, month)
# #define lambda function to iterate over list of days     
#     function = lambda days: month.calendar(days)
    
# #define list of ints between 1 and the number of days in the month
#     iterator = list(range(1, days_in_month+1))
# #Scrape calendar for each day of the month                    
#     objects = list(map(function, iterator))
#concatenate all the calendars in the class attribute
    # concat_df = pd.concat(month.calendars)
    concat_df = month.calendar(tomorrow.day)
    
#Drop any rows with missing data
    drop_df = concat_df.dropna(how='any')
    
#set the dataframe's row index to the company name
    if 'companyName' not in drop_df: return []
    final_df = drop_df.set_index('companyName')
    final_df = final_df.assign(exTime = pd.to_datetime(final_df['dividend_Ex_Date']).dt.date)
    final_df = final_df.loc[final_df['exTime'] == tomorrow]
    print(final_df)
    df = final_df[['symbol','dividend_Ex_Date']]
    return df['symbol'].values

def GetExDividendByDate(date):
    year = date.year
    month = date.month
    month = dividend_calendar(year, month)
    concat_df = month.calendar(date.day)
    drop_df = concat_df.dropna(how='any')
    if 'companyName' not in drop_df: return []
    final_df = drop_df.set_index('companyName')
    final_df = final_df.assign(exTime = pd.to_datetime(final_df['dividend_Ex_Date']).dt.date)
    final_df = final_df.loc[final_df['exTime'] == date]
    df = final_df[['symbol','dividend_Ex_Date']]
    return df['symbol'].values

def GetExDividendWithPayment(date):
    year = date.year
    month = date.month
    month = dividend_calendar(year, month)
    concat_df = month.calendar(date.day)
    drop_df = concat_df.dropna(how='any')
    if 'companyName' not in drop_df: return []
    final_df = drop_df.set_index('companyName')
    final_df = final_df.assign(exTime = pd.to_datetime(final_df['dividend_Ex_Date']).dt.date)
    final_df = final_df.loc[final_df['exTime'] == date]
    final_df = final_df[~final_df['payment_Date'].str.contains("N/A")]
    final_df = final_df.assign(payDate = pd.to_datetime(final_df['payment_Date']).dt.date)
    df = final_df[['symbol','payDate']]
    return df.to_numpy()

def GetExDividendPaymentByDate(date):
    year = date.year
    month = date.month
    month = dividend_calendar(year, month)
    concat_df = month.calendar(date.day)
    drop_df = concat_df.dropna(how='any')
    if 'companyName' not in drop_df: return []
    final_df = drop_df.set_index('companyName')
    final_df = final_df.assign(exTime = pd.to_datetime(final_df['dividend_Ex_Date']).dt.date)
    final_df = final_df.loc[final_df['exTime'] == date]
    df = final_df[['symbol','payment_Date']]
    return df

import requests
from user_agent import generate_user_agent
import pandas as pd
import sys

headers = {
    'User-Agent': generate_user_agent(),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,em;q=0.5',
    'Origin': 'https://www.nasdaq.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nasdaq.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'smae-site',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers', 
}

def GetExDividendNp(days=1):
    date = GetNextBusinessDay(days)
    print(date)
    try:
        response = requests.get(
            f'https://api.nasdaq.com/api/calendar/dividends?date={date}',
            headers=headers).json()
        if response['status']['rCode'] == 200:
            data = response['data']
            df = pd.DataFrame(data['calendar']['rows'])
            df['dividend_Rate'] = df['dividend_Rate'].astype(float)
            df = df[~df['payment_Date'].str.contains("N/A")]
            # df['payment_Date'] = pd.to_datetime(df['payment_Date'],format='%m/%d/%Y')
            # df['payment_Date'] = df['payment_Date'].dt.strftime('%Y-%m-%d')
            df = df[['symbol', 'dividend_Rate']]
            return df.to_numpy()
        else: return []
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []


if __name__ == '__main__':
    # df = GetExDividendNp(13)
    # print(df)
    import datetime
    npArr = GetExDividendWithPayment(datetime.date(2022,4,20))
    print(npArr)