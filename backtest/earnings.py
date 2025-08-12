rootPath = ".."
import sys
sys.path.append(rootPath)
import modules.income as yfincome
import modules.aiztradingview as aiztradingview

def CheckSeiChouRitsu(symbol, close):
    income = yfincome.GetIncome(symbol)
    if len(income) < 4: return False
    print(income)
    if income[1][1] < 1: return False
    if income[3][1] < 1: return False
    cp = income[0][1] / close
    if cp <= 101935483.87096775: return False
    if income[1][1] < income[2][1]: return False
    return True

closeDict = aiztradingview.GetClose()
passedList = []
for symbol, close in closeDict.items():
    if (CheckSeiChouRitsu(symbol,close)):
        print(symbol)
        passedList.append(symbol)

closeDictJP = aiztradingview.GetCloseJP()
for symbol, close in closeDictJP.items():
    if (CheckSeiChouRitsu(symbol+".T",close)):
        print(symbol)
        passedList.append(symbol)
print(passedList)

# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=financialData%2CdefaultKeyStatistics
# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=incomeStatementHistory
# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=incomeStatementHistoryQuarterly
# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=earningsHistory
# https://query2.finance.yahoo.com/v10/finance/quoteSummary/aapl?formatted=true&modules=earnings
# modules = [
#        'assetProfile',
#        'summaryProfile',
#        'summaryDetail',
#        'esgScores',
#        'price',
#        'incomeStatementHistory',
#        'incomeStatementHistoryQuarterly',
#        'balanceSheetHistory',
#        'balanceSheetHistoryQuarterly',
#        'cashflowStatementHistory',
#        'cashflowStatementHistoryQuarterly',
#        'defaultKeyStatistics',
#        'financialData',
#        'calendarEvents',
#        'secFilings',
#        'recommendationTrend',
#        'upgradeDowngradeHistory',
#        'institutionOwnership',
#        'fundOwnership',
#        'majorDirectHolders',
#        'majorHoldersBreakdown',
#        'insiderTransactions',
#        'insiderHolders',
#        'netSharePurchaseActivity',
#        'earnings',
#        'earningsHistory',
#        'earningsTrend',
#        'industryTrend',
#        'indexTrend',
#        'sectorTrend']

# rootPath = ".."
# import sys
# sys.path.append(rootPath)
# import modules.aizyfinance as si
# earnings_hist = si.get_earnings_history("aapl")
# print(earnings_hist)

# rootPath = ".."
# import sys
# sys.path.append(rootPath)
# import modules.alphavantage as alphavantage
# import pandas as pd
# import modules.aiztradingview as aiztradingview

# def GetLargestEPSQuater(symbol):
#     # try:
#     #     earnings = alphavantage.earnings_history_api(symbol)
#     #     df = pd.DataFrame(earnings)
#     #     df = df[['reportedDate','reportedEPS']]
#     #     df['reportedDate'] = pd.to_datetime(df['reportedDate'])
#     #     df['year'] = df['reportedDate'].dt.year
#     #     df['quarter'] = df['reportedDate'].dt.quarter
#     #     df['reportedEPS'] = pd.to_numeric(df['reportedEPS'], errors='coerce')
#     #     # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     #     #    print(df)
#     #     # calculate the previous year
#     #     previous_year = df['year'].max() - 1

#     #     # filter the dataframe to include only data from the previous year
#     #     prev_year_df = df[df['year'] == previous_year]

#     #     all_positive_eps = (prev_year_df['reportedEPS'] > 0).all()

#     #     if not all_positive_eps: return 0

#     #     # group the filtered dataframe by quarter and find the largest reportedEPS for each group
#     #     largest_eps_per_quarter = prev_year_df.groupby('quarter')['reportedEPS'].max()

#     #     # # get the top quarter(s) with the largest EPS values
#     #     # n_largest_quarters = 2
#     #     # largest_quarters = largest_eps_per_quarter.nlargest(n_largest_quarters)

#     #     # # get the index value of the first row of the largest_quarters series
#     #     # largest_quarter_number = largest_quarters.index[0]

#     #     # # check if the two largest quarters have the same EPS value
#     #     # if len(largest_quarters.unique()) == 1:
#     #     #     largest_quarter_number = 0
#     #     largest_quarter = largest_eps.sort_values(ascending=False).index[0]

#     #     # if there are two or more quarters with the same largest EPS value
#     #     if largest_eps.nlargest(2).tolist()[0] == largest_eps.nlargest(2).tolist()[1]:
#     #         # check if the two quarters belong to the same year or different years
#     #         if largest_eps.nlargest(2).index.tolist()[0] // 4 == largest_eps.nlargest(2).index.tolist()[1] // 4:
#     #             # if they belong to the same year, return the largest quarter number
#     #             return largest_quarter
#     #         else:
#     #             return 0

#     #     # print the result
#     #     print(symbol,largest_quarter)
#     #     return largest_quarter
#     # except: return 0
#     earnings = alphavantage.earnings_history_api(symbol)
#     df = pd.DataFrame(earnings)
#     df = df[['reportedDate','reportedEPS']]
#     df['reportedDate'] = pd.to_datetime(df['reportedDate'])

#     # group 'reportedEPS' by year and convert the result to a NumPy array
#     result = df.groupby(df['reportedDate'].dt.year)['reportedEPS'].apply(np.array).values

#     # print the result
#     print(result)
    

# earningsList = aiztradingview.GetRecentEarnings()
# for symbol in earningsList:
#     largestEPSQuater = GetLargestEPSQuater(symbol)
#     if largestEPSQuater == 1:
#         print(symbol)

# GetLargestEPSQuater("AAPL")