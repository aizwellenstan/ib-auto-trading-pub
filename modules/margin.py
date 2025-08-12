import requests
import pandas as pd
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys

headers = {
    'User-Agent': generate_user_agent(),
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'smae-site',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers', 
}

params = {
}

import json
from pandas import json_normalize
def get_data_from_source(src):
    # スクレイピングする
    soup = BeautifulSoup(src, features='lxml')
    # print(soup)
    try:
        info = []
        script = soup.find_all("script")[7]
        data = script.string.split("window.__PRELOADED_STATE__ = ",1)[1]
        data = json.loads(data)['mainStocksMarginHistory']['histories']
        df = json_normalize(data)
        df = df.replace(',','', regex=True)
        df = df.astype({
            'marginTransactionSell':'int',
            'marginTransactionBuy':'int',
            'marginTransactionSellFluctuation':'int',
            'marginTransactionBuyFluctuation':'int',
            'marginCreditMagnification': 'float'
        })
        npArr = df.to_numpy()
        # 売残 買残 売残増減 買残増減 信用倍率 日付
        return npArr
        # table = soup.find("table", class_="boardFin")
        # print(table)
        # if table:
        #     elems = table.find_all("tr")
 
        #     for elem in elems:
        #         td_tags = elem.find_all("td")
 
        #         if len(td_tags) > 0:
        #             row_info = []
        #             tmp_counter = 0
        #             for td_tag in td_tags:
        #                 tmp_text = td_tag.text
 
        #                 if tmp_counter == 0:
        #                     # 年月日
        #                     tmp_text = tmp_text
        #                 else:
        #                     tmp_text = extract_num(tmp_text)
 
        #                 row_info.append(tmp_text)
        #                 tmp_counter = tmp_counter + 1
 
        #             info.append(row_info)
 
        # return info
 
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# https://finance.yahoo.co.jp/quote/9101.T/margin
# https://info.finance.yahoo.co.jp/history/margin/?code=1301.T&sy=2020&sm=11&sd=16&ey=2021&em=2&ed=14
def GetMargin(symbol):
    try:
        response = requests.get(
            f'https://finance.yahoo.co.jp/quote/{symbol}.T/margin',
            headers=headers,params=params)
        info = get_data_from_source(response.text)
        return info
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def get_us_source(src):
    # スクレイピングする
    soup = BeautifulSoup(src, features='lxml')
    # print(soup)
    try:
        info = []
        script = soup.find_all("script")[7]
        data = script.string.split("window.__PRELOADED_STATE__ = ",1)[1]
        data = json.loads(data)['mainStocksPriceBoard']['priceBoard']['usStock']
        ticker = ""
        if data != None:
            data = data['usLink']
            ticker = data.split('/')[-1]
        return ticker
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetUSStock(symbol):
    try:
        response = requests.get(
            f'https://finance.yahoo.co.jp/quote/{symbol}.T/margin',
            headers=headers,params=params)
        info = get_us_source(response.text)
        return info
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# info = GetUSStock('7203')
# print(info)