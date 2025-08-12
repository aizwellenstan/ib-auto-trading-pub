import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.discord import Alert
import numpy as np
import modules.ib as ibc
from modules.trade.vol import GetVolTp
from modules.normalizeFloat import NormalizeFloat
import math
import sys

ibc = ibc.Ib()
ib = ibc.GetIB(27)
total_cash, avalible_cash = ibc.GetTotalCash()
positions = ibc.GetAllPositions()
basicPoint = 0.01

def GetSetup(contract, target):
    ask, bid = ibc.GetAskBidWithContract(contract)
    # op = bid + 0.01
    # if op > ask - 0.01: op = ask - 0.01
    op = ask
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
        print(contract.symbol,vol,op,sl,tp)
        if vol > 1:
            op = NormalizeFloat(op, 0.01)
            if (tp - op) * vol < 2: return np.array([0, 0, 0, 0])
            return np.array([vol, op, sl, tp])
    return np.array([0, 0, 0, 0])

def HandleBuy(contract, setup):
    vol = setup[0]
    if vol < 1: return 1
    op = setup[1]
    sl = setup[2]
    tp = setup[3]
    ibc.HandleBuyLimitTpWithContract(contract,vol,op,sl,tp,basicPoint)
    return vol

def scanner(attrDict, contractDict, hour, minute, sec, 
        hourLimit, setupDict, tradeDict
    ):

    if hour == hourLimit and minute >= 30 and sec >= 5:
        for symbol, setup in setupDict.items():
            if symbol in tradeDict: continue
            contract = contractDict[symbol]
            trade = HandleBuy(contract, setup)
            if trade > 0:
                tradeDict[symbol] = trade
        sys.exit(0)
    else:
        for symbol, attr in attrDict.items():
            if symbol not in contractDict: continue
            contract = contractDict[symbol]
            setup = GetSetup(contract, attr)
            setupDict[symbol] = setup

    return setupDict, tradeDict
    
def init():
    message = "Only Trade Discord Alert!!"
    Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def main():
    dayLightSaving = True
    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14
    # noTrade = ["RAPT"]
    attrDict = {
        # "MORF": 0.34,
        # "LOVE": 0.25,
        # "SWTX": 0.42,
        # "DKNG": 0.21,
        "RVMD": 0.27,
        "CZR": 0.43
    }
    init()
    contractDict = {}
    shift = 0
    for symbol, target in attrDict.items():
        if symbol in positions: continue
        contract = ibc.GetStockContract(symbol)
        contractDict[symbol] = contract
    tradeDict = {}
    setupDict = {}
    while(ib.sleep(1)):
        print(setupDict)
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        sec = currentTime.second
        setupDict, tradeDict = scanner(attrDict, contractDict, 
            hour, minute, sec, hourLimit, setupDict, tradeDict)
        print('tick')
        if dayLightSaving:
            if(hour == 13 and minute == 51 and sec == 0):
                shutDown()
        else:
            if(hour == 14 and minute == 51 and sec == 0):
                shutDown()

if __name__ == '__main__':
    main()