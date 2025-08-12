import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
rootPath = "..";import sys;sys.path.append(rootPath)
from modules.csvDump import DumpDict, LoadDict

BASE_URL = "https://irbank.net"
headers = {
    'User-Agent': generate_user_agent()
}

params = {}

s = requests.Session()

# https://karauri.net/6315/sokuhou/?date=2024-04-25
def GetSokuhou(ticker, d=''):
    try:
        url = f'https://karauri.net/{ticker}/sokuhou/'
        if d != '': url += f'?date={d}'
        response = s.get(
            url,
            headers=headers,params=params)
        soup = BeautifulSoup(response.text)
        table = soup.find('table', id="sort")
        tbody = table.find('tbody')
        res = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                if i in [1]: continue
                elif i in [2, 3, 4, 5]:
                    e = td.get_text(strip=True, separator='\n').splitlines()
                    multipy = 1
                    symbol = '+'
                    if '-' in e[1]: 
                        symbol = '-'
                        multipy = -1
                    rowData.append(int(e[0].replace("株",'').replace(',','')))
                    rowData.append(int(e[1].replace(',','').replace(symbol,''))*multipy)
                elif i in [6]:
                    rowData.append(float(td.text.replace('倍','')))
                else:
                    rowData.append(td.text)
            if len(rowData) < 1: continue
            res.append(rowData)
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    res = GetSokuhou("6315")
    print(res)
