import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
rootPath = "..";import sys;sys.path.append(rootPath)
from modules.csvDump import DumpDict, LoadDict

BASE_URL = "https://nikkeiyosoku.com/data/?up_down_ratio_chart"
headers = {
    'User-Agent': generate_user_agent()
}

params = {}

def GetUpDownRatio():
    try:
        response = requests.get(f'{BASE_URL}', headers=headers, params=params)
        return response.json()["騰落レシオ"]
    except: return []

if __name__ == '__main__':
    upDownRatio = GetUpDownRatio()
    print(upDownRatio)


