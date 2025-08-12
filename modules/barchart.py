import requests
from urllib.parse import unquote
import pandas as pd

geturl=r'https://www.barchart.com/stocks/quotes/AAPL%7C20210423%7C126.00C/price-history/'


getheaders={

    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    "referer":"https://www.barchart.com/stocks/quotes/AAPL%7C20210423%7C126.00C/price-history/historical",
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }



s=requests.Session()
r=s.get(geturl, headers=getheaders)


headers={
    'accept': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',

    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    'x-xsrf-token': unquote(unquote(s.cookies.get_dict()['XSRF-TOKEN']))


}





def GetQuotes():
    payload={

        "symbol":"AAPL|20210423|126.00C",
        "fields":"tradeTime.format(m\/d\/Y),openPrice,highPrice,lowPrice,lastPrice,priceChange,percentChange,volume,openInterest,impliedVolatility,symbolCode,symbolType",
        "type":"eod",
        "orderBy":"tradeTime",
        "orderDir":"desc",
        "limit":65,
        #"meta":"field.shortName,field.type,field.description",
        'raw': '1'


    }
    apiurl=r'https://www.barchart.com/proxies/core-api/v1/quotes/get'
    r=s.get(apiurl,params=payload,headers=headers)
    j=r.json()
    print(j)

def GetHoldings(ticker):
    payload = {
        "composite":ticker,
        "fields":"symbol,symbolName,percent,sharesHeld,symbolCode,symbolType,lastPrice,dailyLastPrice",
        "orderBy":"percent",
        "orderDir":"desc",
        "meta":"field.shortName,field.type,field.description",
        "page":"1",
        "raw":"1",
    }
    r = s.get("https://www.barchart.com/proxies/core-api/v1/EtfConstituents?composite={ticker}&fields=symbol%2CsymbolName%2Cpercent%2CsharesHeld%2CsymbolCode%2CsymbolType%2ClastPrice%2CdailyLastPrice&orderBy=percent&orderDir=desc&meta=field.shortName%2Cfield.type%2Cfield.description&page=1&raw=1", params=payload, headers=headers)
    data = r.json()["data"]
    res = []
    for d in data:
        res.append(d['raw'])
    df = pd.DataFrame(res)
    df = df[['symbol', 'percent']]
    npArr = df.to_numpy()
    return npArr

def GetOiChangeStock():
    payload = {
        "fields":"symbol,baseSymbol,baseLastPrice,baseSymbolType,symbolType,strikePrice,expirationDate,daysToExpiration,bidPrice,midpoint,askPrice,lastPrice,volume,openInterest,openInterestChange,volatility,tradeTime,symbolCode,hasOptions",
        "orderBy":"openInterestChange",
        "baseSymbolTypes":"stock",
        "orderDir":"desc",
        "limit": "14975",
        "meta":"field.shortName,field.type,field.description",
        "hasOptions": "true",
    }
    r = s.get("https://www.barchart.com/proxies/core-api/v1/options/get", params=payload, headers=headers)
    data = r.json()["data"]
    df = pd.DataFrame(data)
    npArr = df.to_numpy()
    return npArr

def GetOiChangeEtf():
    payload = {
        "fields":"symbol,baseSymbol,baseLastPrice,baseSymbolType,symbolType,strikePrice,expirationDate,daysToExpiration,bidPrice,midpoint,askPrice,lastPrice,volume,openInterest,openInterestChange,volatility,tradeTime,symbolCode,hasOptions",
        "orderBy":"openInterestChange",
        "baseSymbolTypes":"etf",
        "orderDir":"desc",
        "limit": "14988",
        "meta":"field.shortName,field.type,field.description",
        "hasOptions": "true",
    }
    r = s.get("https://www.barchart.com/proxies/core-api/v1/options/get", params=payload, headers=headers)
    data = r.json()["data"]
    df = pd.DataFrame(data)
    npArr = df.to_numpy()
    return npArr
#     try:
#         s = requests.Session()
#         r1 = s.get(f"https://www.barchart.com/stocks/quotes/{ticker}/constituents?page=all", headers=headers)
#         # print(r1.cookies)
#         cookies = requests.utils.dict_from_cookiejar(r1.cookies)
#         s.cookies.update(cookies)
#         r2 = s.get("https://www.barchart.com/proxies/core-api/v1/EtfConstituents?composite={ticker}&fields=symbol%2CsymbolName%2Cpercent%2CsharesHeld%2CsymbolCode%2CsymbolType%2ClastPrice%2CdailyLastPrice&orderBy=percent&orderDir=desc&meta=field.shortName%2Cfield.type%2Cfield.description&page=1&raw=1", headers=headers).json()
#         print(r2)
#         # if response['status']['rCode'] == 200:
#         #     data = response['data']
#         # else: return []
#     except Exception as e:
#         print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

# if __name__ == '__main__':
#     GetHoldings("QQQ")