rootPath = '..'
import sys
sys.path.append(rootPath)
import yfinance as yf
import pandas as pd
import numpy as np
from modules.aiztradingview import GetAttr, GetBetaJP
import datetime

today = datetime.date.today()
year = int(today.strftime("%Y"))-1

betaDict = GetAttr("beta_1_year")
betaDictJP = GetBetaJP()

bond = yf.Ticker("^TNX")
hist = bond.history(period="max")
risk_free_rate = round(hist.iloc[-1]['Close']/100,4)

def GetExpectGain(symbol, currency='USD'):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        ticker = stockInfo
        stock = ticker.actions
        stock_split = stock["Stock Splits"].to_numpy()
        stock_split_replaced = np.where(stock_split == 0, 1, stock_split)
        stock_split_comp = np.cumprod(stock_split_replaced, axis=0)
        stock["stocksplit_adj"] = stock_split_comp.tolist()
        stock["div_adj"] = stock["Dividends"] * stock["stocksplit_adj"]
        stock['year'] = stock.index.year
        stock_grp = stock.groupby(by=["year"]).sum()
        stock_grp["div_PCT_Change"] = stock_grp["div_adj"].pct_change(fill_method ='ffill')
        stock_grp = stock_grp[~stock_grp.isin([np.nan, np.inf, -np.inf]).any(1)]
        median_growth = stock_grp["div_PCT_Change"].median()
    
        lst_Div = stock_grp.at[year,'Dividends']
        exp_future_div = round(lst_Div * (1 + median_growth),2)

        mkt_return = 0

        MKT_Risk_prem = mkt_return - risk_free_rate
        beta = 1
        if currency == 'JPY':
            beta = betaDictJP[symbol]
        else:
            beta = betaDict[symbol]
        COE = round(beta * MKT_Risk_prem + risk_free_rate,5)
        fair_sharePrice = round(exp_future_div/(COE-median_growth),2)
        stock_price = ticker.history(period="today")
        stock_price_close = round(stock_price.iloc[0]['Close'],4)
        expected_gain_loss = fair_sharePrice/stock_price_close-1
        # expected_gain_loss = "{:.0%}".format(expected_gain_loss)

        return expected_gain_loss
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def CheckRironkabuka(symbol):
    gain = GetExpectGain(symbol)
    if gain > 0: return True
    return False