import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
rootPath = "..";import sys;sys.path.append(rootPath)
from modules.csvDump import DumpDict, LoadDict
import pandas as pd

import requests

url = 'https://www.interactivebrokers.co.uk/webrest/search/products-by-filters'
headers = {
    'authority': 'www.interactivebrokers.co.uk',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json;charset=UTF-8',
    'cookie': 'x-sess-uuid=0.a4d7d217.1722138007.3625786; x-sess-uuid=0.a4d7d217.1722138042.36291f7; PHPSESSID=fm5ua8qpng55jt2ld9s03ikk2j; IB_QD=0; IB_QD_CFD=0; IB_PRIV_PREFS=1%7C1%7C1; AKA_A2=A',
    'origin': 'https://www.interactivebrokers.co.uk',
    'referer': 'https://www.interactivebrokers.co.uk/en/trading/products-exchanges.php',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Opera";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
}

def GetCfd(pageNumber = 1):
    payload = {
        'pageNumber': pageNumber,
        'pageSize': '100',
        'sortField': 'symbol',
        'sortDirection': 'asc',
        'productCountry': ['US'],
        'productSymbol': '',
        'newProduct': 'all',
        'productType': ['CFD'],
        'domain': 'uk'
    }

    response = requests.post(url, headers=headers, json=payload)
    return  response.json()

data = GetCfd()
count = data['productCount']
res = []
res.append(data['products'])
for i in range(2, int(count/100)+2):
    data = GetCfd(i)
    res.append(data['products'])
df = pd.DataFrame(res)
df.to_csv(f"{rootPath}/data/ib_cfd_us2.csv")

# table_data = get_data(US_BASE_URL, 999)
# df = pd.DataFrame(table_data[1:], columns=table_data[0])
# # df.to_csv(f"{rootPath}/data/ib_cfd_us.csv")
# df.to_csv(f"{rootPath}/data/ib_cfd_us2.csv")

# table_data = get_data(JP_BASE_URL, 22)
# df = pd.DataFrame(table_data[1:], columns=table_data[0])
# df.to_csv(f"{rootPath}/data/ib_cfd_jp.csv")