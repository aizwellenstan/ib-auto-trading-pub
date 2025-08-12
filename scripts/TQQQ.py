from modules.aiztradingview import GetADR
from modules.normalizeFloat import NormalizeFloat

adr = GetADR('USD')

def GetSL(op, adr, basicPoint):
    sl = op - 0.14
    if op > 16.5: sl = op * 0.9930862018
    if op > 100: sl = op * 0.9977520318
    if adr > 0.63: sl = op - adr * 0.4
    elif adr > 0.14: sl = op - adr * 0.35
    else: sl = op - adr * 0.05
    if adr > 1.21:
        if op - sl < basicPoint * 63:
            sl = op - basicPoint * 63
        if sl < 0:
            sl = op - basicPoint * 40
    elif adr > 0.47:
        if op - sl < basicPoint * 49:
            sl = op - basicPoint * 49
        if sl < 0:
            sl = op - basicPoint * 40
    elif adr > 0.2:
        if op - sl < basicPoint * 40:  
            sl = op - basicPoint * 40
    else:
        if (
            op - sl < basicPoint * 2 or
            op - sl > basicPoint * 40
        ):  
            sl = op - basicPoint * 40
        if op - sl < basicPoint * 40:
            sl = op - basicPoint * 40
    return sl

def main():
    import modules.ib as ibc
    ibc = ibc.Ib()
    ib = ibc.GetIB(20)
    total_cash, avalible_cash = ibc.GetTotalCash()
    basicPoint = 0.01
    risk = 0.00613800895
    symbol = 'TQQQ'
    ask, bid = ibc.GetAskBid(symbol)
    sl = 22.02
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        vol = int(total_cash * risk / (ask - sl))
        print(vol)

main()