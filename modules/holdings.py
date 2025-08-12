import pandas as pd
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import yfinance as yf
from yahooquery import Ticker
import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.aiztradingview import GetETF

def GetHoldings(ticker :str):
    try:
        ticker = ticker.replace("-",",")
        try:
           int(ticker)
           ticker += ".T"
        except: pass
        df = yf.Ticker(ticker)._info

        print(df)
        sys.exit()

        # sector weightings, returns pandas DataFrame
        # t.fund_sector_weightings

        fund_holding_info = t.fund_holding_info
        print(fund_holding_info)
        if ticker in fund_holding_info:
            if "holdings" in fund_holding_info[ticker]:
                holdings = fund_holding_info[ticker]["holdings"]

                holdingsDict = {}
                for holding in holdings:
                    sym = holding["symbol"]
                    weight = holding["holdingPercent"]
                    holdingsDict[sym] = weight

                return holdingsDict
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

if __name__ == "__main__":
    holdings = GetHoldings('SPY')
    print(holdings)

# etfHoldingsDict = {}
# etfList = GetETF()
# etfList = etfList[0:20]
# for etf in etfList:
#     holdings = GetHoldings(etf)
#     if holdings is None: continue
#     etfHoldingsDict[etf] = holdings
# print(etfHoldingsDict)