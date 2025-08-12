import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
from collections import defaultdict
import numpy as np

headers = {
    
}

def GetSmillarCompany(ticker):
    try:
        s = requests.Session()
        r1 = s.get(f"https://kabuyoho.ifis.co.jp/index.php?id=100&action=tp1&sa=report&bcode={ticker}", headers=headers)
        soup = BeautifulSoup(r1.text, "lxml")
        div = soup.findAll("div",class_="block_end")[3]
        table = div.find("table")
        ths = table.findAll("th",class_="th_stock_comp")
        tickers = []
        for th in ths[1:]:
            a = th.find("a")
            tickers.append(a['href'][-4:])
        return tickers
    except:
        return []
    # print(r1.cookies)
    # cookies = requests.utils.dict_from_cookiejar(r1.cookies)
    # s.cookies.update(cookies)
    # r2 = s.get("https://jp.kabumap.com/servlets/kabumap/Action?SRC=common/kmTable/get_page_data", headers=headers)
    # # print(r2.cookies)
    # # print(r2.text)
    # # start_text = "{'Tables': ["
    # start_text = "'TD':[\n"
    # end_text = "\n,\n'TDCLASS':["

    # start_index = r2.text.find(start_text)
    # end_index = r2.text.find(end_text)

    # extracted_text = r2.text[start_index+7:end_index]
    # # print(extracted_text)
    # data = find_codetext_substrings(extracted_text)
    # # print(data)
    # # Grouping the dictionary by values
    # grouped_data = defaultdict(list)
    # for key, value in data.items():
    #     grouped_data[value].append(key)

    # # Printing the grouped dictionary
    # res = {}
    # for value, keys in grouped_data.items():
    #     # print(value, ":", keys)
    #     if len(keys) < 3: continue
    #     res[value] = keys
    # return res

def GetMokuhyoukabuka(symbol):
    try:
        response = requests.get(f'https://kabuyoho.ifis.co.jp/index.php?action=tp1&sa=report_top&bcode={symbol}', headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find_all('table')[2]
        td = table.find_all("td")[-1]
        return int(td.text.strip().split(" ")[0].replace(",",""))
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetKabukarange(symbol):
    try:
        response = requests.get(f'https://kabuyoho.ifis.co.jp/index.php?action=tp1&sa=report_pbr&bcode={symbol}', headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        print(soup)
        div = soup.find('div', class_='tb_stock_range')
        print(div)
        div = div.find_all('div')
        print(div)
        div = div.find_all('div')[1]
        table = div.find('table')
        tbody = table.find('tbody')
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                if i == 0:
                    data = td.text
                    data = data.strip().split(" ")[0].split("\n")[0].replace(",","")
                    data = round(np.float64(data), 1)
                    results.append(data)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    # GetSmillarCompany("7203")
    # GetMokuhyoukabuka("9101")
    npArr = GetKabukarange("2914")
    print(npArr)