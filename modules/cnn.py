import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import requests
from user_agent import generate_user_agent
import json
import pandas as pd
import numpy as np

headers = {
    'User-Agent': generate_user_agent()
}

params = {}

s = requests.Session()

def GetData():
    url = 'https://production.dataviz.cnn.io/index/fearandgreed/graphdata'
    response = s.get(
            f'{url}',
            headers=headers,params=params)
    data = response
    data = json.loads(data.text)
    return data

def SaveDf(col = "fear_and_greed_historical"):
    data = GetData()
    fear_and_greed_historical = data[col]["data"]
    df = pd.DataFrame(fear_and_greed_historical)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    # df.to_parquet(fPath)
    return df

def GetFear():
    df = SaveDf()
    df = df.head(len(df)-1)
    data = df['y'].values.tolist()
    return np.array(data)

def GetStrength(col="safe_haven_demand"):
    df = SaveDf(col)
    # df = df.head(len(df)-1)
    data = df['y'].values.tolist()
    return np.array(data)

if __name__ == '__main__':
    # data = GetFear()
    data = GetStrength()