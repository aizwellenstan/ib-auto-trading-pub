import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
rootPath = "..";import sys;sys.path.append(rootPath)
from modules.csvDump import DumpDict, LoadDict

headers = {
    'User-Agent': generate_user_agent()
}

params = {}

def GetPts(ticker):
    try:
        response = requests.get(
            f'https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETsiR002Control&_PageID=DefaultPID&_ActionID=DefaultAID&i_stock_sec={ticker}&exchange_code=TKY',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find_all('table', class_="tbl690")[1]
        tbody = table.find('tbody')
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                if len(results) > 4: break
                tdData = td.text
                number = tdData.split("\xa0")[0].replace(",","")
                data = round(np.float64(number), 1)
                results.append(data)
        return results
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == "__main__":
    npArr = GetPts("9101")
    print(npArr)
