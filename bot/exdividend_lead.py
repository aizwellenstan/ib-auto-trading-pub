rootPath = ".."
import sys
sys.path.append(rootPath)

from modules.data import GetNpDataVolumeWeekday

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetClose
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
import pickle
import math
from modules.dividendCalendar import GetExDividendNp
from modules.normalizeFloat import NormalizeFloat
import csv
import pandas as pd

from modules.trade.vol import GetVolSlTp

import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(29)
total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def load_csv_to_dict(filename):
    result_dict = {}
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            symbol = row['Symbol']
            del row['Symbol']
            result_dict[symbol] = list(row.values())
    return result_dict

csvPath = f"{rootPath}/data/LeadUSTrade.csv"
result_dict = load_csv_to_dict(csvPath)
closeDict = GetClose()

dividendList = []
result_list = []
for i in range(1, 90):
    dividendList = GetExDividendNp(i)
    print(dividendList,i)
    for symbol, div in dividendList:
        if symbol not in closeDict: continue
        if symbol not in result_dict: continue
        op = closeDict[symbol]
        vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
        if (tp - op) * vol < 2: continue
        dividendReceived = div * vol
        if dividendReceived < 2: continue
        result_list.append([symbol, dividendReceived])
    if len(result_list) > 0: break
result_list.sort(key=lambda x: x[1], reverse=True)
resDict = {}
for symbol, div in result_list:
    resDict[symbol] = div

exDividendPath = f'{rootPath}/data/ExDividend.csv'
df = pd.DataFrame()
df['Symbol'] = resDict.keys()
df['Divdend'] = resDict.values()
df.to_csv(exDividendPath)
