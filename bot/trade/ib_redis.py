import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.combine import Combine
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

ibc = ibc.Ib()
ib = ibc.GetIB(5)

def main():
    hourLimit = GetTradeTime()
    contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
    tfs = ['5 mins']
    lastOpMap = {}
    channel_name = 'MES_5mins'
    while(ib.sleep(2)):
        npArr = ibc.GetDataNpArr(contractMES, tf)
        r.publish(channel_name, npArr)
        print(f"Published: {message}")