import math

def floor_round(x, roundval):
    return round(roundval * math.floor(x / roundval),2)

def ceil_round(x, roundval):
    return round(roundval * math.ceil(x / roundval),2)

# RISK = 0.0158
# RISK = 0.01
RISK = 0.0018
def GetVol(cash, op, sl, tp, min_tick=1, point_val=5, currency='USD'):
    avalible_cash = cash * RISK
    points = round(abs(op - sl), 2)
    print(avalible_cash, points, point_val, min_tick)
    if points == 0: return 0
    try:
        vol = floor_round(avalible_cash / points / point_val, min_tick)
    except: return 0
    profit = vol * abs(tp - sl)
    if profit <= 2: return 0
    if currency == 'JPY':
        if profit <= 300: return 0
        if vol > 400: return 400
    # else:
    #     if vol > 100: return 100
    return vol

if __name__ == "__main__":
    import os;from pathlib import Path
    rootPath = Path(os.path.dirname(__file__)).parent.parent
    import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
    from modules.discord import Alert
    import modules.ib as ibc
    ibc = ibc.Ib()
    ib = ibc.GetIB(14)

    total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
    print(total_cash)
    MIN_VOL = 1
    op = 194.06
    sl = 193.68
    tp = 195
    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1, 'USD')
    print(vol)