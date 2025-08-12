import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from modules.trade.placeOrder import PlaceOrder
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp
from modules.normalizeFloat import NormalizeFloat
from modules.data import GetNpData

ibc = ibc.Ib()
ib = ibc.GetIB(24)
total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def HandleBuyOption(symbol, chains, tp):
    for optionschain in chains:
        strikeList = optionschain.strikes
        for strike in strikeList:
            if strike > tp:
                optionContract = ibc.GetOptionCallContract(symbol, optionschain.expirations[1], strike)
                positions = ibc.GetAllPositions()
                if symbol not in positions:
                    PlaceOrder(ib, optionContract)
                message = symbol+' M 1OTM C TP: '+str(tp)
                Alert(message)
                print(message)
                return 1
    return 0

def HandleBuy(symbol, target):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    if (target - op) * vol < 2: return 1
    if(ask>0 and bid>0):
        target = NormalizeFloat(target, basicPoint)
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,target)
        positions = ibc.GetAllPositions()
        if symbol not in positions:
            ibc.HandleBuyLimit(symbol,vol,op,sl,target,basicPoint)
        return vol
    return 1

def scanner(retraceDict, contractDict, hour, minute, sec, 
    hourLimit, chainsDict, previousCloseDict, noOptionList, tradeDict
    ):

    askDict = {}
    tpDict = {}
    optionTpDict = {}
    for symbol, retraceVal in retraceDict.items():
        if symbol in tradeDict:
            if tradeDict[symbol] > 0: continue
        contract = contractDict[symbol]
        ask = ibc.GetAskByContract(contract)
        # ask = ibc.GetData1D(contract)[-1].open
        askDict[symbol] = ask
        tpDict[symbol] = ask + (previousCloseDict[symbol] - ask) * retraceVal
        optionTpDict[symbol] = ask + (previousCloseDict[symbol] - ask) * retraceVal * 0.81203007518

    if hour == hourLimit and minute >= 30 and sec >= 5:
        for symbol, retraceVal in retraceDict.items():
            if symbol in tradeDict:
                if tradeDict[symbol] > 0: continue
            ask = askDict[symbol]
            if ask < 0.01: continue
            previousClose = previousCloseDict[symbol]
            if ask >= previousClose: continue
            tp = optionTpDict[symbol]
            if symbol in noOptionList or tp - ask < 0.07:
                tp = tpDict[symbol]
                trade = HandleBuy(symbol, tp)
                if trade > 0:
                    tradeDict[symbol] = trade
            else:
                trade = HandleBuyOption(symbol, chainsDict[symbol], tp)
                if trade > 0:
                    tradeDict[symbol] = trade

    return tradeDict
    
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

    correlationThresholdDict = {
        'HOOD': 0.11, 
        'BYND': 1.0, 
        'UBER': 0.11, 'AFRM':
        0.35, 'GME': 0.27}
    signal = "QQQ"
    signalArr = GetNpData(signal)[-1058:]

    retraceDict = {
        'HOOD': 0.34, 
        'BYND': 0.2, 
        'UBER': 0.88, 
        'AFRM': 0.17, 'GME': 1.0, 
        }
    
    newRetraceDict = {}
    for symbol, correlationThreshold in  correlationThresholdDict.items():
        npArr = GetNpData(symbol)
        if len(npArr) < 1058: continue
        npArr = npArr[-1058:]
        correlation = np.corrcoef(signalArr[:,3][:-1], npArr[:,3][:-1])[0, 1]
        if correlation < correlationThreshold:
            newRetraceDict[symbol] = retraceDict[symbol]
    retraceDict = newRetraceDict
    
    noOptionList = ["WMT","JPM",  "SWN", "LCID"]
    init()
    contractDict = {}
    chainsDict = {}
    previousCloseDict = {}
    shift = 0
    for symbol, target in retraceDict.items():
        contract = ibc.GetStockContract(symbol)
        contractDict[symbol] = contract
        chainsDict[symbol] = ibc.GetChains(symbol)
        previousCloseDict[symbol] = ibc.GetData1D(contract)[-1-shift].close
    tradeDict = {}
    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second
        tradeDict = scanner(retraceDict, contractDict, 
            hour, minute, sec, hourLimit, 
            chainsDict, previousCloseDict,  noOptionList,
            tradeDict)
        print('tick')
        if dayLightSaving:
            if(hour == 13 and minute == 51 and sec == 0):
                shutDown()
        else:
            if(hour == 14 and minute == 51 and sec == 0):
                shutDown()

if __name__ == '__main__':
    main()