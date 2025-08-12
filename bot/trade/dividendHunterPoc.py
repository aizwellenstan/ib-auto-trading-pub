rootPath = '../..'
import sys
sys.path.append(rootPath)
from modules.trade.vol import GetVol
from modules.dict import take
from modules.aiztradingview import GetClose
import pandas as pd
import math
from typing import NamedTuple
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetADR
from modules.discord import Alert
import csv
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(28)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01
positions = ibc.GetAllPositions()

def HandleBuy(symbol, tp, rr):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    op = NormalizeFloat(op, 0.01)
    if op > ask - 0.01: op = ask - 0.01
    sl = op - (tp - op) / rr
    sl = NormalizeFloat(sl, 0.01)
    vol = GetVol(
        total_cash,avalible_cash,op,sl,'USD'
    )
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        if vol > 1:
            if (tp - op) * vol < 2: return 0
            print(symbol, vol, op, sl, tp)
            ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
            return vol
    return 0

def load_csv_to_dict(filename):
    result_dict = {}
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            symbol = row['Symbol']
            del row['Symbol']
            result_dict[symbol] = list(row.values())
    return result_dict

def main():
    csvPath = f"{rootPath}/data/ExDividendPoc.csv"
    result_dict = load_csv_to_dict(csvPath)
    for symbol, attr in result_dict.items():
        poc_level = float(attr[0])
        rr = round(float(attr[1]), 1)
        HandleBuy(symbol,poc_level,rr)

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()','output.dat')

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()
    
    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()