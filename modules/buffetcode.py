import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
from collections import defaultdict

headers = {
    'User-Agent': generate_user_agent(),
}

def GetMainHolder(symbol):
    s = requests.Session()
    r1 = s.get(f"https://www.buffett-code.com/company/{symbol}/mainshareholder", headers=headers)
    # print(r1.cookies)
    cookies = requests.utils.dict_from_cookiejar(r1.cookies)
    s.cookies.update(cookies)
    print(r1.text)

if __name__ == '__main__':
    GetMainHolder('9101')