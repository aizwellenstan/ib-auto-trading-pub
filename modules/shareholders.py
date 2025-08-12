from yahooquery import Ticker
import sys
def NormalizeFloat(num):
    try:
        return float(num)
    except ValueError:
        return 0.0

def GetShareholders(ticker :str):
    try:
        t = Ticker(ticker)
        shareholders = t.major_holders
        return shareholders[ticker]
    except:
        pass

def GetInsiderPercent(ticker :str):
    try:
        t = Ticker(ticker)
        shareholders = t.major_holders
        insiderPercent = shareholders[ticker]["insidersPercentHeld"]
        return insiderPercent
    except:
        return 1

def GetPercentHeld(ticker :str):
    try:
        t = Ticker(ticker)
        shareholders = t.major_holders
        percentHeld = shareholders[ticker]["institutionsPercentHeld"]
        return percentHeld
    except:
        return 0

def GetFloatPercentHeld(ticker :str):
    try:
        t = Ticker(ticker)
        shareholders = t.major_holders
        floatPercentHeld = shareholders[ticker]["institutionsFloatPercentHeld"]
        return floatPercentHeld
    except:
        return 0

def GetInstitutions(ticker :str):
    try:
        t = Ticker(ticker)
        shareholders = t.major_holders
        institutions = shareholders[ticker]["institutionsCount"]
        return institutions
    except:
        return 0

def GetX1(ticker :str):
    try:
        t = Ticker(ticker)
        balanceSheetHistory = t.get_modules('balanceSheetHistory')[ticker]['balanceSheetStatements'][0]
        currentAssets = balanceSheetHistory['totalCurrentAssets']
        currentLiabilities = balanceSheetHistory['totalCurrentLiabilities']
        totalAssets = balanceSheetHistory['totalAssets']
        x1 = (currentAssets-currentLiabilities)/totalAssets
        return x1
    except:
        return 0

def GetX2(ticker :str):
    try:
        t = Ticker(ticker)
        balanceSheetHistory = t.get_modules('balanceSheetHistory')[ticker]['balanceSheetStatements'][0]
        totalAssets = balanceSheetHistory['totalAssets']
        retainedEarnings = balanceSheetHistory['retainedEarnings']
        x2 = retainedEarnings / totalAssets
        return x2
    except:
        return 0

def GetX3(ticker :str):
    try:
        t = Ticker(ticker)
        balanceSheetHistory = t.get_modules('balanceSheetHistory')[ticker]['balanceSheetStatements'][0]
        totalAssets = balanceSheetHistory['totalAssets']
        incomeStatementHistory = t.get_modules('incomeStatementHistory')[ticker]['incomeStatementHistory'][0]
        ebit = incomeStatementHistory['ebit']
        x3 = ebit / totalAssets
        return x3
    except:
        return 0

def GetZScore(ticker :str):
    try:
        t = Ticker(ticker)
        balanceSheetHistory = t.get_modules('balanceSheetHistory')[ticker]['balanceSheetStatements'][0]
        if "totalCurrentAssets" in balanceSheetHistory:
            currentAssets = balanceSheetHistory['totalCurrentAssets']
        else: currentAssets = 0
        currentLiabilities = balanceSheetHistory['totalCurrentLiabilities']
        if "totalAssets" in balanceSheetHistory:
            totalAssets = balanceSheetHistory['totalAssets']
        else: totalAssets = 1
        x1 = (currentAssets - currentLiabilities) / totalAssets
        if "retainedEarnings" in balanceSheetHistory:
            retainedEarnings = balanceSheetHistory['retainedEarnings']
        else: retainedEarnings = 0
        x2 = retainedEarnings / totalAssets
        incomeStatementHistory = t.get_modules('incomeStatementHistory')[ticker]['incomeStatementHistory'][0]
        ebit = incomeStatementHistory['ebit']
        x3 = ebit / totalAssets
        summary = t.summary_detail[ticker]
        marketcap = summary['marketCap']
        totalLiabilities = balanceSheetHistory['totalLiab']
        if totalLiabilities == 0: totalLiabilities = 1
        x4 = marketcap / totalLiabilities
        if "priceToSalesTrailing12Months" in summary:
            priceToSalesTrailing12Months = summary['priceToSalesTrailing12Months']
            if priceToSalesTrailing12Months == 0: priceToSalesTrailing12Months = 1
        else: priceToSalesTrailing12Months = 1
        sales = marketcap / priceToSalesTrailing12Months
        x5 = sales / totalAssets
        z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + x5
        return (z, x1, x2, x3, x4, x5)
    except:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        return (0.0,0.0,0.0,0.0,0.0,0.0)

def GetOperatingCash(ticker :str):
    try:
        t = Ticker(ticker)
        data = t.all_modules[ticker]
        assetProfile = data['cashflowStatementHistory']
        auditRisk = assetProfile['cashflowStatements'][0]['totalCashFromOperatingActivities']
        return auditRisk
    except:
        return 0

def GetAuditRisk(ticker :str):
    try:
        t = Ticker(ticker)
        data = t.all_modules[ticker]
        assetProfile = data['defaultKeyStatistics']
        auditRisk = assetProfile['enterpriseToRevenue']
        return auditRisk
    except:
        return 0

def GetIncome(ticker :str):
    try:
        t = Ticker(ticker)
        data = t.all_modules[ticker]
        cashflowStatementHistory = data['cashflowStatementHistory']
        cashflowStatements = cashflowStatementHistory['cashflowStatements']
        netIncomeHistory = []
        for i in cashflowStatements:
            netIncome = i['netIncome']
            netIncomeHistory.append(netIncome)
        return netIncomeHistory
    except:
        return 0

def CheckIncomeIncrease(ticker):
    try:
        decending = False
        seq = GetIncome(ticker)
        for s in seq:
            if s < 0:
                return False
        decending = all(earlier >= later for earlier, later in zip(seq, seq[1:]))
        return decending
    except: return False

# increase = CheckIncomeIncrease('SOTK')
# print(increase)

# import json

# # data = GetZScore('NTRB')
# data = GetAuditRisk('NTRB')
# print(data)
# json_formatted_str = json.dumps(data, indent=2)

# print(json_formatted_str)
# t = Ticker('AAPL')
# data = t.all_modules
# print(t.all_modules)
# print(t.asset_profile)