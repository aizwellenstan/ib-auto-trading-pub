import json
from bs4 import BeautifulSoup
import sys
import pandas as pd
from user_agent import generate_user_agent
import requests
import urllib3
from lxml import html
import lxml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRE_VOLUME_URL = "https://finviz.com/quote.ashx?L&ty=c&ta=1&p=d"
NASDAQ_URL = "https://www.nasdaq.com/market-activity/stocks/{}/pre-market"
STOCK_URL = "https://finviz.com/quote.ashx"
VOLUME_URL = "https://finviz.com/screener.ashx?v=320&s=ta_unusualvolume"
NEWS_URL = "https://finviz.com/news.ashx"
CRYPTO_URL = "https://finviz.com/crypto_performance.ashx"
STOCK_PAGE = {}


def http_request_get(
    url, session=None, payload=None, parse=True, user_agent=generate_user_agent()
):

    if payload is None:
        payload = {}

    try:
        if session:
            content = session.get(
                url,
                params=payload,
                verify=False,
                headers={"User-Agent": user_agent},
            )
        else:
            content = requests.get(
                url,
                params=payload,
                verify=False,
                headers={"User-Agent": user_agent},
            )

        content.raise_for_status()  # Raise HTTPError for bad requests (4xx or 5xx)
        if parse:
            return html.fromstring(content.text), content.url
        else:
            return content.text, content.url
    except:
        print("time out")


def get_page(ticker):
    global STOCK_PAGE

    if ticker not in STOCK_PAGE:
        STOCK_PAGE[ticker], _ = http_request_get(
            url=STOCK_URL, payload={"t": ticker}, parse=True
        )

def GetStockData(ticker):
    try:
        data = {}
        get_page(ticker)
        page_parsed = STOCK_PAGE[ticker]
        res = page_parsed.cssselect('table[class="snapshot-table2"]')
        if(len(res) > 0):
            table = res[0]
            for row in table:
                arr=row.xpath("td//text()")
                for i in range(0, len(arr), 2):
                    data[arr[i]]=arr[i+1]
        return data
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def GetOptionable(ticker):
    try:
        data = GetStockData(ticker)
        optionable = data['Optionable']
        if optionable == 'Yes': return True
        return False
    except Exception as e:
        return False

def get_insider(ticker):
    try:
        data = []
        get_page(ticker)
        page_parsed = STOCK_PAGE[ticker]
        res = page_parsed.cssselect('table[class="body-table"]')
        if(len(res) > 0):
            table = res[0]
            headers = table[0].xpath("td//text()")
            data = [dict(zip(headers, row.xpath("td//text()")))
                    for row in table[1:]]
        return data
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def get_all_unusual_volume():
    page_parsed = http_request_get(
        url=VOLUME_URL, parse=True
    )
    data, url = page_parsed

    select = data.cssselect('select[class="pages-combo"]')
    options = select[0].cssselect('option')

    stocks = []

    for opt in options:
        page_parsed = http_request_get(
            url=VOLUME_URL, payload={"r": opt.attrib['value']}, parse=True
        )
        data, url = page_parsed

        tickers = data.cssselect('a[class="tab-link"]')

        for ticker in tickers:
            if str(ticker.text).isupper():
                stocks.append(ticker.text)
    
    return stocks

def get_unusual_volume(ticker):
    page_parsed = http_request_get(
        url=VOLUME_URL, payload={"t": ticker}, parse=True
    )
    data, url = page_parsed

    td = data.cssselect('td[class="snapshot-td"]')
    if len(td) > 1:
        return True
    return False


def to_html(elm, encoding='utf-8', method='html'):
    return lxml.etree.tostring(elm, encoding=encoding, method=method).decode(encoding)


def get_pre_volume(ticker):
    page_parsed = http_request_get(
        url=PRE_VOLUME_URL, payload={"t": ticker}, parse=True
    )
    data, url = page_parsed

    b = data.cssselect('b')
    print(b[76].text)
    # if len(td) > 1: return True
    # return False

s = requests.Session()

def get_df(url):
    try:
        page_parsed = http_request_get(
            url=url, parse=True
        )
        data, url = page_parsed
        data = json.loads(data.text)
        for key, value in data['data'].items():
            if key != 'Period End Date':  # Skip 'Period End Date' column
                cleaned_values = []
                for val in value:
                    if isinstance(val, str):
                        cleaned_val = val.replace(',', '')
                        try:
                            cleaned_values.append(int(cleaned_val))  # Convert to float to handle decimals
                        except:
                            cleaned_values.append(cleaned_val)
                    else:
                        cleaned_values.append(val)
                data['data'][key] = cleaned_values
        df = pd.DataFrame(data['data'])
        df['da'] = pd.to_datetime(df['Period End Date'], format='%m/%d/%Y')
        return df
    except: return []

def GetBSQ(symbol):
    url = f'https://finviz.com/api/statement.ashx?t={symbol}&so=F&s=BQ'
    df = get_df(url)
    if len(df) < 1: return[]
    # Drop the 'Period End Date' column after setting it as index, if needed
    try:
        df.drop(columns=['Period End Date','Full-Time Employees'], inplace=True)
    except:
        df.drop(columns=['Period End Date'], inplace=True)
    return df

def GetCFQ(symbol):
    url = f'https://finviz.com/api/statement.ashx?t={symbol}&so=F&s=CQ'
    df = get_df(url)
    if len(df) < 1: return[]
    # Drop the 'Period End Date' column after setting it as index, if needed
    df.drop(columns=['Period End Date', 'Period Length'], inplace=True)
    return df

def GetISQ(symbol):
    url = f'https://finviz.com/api/statement.ashx?t={symbol}&so=F&s=IQ'
    df = get_df(url)
    if len(df) < 1: return[]
    # Drop the 'Period End Date' column after setting it as index, if needed
    df.drop(columns=['Period End Date', 'Period Length'], inplace=True)
    return df

if __name__ == '__main__':
    # cq = GetCFQ("NVDA")
    # print(cq)
    bq = GetISQ("AAPL")
    print(bq)
# get_all_unusual_volume()
# get_pre_volume("AAPL")
# insider = get_insider('AAPL')
# df = pd.DataFrame(insider)
# df.to_csv('./csv/insider.csv')

# optionalbe = GetOptionable('AAPL')
# print(optionalbe)
