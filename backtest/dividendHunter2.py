import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.dividendCalendarV2 import GetExDividendWithPayment
import datetime
import modules.ib as ibc
from ib_insync import Stock, CFD
import pandas as pd
import math
from config import load_credentials
from modules.trade.utils import floor_round, ceil_round
ACCOUNT = load_credentials('monday')

today_str = datetime.datetime.now().strftime('%Y%m%d')
print(today_str)
today_str = '20240927'

ibc = ibc.Ib()
ib = ibc.GetIB(5)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# avalible_cash /= 2
avalible_cash = total_cash * 0.5 # margin account
# avalible_cash = min(total_cash * 0.5, avalible_cash/4) # After JP Div
print(avalible_cash)
# sys.exit()
FOLDER = f"{rootPath}/data/dividendHunter"
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
    cStock = Stock(symbol, 'SMART', 'USD')
    cCFD = CFD(symbol, 'SMART', 'USD')
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
    npArr = df.to_numpy()
    closeDict = {}
    for symbol, div, date in npArr:
        if symbol not in divPerDict: continue
        contract = CFD(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        c = ib.reqContractDetails(contract)
        if len(c) < 1: continue
        contract = Stock(symbol, 'SMART', 'USD')
        close = ibc.GetDataNpArr(contract, '1 min')[-1][3]
        closeDict[symbol] = close

    divPerDict = {}
    for symbol, div, date in npArr: 
        if symbol not in closeDict: continue
        divPer = div / closeDict[symbol]
        divPerDict[symbol] = [closeDict[symbol], div, divPer]
    divPerDict = dict(sorted(divPerDict.items(), key=lambda item: item[1][2], reverse=True))
    return divPerDict

def GetCall(chains, price):
    for optionschain in chains:
        strikeList = optionschain.strikes
        for expir in optionschain.expirations:
            if expir != today_str: break
        for strike in strikeList:
            if strike >= price + 0.5:
                optionContract = ibc.GetOptionCallContract(symbol, expir, strike)
                npArrBid = ibc.GetDataNpArr(optionContract, '1 min', 'BID')
                if len(npArrBid) < 1: return 0, 0, 0, 0, 0
                npArrAsk = ibc.GetDataNpArr(optionContract, '1 min', 'ASK')
                if len(npArrAsk) < 1: return 0, 0, 0, 0, 0
                bid = npArrBid[-1][3]
                ask = npArrAsk[-1][3]
                spread = ask - bid
                # if spread > 0.6: return 0, 0, 0, 0
                return bid, ask, spread, expir, strike
    return 0, 0, 0, 0, 0
# https://www.nasdaq.com/market-activity/dividends
exDate = datetime.date(2024, 9, 27)

# Format the date as YYYYMMDD
formatted_date = exDate.strftime("%Y%m%d")

div_per_filename = f"{FOLDER}/DividendHunter_{formatted_date}.csv"
ex_filename = f"{FOLDER}/exdividend_{formatted_date}.csv"

if not os.path.exists(div_per_filename) or True:
    if not os.path.exists(ex_filename):
        # If the file doesn't exist, get the dividend data
        npArr = GetExDividendWithPayment(exDate)
        
        # Create a DataFrame
        df = pd.DataFrame(npArr, columns=["symbol", "div", "paymentDate"])
        
        # Save the DataFrame to a CSV file with the dynamic filename
        df.to_csv(ex_filename, index=False)
        print(f"Data saved to {ex_filename}")
    else:
        df = pd.read_csv(ex_filename)
        
        # Convert the DataFrame back to a NumPy array
        npArr = df.to_numpy()

    closeDict = {}
    for symbol, div, date in npArr:
        # contract = CFD(symbol, 'SMART', 'USD')
        # ib.qualifyContracts(contract)
        # c = ib.reqContractDetails(contract)
        # if len(c) < 1: continue
        # chains = ibc.GetChains(symbol)
        # if len(chains) < 1: continue
        contract = Stock(symbol, 'SMART', 'USD')
        arr = ibc.GetDataNpArr(contract, '1 min')
        if len(arr) < 1: continue
        close = arr[-1][3]
        closeDict[symbol] = close

    divPerDict = {}
    for symbol, div, date in npArr: 
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
    divPerDict = {row["symbol"]: [row["close"], row["div"], row["divPer"]] for _, row in divPer_df.iterrows()}

print(divPerDict)
print(avalible_cash)
# divPerDict = UpdateDivPer(ex_filename, divPerDict)
# print(divPerDict)

for symbol, data in divPerDict.items():
    close = data[0]
    div = data[1]
    print(f"Symbol: {symbol}, Close: {close},  Div: {div}")
    sharesToBuy = floor_round(int(avalible_cash / close), 100)
    if sharesToBuy < 100: continue
    multiplier = sharesToBuy / 100
    totalDivs = sharesToBuy * div
   
    spreadStock = 0.01
    spreadCFD = 0.01

    spreadStock, spreadCFD, ask, bid, cStock, cCFD = GetStockCFDSpread(symbol)
    # print(spreadStock, spreadCFD)
    if math.isnan(spreadStock): continue
    if spreadStock <= 0: continue
    commissionAndSpread = (1 + (spreadStock) * sharesToBuy) * 2
    profit = totalDivs - commissionAndSpread
    chains = ibc.GetChains(symbol)
    # bid, ask, spread, expir, strike = GetCall(chains, close)
    # if bid <= 0.05: continue
    # print(symbol, bid, expir, strike)
    # option_cost = (ask * multiplier * 100 + 4)
    if profit > 4.25:
        print(symbol, "PROFIT: ", profit)
        # if profit <= 0: continue
        print(f"Symbol: {symbol}")
        print(f"Shares to Buy: {sharesToBuy}")
        print(f"Total Dividends: ${totalDivs:,.2f}")
        print(f"Commssion & Spread: ${-commissionAndSpread:,.2f}")
        # print(f"Protective Puts & Spread: ${-option_cost}")
        print(f"Profit: ${profit:,.2f}")
        # if profit > 3.17:
        # if profit > 4.25:
            
        # SubmitOrder(symbol, sharesToBuy, ask, bid, cStock, cCFD)
        break

    