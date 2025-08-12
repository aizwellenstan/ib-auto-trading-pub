import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__))
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.kabumap import GetExDividend
import datetime
import modules.ib as ibc
from ib_insync import Stock, CFD, Forex
import pandas as pd
import math
from modules.trade.utils import floor_round
from config import load_credentials
ACCOUNT = load_credentials('monday')

ibc = ibc.Ib()
ib = ibc.GetIB(2)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)

contract = Forex('USDJPY')
ticker=ib.reqMktData(contract, '', False, False)
ib.sleep(2)
exchangeRate = ticker.bid
avalible_cash = total_cash * 0.5 * exchangeRate

FOLDER = f"{rootPath}/data/dividendHunter/jp"
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
ensure_directory_exists(FOLDER)

def GetSpread(contract):
    ticker=ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    ask = ticker.ask
    bid = ticker.bid
    retryCount = 0

    while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
        print("retry")
        ticker=ib.reqMktData(contract, '', False, False)
        ib.sleep(3)
        ask = ticker.ask
        bid = ticker.bid
        retryCount += 1
    spread = ask - bid
    return spread, ask, bid

def GetStockCFDSpread(symbol):
    cStock = Stock(symbol, 'TSEJ', 'JPY')
    cCFD = CFD(symbol, 'SMART', 'JPY')
    spreadStock, stockAsk, stockBid = GetSpread(cStock)
    # spreadCFD, ask, bid = GetSpread(cCFD)
    # if math.isnan(spreadCFD): spreadCFD = spreadStock
    spreadCFD = spreadStock
    return spreadStock, spreadCFD, stockAsk, stockBid, cStock, cCFD

def SubmitOrder(symbol, vol, ask, bid, cStock, cCFD):
    ibc.HandleLimitOrder(cStock, "BUY", vol, ask, ACCOUNT)
    ib.sleep(1)
    ibc.HandleLimitOrder(cCFD, "SELL", vol, bid, ACCOUNT)

def UpdateDivPer(ex_filename, divPerDict):
    df = pd.read_csv(ex_filename)
    df['symbol'] = df['symbol'].astype(str)
    npArr = df.to_numpy()
    closeDict = {}
    for symbol, close, divPer, div in npArr:
        if symbol not in divPerDict: continue
        contract = CFD(symbol, 'SMART', 'JPY')
        ib.qualifyContracts(contract)
        c = ib.reqContractDetails(contract)
        if len(c) < 1: continue
        contract = Stock(symbol, 'TSEJ', 'JPY')
        close = ibc.GetDataNpArr(contract, '1 min')[-1][3]
        closeDict[symbol] = close

    divPerDict = {}
    for symbol, close, divPer, div in npArr: 
        if symbol not in closeDict: continue
        divPer = div / closeDict[symbol]
        divPerDict[symbol] = [closeDict[symbol], div, divPer]
    divPerDict = dict(sorted(divPerDict.items(), key=lambda item: item[1][2], reverse=True))
    return divPerDict

# https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base
def main():
    exWithPayment = GetExDividend()
    exDate = '20241029'
    print(exWithPayment[exDate])

    div_per_filename = f"{FOLDER}/DividendHunter_{exDate}.csv"
    ex_filename = f"{FOLDER}/exdividend_{exDate}.csv"

    if not os.path.exists(div_per_filename):
        if not os.path.exists(ex_filename):
            # If the file doesn't exist, get the dividend data
            npArr = GetExDividend()[exDate]
            
            # Create a DataFrame
            df = pd.DataFrame(npArr, columns=["symbol", "close", "divPer", "div"])
            
            # Save the DataFrame to a CSV file with the dynamic filename
            df.to_csv(ex_filename, index=False)
            print(f"Data saved to {ex_filename}")
        else:
            df = pd.read_csv(ex_filename)
            
            # Convert the DataFrame back to a NumPy array
            npArr = df.to_numpy()

        closeDict = {}
        for symbol, close, divPer, div in npArr:
            contract = CFD(symbol, 'SMART', 'JPY')
            ib.qualifyContracts(contract)
            c = ib.reqContractDetails(contract)
            if len(c) < 1: continue
            contract = Stock(symbol, 'TSEJ', 'JPY')
            arr = ibc.GetDataNpArr(contract, '1 min')
            if len(arr) < 1: continue
            close = arr[-1][3]
            closeDict[symbol] = close

        divPerDict = {}
        for symbol, close, divPer, div in npArr: 
            if symbol not in closeDict: continue
            divPer = div / closeDict[symbol]
            divPerDict[symbol] = [closeDict[symbol], div, divPer]
        divPerDict = dict(sorted(divPerDict.items(), key=lambda item: item[1][2], reverse=True))
        print(divPerDict)

        divPer_df = pd.DataFrame.from_dict(divPerDict, orient='index').reset_index()
        divPer_df.columns = ["symbol", "close", "div", "divPer"]
        divPer_df.to_csv(div_per_filename, index=False)
        print(f"divPerDict saved to {div_per_filename}")
    else:
        # Load the existing divPerDict from the CSV
        divPer_df = pd.read_csv(div_per_filename)
        divPer_df["symbol"] = divPer_df["symbol"].astype(str)
        divPerDict = {row["symbol"]: [row["close"], row["div"], row["divPer"]] for _, row in divPer_df.iterrows()}

    print(divPerDict)
    print(avalible_cash)
    divPerDict = UpdateDivPer(ex_filename, divPerDict)

    for symbol, data in divPerDict.items():
        close = data[0]
        div = int(data[1])
        print(f"Symbol: {symbol}, Close: {close},  Div: {div}")
        sharesToBuy = floor_round(avalible_cash / close, 100)
        totalDivs = sharesToBuy * div
    
        spreadStock = 0.01
        spreadCFD = 0.01

        spreadStock, spreadCFD, ask, bid, cStock, cCFD = GetStockCFDSpread(symbol)
        print(spreadStock, spreadCFD)
        if math.isnan(spreadStock): continue
        if spreadStock <= 0: continue
        commissionAndSpread = (251 + (spreadStock+spreadCFD) * sharesToBuy) * 2
        profit = totalDivs - commissionAndSpread
        print(symbol, "PROFIT: ", profit)
        # if profit <= 0: continue
        print(f"Symbol: {symbol}")
        print(f"Shares to Buy: {sharesToBuy}")
        print(f"Total Dividends: ${totalDivs:,.2f}")
        print(f"Spread {-spreadStock}")
        print(f"Commssion & Spread: ${-commissionAndSpread:,.2f}")
        print(f"Profit: ${profit:,.2f}")
        if profit >= 1: 
            SubmitOrder(symbol, sharesToBuy, ask, bid, cStock, cCFD)
            break

if __name__ == '__main__':
    main()