rootPath = '..'
import sys
sys.path.append(rootPath)
import yfinance as yf
from modules.aiztradingview import GetCommonStock, GetAttr
from ib_insync import *
import math
import pandas as pd
from modules.csvDump import DumpCsv
import os
from datetime import date, datetime
import modules.ib as ibc

today = date.today()

ibc = ibc.Ib()
ib = ibc.GetIB(12)

total_cash, avalible_cash = ibc.GetTotalCash()
total_cash -= (259 + 61 + 5)
risk = total_cash/100

def CheckHaveOption(symbol, currency='USD'):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        optionChain=list(stockInfo.options)
        haveOptionChain = False
        if len(optionChain) > 0:
            haveOptionChain = True
        return haveOptionChain
    except: return False

def main():
    ignore = ['UVIX','DDD','AMC','FSTX','BOIL','BBBY','SI',
        'CVNA','RIVN','SAVE','FSLY','U']
    currency = 'USD'
    closeDict = GetCommonStock()
    countryDict = GetAttr("country")
    optionList = []
    noTradeList = []
    optionPath = f'{rootPath}/data/Options.csv'
    if os.path.exists(optionPath):
        df = pd.read_csv(optionPath)
        optionList = list(df.Symbol.values)
    noTradePath = f'{rootPath}/data/NoTrade.csv'
    if os.path.exists(noTradePath):
        df = pd.read_csv(noTradePath)
        noTradeList = list(df.Symbol.values)
    rrDict = {}
    for symbol, close in closeDict.items():
        if symbol in ignore: continue
        if symbol in countryDict:
            if countryDict[symbol] == "China": continue
        if symbol not in optionList: continue
        # if CheckHaveOption(symbol):
        if close > risk: continue
        print("SYMBOL",symbol)
        if symbol == "MARK": continue
        chains = ibc.GetChains(symbol)
        trade = 0
        error = False
        for optionschain in chains:
            if error: break
            if trade > 0: break
            if len(optionschain.expirations) < 2: break
            for expiration in optionschain.expirations:
                if error: break
                if trade > 0: break
                expir = datetime.strptime(expiration, '%Y%m%d').date()
                dur = (expir-today).days
                if dur < 1: continue
                strikeList = optionschain.strikes
                strikeList.sort(reverse=True)
                strikeAwayCount = 0
                targetPrice = close - 0.5
                for strike in strikeList:
                    if error: break
                    if strike < targetPrice:
                        if strikeAwayCount < 6:
                            strikeAwayCount += 1
                            continue
                        print(symbol, expiration, strike)
                        optionContract = ibc.GetOptionPutContract(symbol, expiration, strike)
                        data = ibc.GetData(optionContract)
                        if len(data) < 1:
                            error = True
                            break
                        if data[-1].low < 0.11: break
                        gain = data[-1].low/close/100/dur
                        rrDict[f"{symbol}_{expiration}_{strike}"] = gain
                        rrDict = dict(sorted(rrDict.items(), key=lambda item: item[1], reverse=True))
                        print(rrDict)
                        trade += 1
                        break
        print(rrDict)
    nakedPuts = rrDict.keys()
    nakedPutsPath = f'{rootPath}/data/NakedPuts6StrikeAway.csv'
    DumpCsv(nakedPutsPath, nakedPuts)
    print(nakedPuts)

if __name__ == '__main__':
    main()
