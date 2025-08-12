from yahooquery import Ticker
import pandas as pd
import numpy as np
import sys

# https://yahooquery.dpguthrie.com/guide/ticker/modules/
# [
#     'assetProfile', 'recommendationTrend', 'cashflowStatementHistory',
#     'indexTrend', 'defaultKeyStatistics', 'industryTrend', 'quoteType',
#     'incomeStatementHistory', 'fundOwnership', 'summaryDetail', 'insiderHolders',
#     'calendarEvents', 'upgradeDowngradeHistory', 'price', 'balanceSheetHistory',
#     'earningsTrend', 'secFilings', 'institutionOwnership', 'majorHoldersBreakdown',
#     'balanceSheetHistoryQuarterly', 'earningsHistory', 'esgScores', 'summaryProfile',
#     'netSharePurchaseActivity', 'insiderTransactions', 'sectorTrend',
#     'incomeStatementHistoryQuarterly', 'cashflowStatementHistoryQuarterly', 'earnings',
#     'pageViews', 'financialData'
# ]

def GetIncome(symbol, currency="USD"):
    try:
        if "." in symbol:
            symbol = symbol.replace(".","-")
        if currency == 'JPY':
            symbol += '.T'
        t = Ticker(symbol)
        modules= 'incomeStatementHistoryQuarterly'
        df = pd.DataFrame(t.get_modules(modules)[symbol]["incomeStatementHistory"])
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
        npArr = df[['endDate', 'netIncome']].to_numpy()
        return npArr
    except: return[]

from datetime import datetime, timedelta

def ConvertDate(input_datetime_str):
    input_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d').replace(tzinfo=None)
    
    # # Add one day to the datetime
    # next_day_datetime = input_datetime + timedelta(days=1)

    # # Format the next day datetime as "YYYY-MM-DD"
    # next_day_str = next_day_datetime.strftime('%Y-%m-%d')

    return input_datetime

def GetEarnings(symbol, currency="USD"):
    try:
        if "." in symbol:
            symbol = symbol.replace(".","-")
        if currency == 'JPY':
            symbol += '.T'
        t = Ticker(symbol)
        modules= 'earningsHistory'
        # print(t.get_modules("earningsHistory")[symbol])
        df = pd.DataFrame(t.get_modules(modules)[symbol]["history"])
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(df)
        npArr = df[['quarter', 'epsActual']].to_numpy()
        res = []
        for i in npArr:
            res.append([ConvertDate(i[0]),i[1]])
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e) 
        return[]

def GetInventory(symbol):
    try:
        try:
            int(symbol)
            symbol += ".T"
        except: pass
        t = Ticker(symbol)
        modules= 'balanceSheetHistory'
        print(t.get_modules(modules))
        # print(t.get_modules("earningsHistory")[symbol])
        df = pd.DataFrame(t.get_modules(modules)[symbol]["history"])
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(df)
        print(df)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e) 
        return[]