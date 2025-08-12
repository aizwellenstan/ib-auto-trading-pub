rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetADR
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetADR

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
    sl =  NormalizeFloat(sl, basicPoint)
    return sl

def GetVolSlTp(symbol, total_cash, avalible_cash, op, currency='USD'):
    risk = 0.00613800895
    basicPoint = 0.01
    if currency == 'JPY': basicPoint = 1
    adrDict = GetADR(currency)
    sl = GetSL(op,adrDict[symbol],basicPoint)
    maxVol = int(total_cash/2/op)
    avalibleVol = int(avalible_cash*0.83657741748/op)
    vol = int(total_cash * risk / (op - sl))
    if vol > maxVol: vol = maxVol
    if vol > avalibleVol: vol = avalibleVol
    tp = NormalizeFloat(op+(op-sl)*15.42857143, basicPoint)
    return vol, sl, tp

def GetVolLargeSlTp(symbol, total_cash, avalible_cash, op, currency='USD'):
    risk = 0.00613800895
    basicPoint = 0.01
    if currency == 'JPY': basicPoint = 1
    adrDict = GetADR(currency)
    sl = GetSL(op,adrDict[symbol]*1.4,basicPoint)
    maxVol = int(total_cash/2/op)
    avalible_cash -= 149
    avalibleVol = int(avalible_cash*0.83657741748/op)
    vol = int(total_cash * risk / (op - sl))
    if vol > maxVol: vol = maxVol
    if vol > avalibleVol: vol = avalibleVol
    tp = NormalizeFloat(op+(op-sl)*15.42857143, basicPoint)
    return vol, sl, tp

def GetVolTp(total_cash, avalible_cash, op, sl, currency='USD'):
    risk = 0.00613800895
    basicPoint = 0.01
    if currency == 'JPY': basicPoint = 1
    maxVol = int(total_cash/2/op)
    avalibleVol = int(avalible_cash*0.83657741748/op)
    vol = int(total_cash * risk / (op - sl))
    if vol > maxVol: vol = maxVol
    if vol > avalibleVol: vol = avalibleVol
    tp = NormalizeFloat(op+(op-sl)*15.42857143, basicPoint)
    return vol, tp

def GetVol(total_cash, avalible_cash, op, sl, currency='USD'):
    risk = 0.00613800895
    basicPoint = 0.01
    if currency == 'JPY': basicPoint = 1
    maxVol = int(total_cash/2/op)
    avalibleVol = int(avalible_cash*0.83657741748/op)
    vol = int(total_cash * risk / (op - sl))
    if vol > maxVol: vol = maxVol
    if vol > avalibleVol: vol = avalibleVol
    return vol