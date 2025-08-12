import requests
import pandas as pd
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup

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

# https://finance.yahoo.com/calendar/earnings?symbol=aapl
def GetEarnings(symbol):
    try:
        response = requests.get(
            f'https://finance.yahoo.com/calendar/earnings?symbol={symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        # res = soup.find_all('div', {'id': 'Lead-7-CalTable-Proxy'})
        res = soup.find(text='Reported EPS')
        print(res)

        # for table in tables:
        #     print(table)
        # riron_string = soup.find_all(text=re.compile('理論株価')) 
        # rironkabuka = 0
        # for s in riron_string:
        #     if rironkabuka > 0: break
        #     for c in s.parent.next_siblings:
        #         if c.name == 'div' and 'riron' in c['class']:
        #             rironkabuka = int(c.text.replace(",", ""))
        #             break
        # return rironkabuka
    except:
        return 0
