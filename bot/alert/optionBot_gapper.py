import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=11)

def GetData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df[['open','high','low','close']]
    npArr = df.to_numpy()
    
    return npArr

def GetPreviousData(contract):
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    return hisBarsD1[-1].high, hisBarsD1[-1].close

gapDown = False
pCloseIWM = 0.0
pCloseDIA = 0.0
clsoeIWM = 0.0
closeDIA = 0.0

def PlaceOrder(closeDict, chainsDict, gappers):
    tradedList = []
    for symbol in gappers:
        for optionschain in chainsDict[symbol]:
            if symbol in tradedList: break
            strikeList = optionschain.strikes
            for strike in strikeList:
                if strike > closeDict[symbol]:
                    options_contract = Option(symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=symbol)
                    options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
                    print(options_contract)
                    trade = ib.placeOrder(options_contract, options_order)
                    tradedList.append(symbol)
                    break

    # for optionschain in chainsDIA:
    #     if tradeDIA > 0: break
    #     strikeList = optionschain.strikes
    #     strikeList.sort(reverse=True)
    #     for strike in strikeList:
    #         if strike < closeDIA:
    #             options_contract = Option('DIA', optionschain.expirations[1], strike, 'P', 'SMART', tradingClass='DIA')
    #             options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
    #             print(options_contract)
    #             trade = ib.placeOrder(options_contract, options_order)
    #             tradeDIA += 1
    #             break

    for symbol in tradedList:
        Alert(symbol + ' C')
    
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

    init()

    contractIdDict = {
        'AMZN':3691937, 
        'AAPL':265598,
        'NVDA': 4815747,
        'TSM': 6223250, 
        'DIS': 6459,
        'JPM': 1520593,
        'CMCSA': 267748,
        'NKE': 10291,
        'WMT': 13824,
        'KO': 8894,
        'NFLX': 15124833,
        'WFC': 10375,
        'BAC': 10098, 
        'BMY': 5111
    }

    contractDict = {}
    chainsDict = {}
    pHighDict = {}
    pCloseDict = {}
    closeDict = {}
    optionList = []

    for symbol, contractId in contractIdDict.items():
        contract = Stock(symbol, 'SMART', 'USD')
        contractDict[symbol] = contract
        chainsDict[symbol] = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contractId)
        pHighDict[symbol], pCloseDict[symbol] = GetPreviousData(contract)
        optionList.append(symbol)

    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if (hour == hourLimit and minute <= 29 and sec < 30):
            gappers = []
            for symbol in optionList:
                close = GetData(symbol)[-1][3]
                if (
                    close > pHighDict[symbol] and
                    close / pCloseDict[symbol] > 1.038
                ):  
                    gappers.append(symbol)
                    closeDict[symbol] = close
        if (hour == hourLimit and minute == 30):
            PlaceOrder(closeDict,chainsDict,gappers)
            shutDown()
            return
        print('tick')
        if(hour == hourLimit and minute == 51 and sec == 0):
            shutDown()
            return

if __name__ == '__main__':
    main()