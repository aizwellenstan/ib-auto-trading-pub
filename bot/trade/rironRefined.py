rootPath = '../..'
import sys
sys.path.append(rootPath)
from modules.csvDump import LoadDict
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp, GetVolLargeSlTp

ibc = ibc.Ib()
ib = ibc.GetIB(25)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def HandleBuy(symbol):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolLargeSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        if vol > 2:
            # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
            return vol
    return 0

rironPath = f"{rootPath}/data/RironRefined.csv"
rironDict = LoadDict(rironPath, "riron")

ignoreList = ['GOOG','GOOGL','SPUU']
for symbol, riron in rironDict.items():
    ask = ibc.GetAsk(symbol)
    if ask < 0.01: continue
    if ask < riron - 0.01:
        print(symbol, riron)
        if symbol in ignoreList: continue
        vol = HandleBuy(symbol)
        if vol > 0: break