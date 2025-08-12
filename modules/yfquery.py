import requests
import pandas as pd
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import numpy as np

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

# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=incomeStatementHistoryQuarterly
def GetCrumb():
    s = requests.Session()
    r1 = s.get(
        f'https://fc.yahoo.com',
        headers=headers,params=params)
    cookies = requests.utils.dict_from_cookiejar(r1.cookies)
    s.cookies.update(cookies)
    r2 = s.get(
        f'https://query2.finance.yahoo.com/v1/test/getcrumb',
        headers=headers,params=params)
    crumb = r2.text
    return s, crumb
def GetNetIncome(symbol):
    symbol = symbol.replace("-",".")
    try:
        int(symbol)
        symbol += ".T"
    except: pass
    try:
        s = requests.Session()
        r1 = s.get(
            f'https://fc.yahoo.com',
            headers=headers,params=params)
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        r2 = s.get(
            f'https://query2.finance.yahoo.com/v1/test/getcrumb',
            headers=headers,params=params)
        crumb = r2.text
        response = s.get(
            f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?formatted=true&modules=incomeStatementHistoryQuarterly&crumb={crumb}',
            headers=headers,params=params)
        return response.json()
    except:
        return 0

def GetInventory(symbol):
    symbol = symbol.replace("-",".")
    try:
        int(symbol)
        symbol += ".T"
    except: pass
    try:
        s = requests.Session()
        r1 = s.get(
            f'https://fc.yahoo.com',
            headers=headers,params=params)
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        r2 = s.get(
            f'https://query2.finance.yahoo.com/v1/test/getcrumb',
            headers=headers,params=params)
        crumb = r2.text
        response = s.get(
            f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?formatted=true&modules=balanceSheetHistoryQuarterly&crumb={crumb}',
            headers=headers,params=params)
        return response.json()
    except:
        return 0

# https://yahooquery.dpguthrie.com/guide/ticker/modules/
def GetBalanceSheetIncomeStatement(symbol):
    symbol = symbol.replace("-",".")
    try:
        int(symbol)
        symbol += ".T"
    except: pass
    try:
        s = requests.Session()
        r1 = s.get(
            f'https://fc.yahoo.com',
            headers=headers,params=params)
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        r2 = s.get(
            f'https://query2.finance.yahoo.com/v1/test/getcrumb',
            headers=headers,params=params)
        crumb = r2.text
        response = s.get(
            f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=incomeStatementHistoryQuarterly,balanceSheetHistoryQuarterly&crumb={crumb}',
            headers=headers,params=params)
        res = response.json()
        res = res["quoteSummary"]["result"][0]
        balanceSheetQ = res["balanceSheetHistoryQuarterly"]["balanceSheetStatements"]
        incomeStatementQ = res["incomeStatementHistoryQuarterly"]["incomeStatementHistory"]
        return balanceSheetQ, incomeStatementQ
    except:
        return [], []

def GetCapex(symbol):
    symbol = symbol.replace("-",".")
    try:
        int(symbol)
        symbol += ".T"
    except: pass
    try:
        s = requests.Session()
        r1 = s.get(
            f'https://fc.yahoo.com',
            headers=headers,params=params)
        cookies = requests.utils.dict_from_cookiejar(r1.cookies)
        s.cookies.update(cookies)
        r2 = s.get(
            f'https://query2.finance.yahoo.com/v1/test/getcrumb',
            headers=headers,params=params)
        crumb = r2.text
        response = s.get(
            f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?formatted=true&modules=earningsHistory&events=history&crumb={crumb}',
            headers=headers,params=params)
        res = response.json()
        print(res)
        return res
    except:
        return []
