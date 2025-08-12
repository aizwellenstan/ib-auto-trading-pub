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

# https://www.investing.com/search/?q=8887
def GetEPS(ticker):
    try:
        response = requests.get(
            f'https://www.investing.com/search/?q={ticker}',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        # table = soup.find('table', id="tbc")
        # tbody = table.find('tbody')
        print(soup)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    npArr = GetEPS('8887')
    print(npArr)