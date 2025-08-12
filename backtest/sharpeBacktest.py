rootPath = ".."
import sys
sys.path.append(rootPath)
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import numpy as np
from modules.aiztradingview import GetClose, GetCloseJP
from modules.rironkabuka import GetRironkabuka
import csv

bond = yf.Ticker("^TNX")
hist = bond.history(period="max")
risk_free_rate = round(hist.iloc[-1]['Close']/100,4)

def GetSharpeBefore(ticker):
    try:
        # Step 4: Retrieve historical stock prices and dividends
        # data = yf.Ticker(ticker).history(period="547d")
        data = yf.Ticker(ticker).history(period="max")
        
        data = data.loc[data.index<"2021-03-18"]
        # if len(data) < 245: return 0

        # Step 5: Calculate daily returns including dividends
        data["Adj Close with Div"] = data["Close"] + data["Dividends"].cumsum()
        data["Daily Return with Div"] = data["Adj Close with Div"].pct_change()

        # Step 6: Calculate annualized mean return and standard deviation
        mean_return = data["Daily Return with Div"].mean()
        std_dev = data["Daily Return with Div"].std()
        annual_return = mean_return * 252  # Assuming 252 trading days in a year
        annual_std_dev = std_dev * np.sqrt(252)

        # # Step 7: Define risk-free rate
        # risk_free_rate = 0.02

        # Step 8: Calculate Sharpe ratio
        sharpe_ratio = (annual_return - risk_free_rate) / annual_std_dev

        # Print the Sharpe ratio
        # print("Sharpe Ratio (including dividends):", sharpe_ratio)
        return sharpe_ratio, len(data)
    except:
        return 0, 0


def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'Sharpe', 'Length'])
        for symbol, sharpe, length in result_list:
            writer.writerow([symbol, sharpe, length])

closeDictJP = GetCloseJP()
closeDictUS = GetClose()
symbolList = list(closeDictJP.keys()) + list(closeDictUS.keys())

def HandleGetSharpeBefore(symbol):
    ticker = symbol
    if ticker in closeDictJP: 
        ticker += ".T"
    sharpe, length = GetSharpeBefore(ticker)
    return [symbol, sharpe, length]


# csvPath = f"{rootPath}/data/sharpeBacktest.csv"
# result_list = []
# with ThreadPoolExecutor(max_workers=100) as executor:
#     futures = [executor.submit(HandleGetSharpeBefore, symbol) for symbol in symbolList]
#     for future in as_completed(futures):
#         result = future.result()
#         symbol = result[0]
#         sharpe = result[1]
#         length = result[2]
#         # if sharpe <= 1: continue
#         # if symbol in closeDictJP:
#         #     rironkabuka = GetRironkabuka(symbol)
#         #     close = closeDictJP[symbol]
#         #     if close > rironkabuka: continue
#         result_list.append((symbol, sharpe, length))
#         result_list.sort(key=lambda x: x[1], reverse=True)
#         dump_result_list_to_csv(result_list, csvPath)

def GetSharpe(ticker):
    try:
        # Step 4: Retrieve historical stock prices and dividends
        # data = yf.Ticker(ticker).history(period="547d")
        data = yf.Ticker(ticker).history(start="2021-03-19")
        if len(data) < 245: return 0, 0

        # Step 5: Calculate daily returns including dividends
        data["Adj Close with Div"] = data["Close"] + data["Dividends"].cumsum()
        data["Daily Return with Div"] = data["Adj Close with Div"].pct_change()

        # Step 6: Calculate annualized mean return and standard deviation
        mean_return = data["Daily Return with Div"].mean()
        std_dev = data["Daily Return with Div"].std()
        annual_return = mean_return * 252  # Assuming 252 trading days in a year
        annual_std_dev = std_dev * np.sqrt(252)

        # # Step 7: Define risk-free rate
        # risk_free_rate = 0.02

        # Step 8: Calculate Sharpe ratio
        sharpe_ratio = (annual_return - risk_free_rate) / annual_std_dev

        # Print the Sharpe ratio
        # print("Sharpe Ratio (including dividends):", sharpe_ratio)
        return sharpe_ratio, len(data)
    except:
        return 0, 0

from modules.csvDump import load_csv_to_dict
portfolioPath = f'{rootPath}/data/sharpeBacktest.csv'
sourceDict = load_csv_to_dict(portfolioPath)
# print(sourceDict)


def HandleGetSharpe(symbol):
    ticker = symbol
    if ticker in closeDictJP: 
        ticker += ".T"
    sharpe, length = GetSharpe(ticker)
    return [symbol, sharpe, length]

resDict = {}
# result_list = []
# csvPath = f"{rootPath}/data/sharpeBacktestAfter.csv"
# with ThreadPoolExecutor(max_workers=100) as executor:
#     futures = [executor.submit(HandleGetSharpe, symbol) for symbol in list(sourceDict.keys())]
#     for future in as_completed(futures):
#         result = future.result()
#         symbol = result[0]
#         sharpe = result[1]
#         length = result[2]
#         resDict[symbol] = sharpe
#         result_list.append((symbol, sharpe, length))
#         result_list.sort(key=lambda x: x[1], reverse=True)
#         dump_result_list_to_csv(result_list, csvPath)

# for symbol in list(sourceDict.keys()):
#     result = HandleGetSharpe(symbol)
#     symbol = result[0]
#     sharpe = result[1]
#     length = result[2]
#     resDict[symbol] = sharpe
#     result_list.append((symbol, sharpe, length))
#     result_list.sort(key=lambda x: x[1], reverse=True)
#     dump_result_list_to_csv(result_list, csvPath)
portfolioPath = f'{rootPath}/data/sharpeBacktestAfter.csv'
resDict = load_csv_to_dict(portfolioPath)
# print(resDict)

for symbol, before in sourceDict.items():
    if symbol in resDict:
        beforeSharpe = before[0]
        length = int(before[1])
        if length < 796: continue
        print(resDict[symbol][0])
        afterSharpe = float(resDict[symbol][0])
        if afterSharpe < 1:
            print(symbol, beforeSharpe, afterSharpe)
            break
        else:
            print(symbol, 'PASSED')