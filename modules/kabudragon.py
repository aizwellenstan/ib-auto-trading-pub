import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import pandas as pd

headers = {
    'User-Agent': generate_user_agent()
}

params = {}

# https://www.kabudragon.com/ranking/st/dekizou.html
def GetDekizou():
    try:
        response = requests.get(
            f'https://www.kabudragon.com/ranking/st/dekizou.html',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find_all('table')[3]
        df = pd.read_html(str(table))[0]
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(df)
        # for col in df.columns:
        #     print(col)
        df = df[['コード','前日比']]
        df = df.assign(Ticker=df['コード'].apply(lambda x: int(x) if str(x).isnumeric() else pd.NA))
        df = df[df['Ticker'].notna()]
        df = df.assign(Change=df['前日比'].apply(lambda x: int(x.replace('+', '') if '+' in x else '-' + x.replace('-', ''))))
        df = df[df['Change'] > 0]
        return list(df['コード'].values)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

if __name__ == '__main__':
    GetDekizou()