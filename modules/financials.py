import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import yfinance as yf

def normalizeSymbol(symbol):
    symbol = symbol.replace(".","-")
    try: 
        int(symbol)
        symbol += ".T"
    except: pass
    return symbol

def getTicker(symbol):
    symbol = normalizeSymbol(symbol)
    ticker = yf.Ticker(symbol)
    return ticker

def GetIncomeStatementQ(symbol):
    ticker = getTicker(symbol)
    incomeStatementQ = ticker.quarterly_income_stmt
    return incomeStatementQ

def GetBalanceSheetQ(symbol):
    ticker = getTicker(symbol)
    balanceSheetQ = ticker.quarterly_balance_sheet
    return balanceSheetQ

def GetInterestExpenseOperatingIncome(symbol):
    try:
        incomeStatementQ = GetIncomeStatementQ(symbol)
        interestExpense = incomeStatementQ.loc['Interest Expense']
        oepratingIncome = incomeStatementQ.loc['Operating Income']
        return interestExpense.to_numpy(), oepratingIncome.to_numpy()
    except:
        return [], []

def GetInventory(symbol):
    ticker = getTicker(symbol)
    balanceSheet = ticker.quarterly_balance_sheet
    inventory = balanceSheet.loc['Inventory']
    return inventory.to_numpy()

def GetNetIncome(symbol):
    ticker = getTicker(symbol)
    incomeStatement = ticker.quarterly_income_stmt
    netIncome = incomeStatement.loc['Net Income']
    return netIncome.to_numpy()

def GetInventoryNetIncome(symbol):
    try:
        ticker = getTicker(symbol)
        balanceSheet = ticker.quarterly_balance_sheet
        inventory = balanceSheet.loc['Inventory']
        incomeStatement = ticker.quarterly_income_stmt
        netIncome = incomeStatement.loc['Net Income']
        return inventory.to_numpy(), netIncome.to_numpy()
    except:
        return [], []

def GetTreasuryShares(symbol):
    try:
        balanceSheetQ = GetBalanceSheetQ(symbol)
        treasuryShares = balanceSheetQ.loc['Treasury Shares Number']
        return treasuryShares.to_numpy()
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetOrdinaryShares(symbol):
    try:
        balanceSheetQ = GetBalanceSheetQ(symbol)
        treasuryShares = balanceSheetQ.loc['Ordinary Shares Number']
        return treasuryShares.to_numpy()
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetTotalShares(symbol):
    try:
        balanceSheetQ = GetBalanceSheetQ(symbol)
        totalShares = balanceSheetQ.loc['Share Issued']
        return totalShares.to_numpy()
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetOperatingInvestmentCashFlow(symbol):
    try:
        ticker = getTicker(symbol)
        cashflow = ticker.cashflow
        operating = cashflow.loc['Operating Cash Flow']
        investment = cashflow.loc['Investing Cash Flow']
        return operating.to_numpy(), investment.to_numpy()
    except:
        return [], []

def GetFreeCashFlow(symbol):
    try:
        ticker = getTicker(symbol)
        cashflow = ticker.cashflow
        freeCashFlow = cashflow.loc['Free Cash Flow']
        return freeCashFlow.to_numpy()
    except:
        return []

if __name__ == "__main__":
    # inventory = GetInventory("9101")
    # print(inventory)
    netIncome = GetNetIncome("9101")
    print(netIncome)