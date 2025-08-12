rootPath = '../..'
import sys
sys.path.append(rootPath)
from modules.csvDump import LoadDict
import modules.ib as ibc
from modules.trade.vol import GetVolTp
from modules.normalizeFloat import NormalizeFloat
import math

ibc = ibc.Ib()
ib = ibc.GetIB(27)

total_cash, avalible_cash = ibc.GetTotalCash()
positions = ibc.GetAllPositions()
basicPoint = 0.01

def HandleBuy(symbol, target):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    target = NormalizeFloat(math.ceil(bid+ask)/2 + target, 0.01)
    sl = op - (target - op)
    sl = NormalizeFloat(sl, 0.01)
    vol, tp = GetVolTp(
        total_cash,avalible_cash,op,sl,'USD'
    )
    if tp > target:
        tp = target
    else:
        sl = op - (tp - op)
        sl = NormalizeFloat(sl, 0.01)
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        if vol > 1:
            if (tp - op) * vol < 2: return 0
            ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
            return vol
    return 0

# noTrade = ["RAPT"]
centDict = {
    "MORF": 0.34,
    "LOVE": 0.25,
    # "SWTX": 0.42,
    "DKNG": 0.21,
    "RVMD": 0.27,
    "CZR": 0.43
}

for symbol, tp in centDict.items():
    ask = ibc.GetAsk(symbol)
    if ask < 0.01: continue
    if symbol in positions: continue
    vol = HandleBuy(symbol, tp)