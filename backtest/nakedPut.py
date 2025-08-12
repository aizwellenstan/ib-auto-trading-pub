rootPath = '..'
import sys
sys.path.append(rootPath)
import yfinance as yf
from modules.aiztradingview import GetClose, GetAttr
from ib_insync import *
import math
import pandas as pd
from modules.csvDump import DumpCsv
import os
from datetime import date, datetime

today = date.today()

ib = IB()
ib.connect('127.0.0.1',7497,clientId=17)

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
total_cash = float(cashDf['value'])
print(total_cash)
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
    except:
        return False

def main():
    ignore = ['UVIX','DDD','AMC','FSTX']
    currency = 'USD'
    closeDict = GetClose()
    countryDict = GetAttr("country")
    optionList = []
    tradableList = []
    noTradeList = []
    optionPath = f'{rootPath}/data/Options.csv'
    if os.path.exists(optionPath):
        df = pd.read_csv(optionPath)
        optionList = list(df.Symbol.values)
    noTradePath = f'{rootPath}/data/NoTrade.csv'
    if os.path.exists(noTradePath):
        df = pd.read_csv(noTradePath)
        noTradeList = list(df.Symbol.values)
    # newOptionList = []
    # for symbol in optionList:
    #     if symbol in countryDict:
    #         if countryDict[symbol] == "China": continue
    #     newOptionList.append(symbol)
    # DumpCsv(optionPath, newOptionList)
    rrDict = {}
    for symbol, close in closeDict.items():
        if symbol in ignore: continue
        if symbol in countryDict:
            if countryDict[symbol] == "China": continue
        # if symbol in noTradeList: continue
        if symbol in optionList:
        # if CheckHaveOption(symbol):
            if close > risk: continue
            tradableList.append(symbol)
            contract = Stock(symbol, 'SMART', currency)
            ib.qualifyContracts(contract)
            chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
            trade = 0
            error = False
            for optionschain in chains:
                if error: break
                if trade > 0: break
                strikeList = optionschain.strikes
                strikeList.sort(reverse=True)
                for strike in strikeList:
                    if error: break
                    if strike < close - 0.5:
                        if len(optionschain.expirations) < 2: 
                            error = True
                            break
                        for expiration in optionschain.expirations:
                            expir = datetime.strptime(expiration, '%Y%m%d').date()
                            dur = (expir-today).days
                            if dur < 1: continue
                            options_contract = Option(symbol, expiration, strike, 'P', 'SMART', tradingClass=symbol)
                            ib.qualifyContracts(options_contract)
                            bars = ib.reqHistoricalData(
                            contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                            whatToShow='TRADES', useRTH=True)
                            if len(bars) < 1: 
                                error = True
                                break
                            if bars[-1].low < 0.11: continue
                            gain = bars[-1].low/close/100/dur
                            if gain > 0:
                                rrDict[f"{symbol}_{expiration}_{strike}"] = gain
                                rrDict = dict(sorted(rrDict.items(), key=lambda item: item[1], reverse=True))
                                print(rrDict)
                                trade += 1
                            break
        print(rrDict)
    nakedPuts = rrDict.keys()
    nakedPutsPath = f'{rootPath}/data/NakedPuts.csv'
    DumpCsv(nakedPutsPath, nakedPuts)
    print(nakedPuts)

if __name__ == '__main__':
    main()
