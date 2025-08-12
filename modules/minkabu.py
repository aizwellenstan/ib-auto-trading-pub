import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
from collections import defaultdict
import json

headers = {
    
}

def GetPrice(ticker):
    try:
        s = requests.Session()
        r1 = s.get(f"https://minkabu.jp/current_price.json?codes={ticker}", headers=headers)
        data = json.loads(r1.text)
        data = data["items"][0]
        print(ticker, data["at"])
        res = float(data["price"])
        return res, data["at"]
    except:
        return 0
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

if __name__ == '__main__':
    GetPrice("9101")