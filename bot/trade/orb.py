import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.aiztradingview import GetOrb
import pandas as pd
import modules.ib as ibc
from ib_insync import Stock, CFD
import math
from modules.trade.options import BuyOption
from config import load_credentials
from modules.trade.utils import floor_round, GetVol
from modules.trade.futures import GetTradeTime, ExecTrailMOC

CASHACCOUNT = load_credentials('cashAccount')
ibc = ibc.Ib()
ib = ibc.GetIB(1)
stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(CASHACCOUNT)

df = pd.read_csv(f"{rootPath}/data/orb.csv")
cfd = df[['Symbol', 'Atr']].values.tolist()
orb = GetOrb()[:20]

orb_set = set(orb)

# Filter 'cfd' to keep only rows with a Symbol in 'orb_set'
cfd = [row for row in cfd if row[0] in orb_set]
cfd = sorted(cfd, key=lambda x: orb.index(x[0]))
print(cfd)

def ExecScan(cfd):
    for c in cfd:
        symbol = c[0]
        contract = Stock(symbol, 'SMART', 'USD')
        ibc.qualifyContracts(contract)
        npArr = ibc.GetDataNpArr(contract , '5 mins')
        if len(npArr) > 0:
            if npArr[-1][1] > npArr[-2][1]:
                op = npArr[-1][1]
                sl = op - c[1] * 0.1
                sl = floor_round(sl, 0.01)
                tp = floor_round(op * 1.26315789474, 0.01)
                vol = GetVol(stock_total_cash, op, sl, tp, 1, 1, 'USD')
                MIN_VOL = 12
                if vol < MIN_VOL: 
                    print(vol)
                    continue
                contractCFD = CFD(contract.symbol, 'SMART', 'USD')
                print(symbol, op, sl, tp)
                # ExecTrailMOC(ibc, 1, contractCFD, vol, op, sl, 0.01, CASHACCOUNT)

hourLimit = GetTradeTime()
while(ib.sleep(2)):
    currentTime = ib.reqCurrentTime()
    hour = currentTime.hour
    if hour == hourLimit + 7: continue
    minute = currentTime.minute
    t = hour * 60 + minute

    if(
        t > hourLimit * 60 + 30 and
        t >= hourLimit * 60 + 35
    ): 
        ExecScan(cfd)
        break