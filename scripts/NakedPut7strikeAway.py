rootPath = '.'
import sys
sys.path.append(rootPath)
import yfinance as yf
from modules.aiztradingview import GetClose
from ib_insync import *
import math
import pandas as pd
from modules.csvDump import DumpCsv
import os
from datetime import date, datetime
from modules.discord import Alert

today = date.today()

ib = IB()
ib.connect('127.0.0.1',7497,clientId=19)

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
total_cash = float(cashDf['value'])
print(total_cash)
total_cash -= (259 + 61 + 5)
risk = total_cash/100

def GetData(symbol):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='6 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        df = pd.DataFrame(data)
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()
    except:
        return []
    
    return npArr

def CheckHaveOption(symbol, currency):
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
    print('NEVER USE STP ORDER WHEN SELLING PUTS')
    Alert('NEVER USE STP ORDER WHEN SELLING PUTS')
    optionPath = f'{rootPath}/data/NakedPuts7StrikeAway.csv'
    optionList = []
    if os.path.exists(optionPath):
        df = pd.read_csv(optionPath)
        optionList = list(df.Symbol.values)
    
    tradable = []
    for contract in optionList:
        explode = contract.split('_')
        symbol = explode[0]
        expir = explode[1]
        strike = float(explode[2])
    
        options_contract = Option(symbol, expir, strike, 'P', 'SMART', tradingClass=symbol)
        ib.qualifyContracts(options_contract)
        bars = ib.reqHistoricalData(
            contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
            whatToShow='TRADES', useRTH=True)
        if len(bars) < 1: continue
        if bars[-1].low < 0.11: continue

        npArr = GetData(symbol)
        if len(npArr) < 1: continue
        # if npArr[-1][0] / npArr[-2][3] < 1.008: continue
        print(contract)
        tradable.append(contract)
    print(tradable)
    # # newOptionList = []
    # # for symbol in optionList:
    # #     if symbol in countryDict:
    # #         if countryDict[symbol] == "China": continue
    # #     newOptionList.append(symbol)
    # # DumpCsv(optionPath, newOptionList)
    # rrDict = {}
    # for symbol, close in closeDict.items():
    #     if symbol in ignore: continue
    #     if symbol in optionList:
    #         if close > risk: continue
    #         tradableList.append(symbol)
    #         contract = Stock(symbol, 'SMART', currency)
    #         ib.qualifyContracts(contract)
    #         chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
    #         trade = 0
    #         error = False
    #         for optionschain in chains:
    #             if error: break
    #             if trade > 0: break
    #             strikeList = optionschain.strikes
    #             strikeList.sort(reverse=True)
    #             for strike in strikeList:
    #                 if error: break
    #                 if strike < close - 0.5:
    #                     if len(optionschain.expirations) < 2: 
    #                         error = True
    #                         break
    #                     expiration = 0
    #                     expir = datetime.strptime(optionschain.expirations[expiration], '%Y%m%d').date()
    #                     dur = (expir-today).days
    #                     while dur < 1:
    #                         expiration += 1
    #                         expir = datetime.strptime(optionschain.expirations[expiration], '%Y%m%d').date()
    #                         dur = (expir-today).days
    #                     options_contract = Option(symbol, optionschain.expirations[expiration], strike, 'P', 'SMART', tradingClass=symbol)
    #                     ib.qualifyContracts(options_contract)
    #                     bars = ib.reqHistoricalData(
    #                     contract=options_contract, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
    #                     whatToShow='TRADES', useRTH=True)
    #                     if len(bars) < 1: 
    #                         error = True
    #                         break
    #                     gain = bars[-1].low/close/100/dur
    #                     if gain > 0:
    #                         rrDict[f"{symbol}_{optionschain.expirations[expiration]}_{strike}"] = gain
    #                         rrDict = dict(sorted(rrDict.items(), key=lambda item: item[1], reverse=True))
    #                         print(rrDict)
    #                         trade += 1
    #                     break
    #     print(rrDict)
    # nakedPuts = rrDict.keys()
    # nakedPutsPath = f'{rootPath}/data/NakedPuts.csv'
    # DumpCsv(nakedPutsPath, nakedPuts)
    # print(nakedPuts)

if __name__ == '__main__':
    main()
