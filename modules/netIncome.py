import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np

headers = {
    'User-Agent': generate_user_agent()
}

params = {}

# https://www.tradingview.com/symbols/TSE-9101/financials-income-statement/net-income/
def GetNetincome():
    try:
        s = requests.Session()
        r1 = s.get("https://www.tradingview.com/financial/fundamentals_config/", headers=headers)
        # print(r1.cookies)
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        r2 = s.get("https://www.tradingview.com/symbols/TSE-9101/financials-income-statement/net-income/", headers=headers)
        soup = BeautifulSoup(r2.text, "lxml")
        # print(soup)
        # response = requests.get(
        #     f'https://www.tradingview.com/symbols/TSE-9101/financials-income-statement/net-income/',
        #     headers=headers,params=params)
        # soup = BeautifulSoup(response.text, "lxml")
        # tables = soup.findAll('div')
        # print(tables[1])
        divs = soup.findAll("div", class_="container-XBlFAtm7")
        print(divs)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    GetNetincome()