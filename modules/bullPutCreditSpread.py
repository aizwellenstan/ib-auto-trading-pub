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

URL = "https://www.barchart.com/options/put-spreads/bull-put?orderBy=maxProfitPercent&orderDir=desc"
API_URL="https://www.barchart.com/api/v1/options/bull-puts-spread?orderBy=maxProfitPercent&orderDir=desc&fields=baseSymbol%2CbaseSymbolType%2CbaseLastPrice%2CmaxProfit%2CmaxProfitPercent%2CmaxLoss%2CbreakEven%2CbreakEvenProbability%2CexpirationDate%2CstrikePriceLeg1%2CbidPriceLeg1%2CstrikePriceLeg2%2CaskPriceLeg2%2CexpirationType%2Clegs%2CexpirationDate%2CsymbolCode%2CsymbolType%2ChasOptions&page=1&limit=20&hasOptions=true&raw=1&meta=field.shortName%2Cfield.type%2Cfield.description&between(daysToExpiration,0,60)&in(expirationType,(monthly))&in(exchange,(AMEX,NYSE,NASDAQ))&in(baseSymbolType,(1))&between(volumeLeg1,100,)&between(openInterestLeg1,500,)&between(moneynessLeg1,-10,0)&between(breakEvenProbability,25,)&between(volumeLeg2,100,)&between(openInterestLeg2,500,)&gt(bidPriceLeg1,0.05)&gt(askPriceLeg2,0.05)"

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

def to_html(elm, encoding='utf-8', method='html'):
    return lxml.etree.tostring(elm, encoding=encoding, method=method).decode(encoding)

def clean_str(print_str):
    cleanArr = ['\xa0','\xa9']
    for i in cleanArr:
        print_str = print_str.replace(i, '')
    return print_str

def get_page():
    page_parsed, _ = http_request_get(
        url=URL, parse=False
    )
    soup = BeautifulSoup(page_parsed, "html.parser")

    # HTML全体を表示する
    # print(soup)

    data = soup.find(id="bc-dynamic-config")
    # data = soup.find(class_="bc-datatable")
    # body = soup.find("body")
    data = str(data).split(">",1)[1]
    data = str(data).split("</script>",1)[0]
    # data = '"{0}"'.format(data)
    data = json.loads(data)
    # print(data)
    for key, value in data.items() :
        print(key, value) 

def get_data():
    page_parsed, _ = http_request_get(
        url=URL, parse=False
    )
    print(page_parsed)

get_data()

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

def get_pre_volume(ticker):
    page_parsed = http_request_get(
        url=PRE_VOLUME_URL, payload={"t": ticker}, parse=True
    )
    data, url = page_parsed

    b = data.cssselect('b')
    print(b[76].text)
    # if len(td) > 1: return True
    # return False

# get_all_unusual_volume()
# get_pre_volume("AAPL")
# insider = get_insider('AAPL')
# df = pd.DataFrame(insider)
# df.to_csv('./csv/insider.csv')

# optionalbe = GetOptionable('AAPL')
# print(optionalbe)
