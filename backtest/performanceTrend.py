import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.holdings import GetHoldings
from modules.data import GetDf
from modules.movingAverage import SmaArr
from modules.aiztradingview import GetSectorIndustry, GetPerformance, GetAttr, GetTrend
import pickle
import gc

etfs = ['XLE','XLU','XLP','XLV','XLI','XLK','XLY','XLF']

def updateData(etfs):
    for etf in etfs:
        etfdf = GetDf(etf)
        holdings = GetHoldings(etf)
        for symbol in holdings:
            df = GetDf(symbol)
            print(etf,symbol)

def getDataDict(etfs, performanceList, update):
    days = 1000
    dataDict = {}
    for etf in etfs:
        etfdf = GetDf(etf, update=update)
        etfdf = etfdf[['Open','High','Low','Close','Vwap']]
        etfdf = etfdf.tail(days)
        etfNpArr = etfdf.to_numpy()
        dataDict[etf] = etfNpArr
        holdings = GetHoldings(etf)
        for symbol in holdings:
            df = GetDf(symbol, update=update)
            if len(df) < 1000: continue
            closeArr = df.Close.values
            # Sma75 = SmaArr(closeArr,25)
            # df['Sma75'] = Sma75
            # df = df[['Open','High','Low','Close','Vwap','Sma75']]
            df = df[['Open','High','Low','Close','Volume','Vwap']]
            df = df.tail(days)
            npArr = df.to_numpy()
            dataDict[symbol] = npArr

    
    for symbol in performanceList:
        try:
            df = GetDf(symbol, update=update)
            if len(df) < 1000: continue
            closeArr = df.Close.values
            Sma25 = SmaArr(closeArr,25)
            df['Sma25'] = Sma25
            Sma75 = SmaArr(closeArr,75)
            df['Sma75'] = Sma75
            df = df[['Open','High','Low','Close','Volume','Vwap','Sma25','Sma75']]
            # df = df[['Open','High','Low','Close','Volume','Vwap']]
            df = df.tail(days)
            npArr = df.to_numpy()
            dataDict[symbol] = npArr
        except: pass

    return dataDict

def GetTradableSectorIndustry(etfs):
    tradableSectorDict = {}
    tradableIndustryDict = {}
    for etf in etfs:
        tradableSectorList = []
        tradableIndustryList = []
        holdings = GetHoldings(etf)
        for symbol in holdings:
            if symbol in sectorDict:
                sector = sectorDict[symbol]
                if sector not in tradableSectorList:
                    tradableSectorList.append(sector)
            if symbol in industryDict:
                industry = industryDict[symbol]
                if sector not in tradableIndustryList:
                    tradableIndustryList.append(industry)
        tradableSectorDict[etf] = tradableSectorList
        tradableIndustryDict[etf] = tradableIndustryList
    return tradableSectorDict, tradableIndustryDict

topOption = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY'
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV'
]

performanceList = GetTrend()

# newPerformanceList = []
# data = open("./pickle/option.p", "rb")
# gc.disable()
# option = pickle.load(data)
# data.close()
# gc.enable()

# for symbol in performanceList:
#     if symbol in option:
#         newPerformanceList.append(symbol)
# performanceList = newPerformanceList
# dataDict = getDataDict(etfs, performanceList, True)
# pickle.dump(dataDict, open("./pickle/dataDict.p", "wb"))

data = open("./pickle/dataDict.p", "rb")
gc.disable()
dataDict = pickle.load(data)
data.close()
gc.enable()
# print(dataDict)

sectorDict, industryDict = GetSectorIndustry()
tradableSectorDict, tradableIndustryDict = GetTradableSectorIndustry(etfs)
# performanceList = GetPerformance()

holdingsDict = {}
for etf in etfs:
    holdings = GetHoldings(etf)
    holdingsDict[etf] = holdings
    # for symbol in holdings:
    #     if symbol not in performanceList:
    #         print(f"{symbol} not in list")
            # performanceList.append(symbol)

attrDict = GetAttr()

newAttrDict = {}
for symbol in performanceList:
    if symbol in attrDict:
        attr = attrDict[symbol]
        if attr > 0:
            newAttrDict[symbol] = attrDict[symbol]

attrList = list(newAttrDict.values())
newAttrList = []
for attr in attrList:
    if attr not in newAttrList:
        newAttrList.append(attr)
attrList = newAttrList
attrList.sort()
# attrList.sort(reverse=True)

# import yfinance as yf
# for symbol in performanceList:
#     try:
#         stockInfo = yf.Ticker(symbol)
#         optionChain=list(stockInfo.options)
#         if len(optionChain) > 0:
#             newPerformanceList.append(symbol)
#     except: continue
#     performanceList = newPerformanceList
# pickle.dump(performanceList, open("./pickle/option.p", "wb"))

maxAttr = 0
maxGain = 0
maxDay = 0
day = 34
performanceVal = 0.88
days = 1000
# for attrVal in attrList:
# biasVal = 0
# while biasVal < 20:
#     biasVal += 0.001
gain = 1
for i in range(367, days-1):
    performanceDict = {}
    for etf in etfs:
        npArr = dataDict[etf]
        etfperformance = npArr[i-1][3] / npArr[i-day][3]
        performanceDict[etf] = etfperformance
    performanceDict = dict(sorted(performanceDict.items(), key=lambda item: item[1], reverse=True))
    etf = next(iter(performanceDict))
    tradableSectorList = tradableSectorDict[etf]
    tradableIndustryList = tradableIndustryDict[etf]
    holdings = holdingsDict[etf]
    holdingsPerformanceDict = {}
    for symbol in performanceList:
        if symbol not in dataDict: continue
        attr = attrDict[symbol]
        # if attr < attrVal: continue
        # if attr > attrVal: continue
        # if symbol not in holdings: continue
        sector = sectorDict[symbol]
        industry = industryDict[symbol]
        if sector not in tradableSectorList: continue
        if industry not in tradableIndustryList: continue
        npArr = dataDict[symbol]
        performance = npArr[i-1][3] / npArr[i-day][3]
        if performance > etfperformance * performanceVal:
            bias25 = (npArr[i-1][3] - npArr[i-1][6]) / npArr[i-1][6]
            bias75 = (npArr[i-1][3] - npArr[i-1][7]) / npArr[i-1][7]
            if bias25 > 0.232: continue
            # if bias25 < -0.074: continue
            # if bias75 > 0.42: continue
            # if bias75 < -0.347: continue
            if (
                npArr[i-1][3] / npArr[i-1][5] > 21.3
            ): continue
            if (
                npArr[i-1][3] < npArr[i-2][3] and
                npArr[i-1][3] < npArr[i-1][0]
            ):
                gain *= npArr[i][3] / npArr[i][0]
                # holdingsPerformanceDict[symbol] = performance
                # break
    # holdingsPerformanceDict = dict(sorted(holdingsPerformanceDict.items(), key=lambda item: item[1], reverse=True))
    # if len(holdingsPerformanceDict) > 0:
    #     topPeformanceSymbol = next(iter(holdingsPerformanceDict))
    #     npArr = dataDict[topPeformanceSymbol]
    #     gain *= npArr[i][3] / npArr[i][0]
    
    
print(gain)
if gain > maxGain:
    # maxAttr = biasVal
    maxGain = gain
    maxDay = day
    minPerformanceVal = performanceVal
print(f"maxAttr {maxAttr} maxGain {'{0:.10f}'.format(maxGain)} maxDay {maxDay} minPerformanceVal {minPerformanceVal}")

# shareholders >= 339, 34945.84820849877
# average_volume_90d_calc >= 1299330, 321.1830735445045
# market_cap_basic >= 1339896162, 2564.296234838704
# number_of_employees >= 326, 1954.3048912364125
# total_assets >= 226443830, 2506.9270240145
# total_current_assets >= 227375000, 2046.235964589863
# close >= 16.75, 8981.225081841152
# float_shares_outstanding >= 218684869, 2042.0450560394793
# ADR >= 0.86, 4344.67606733778
# ATR >= 0.70, 5780.613075826233
## basic_eps_net_income >= 0.7645, 9780.570358591904
# earnings_per_share_basic_ttm >= 0.5456, 8856.289907844997
# dividends_paid <= -101000000, 2047.1090249703857
# dps_common_stock_prim_issue_fy >= 0.18, 2619.1816285406803
# dividends_per_share_fq >= 0.077222
# dividend_yield_recent >= 0.21287543, 2619.1816285406803
# ebitda >= 3533000, 8751.911632440271
# enterprise_value_fq >= 5601990000, 2279.4604417052587
# last_annual_eps >= 0.7811, 9780.570358591904
# earnings_per_share_fq >= 0.005441, 2544.1568570810614
# earnings_per_share_diluted_ttm >= 0.5326, 8393.049796150422
# gross_margin >= 2.67759841, 712.0755830483724
# gross_profit >= 215500000, 1560.9474332424475
# gross_profit_fq >= 364000000, 1715.520124859307
# last_annual_revenue >= 8729000000, 2057.6333645159757
# net_income >= 2855066, 3326.799871151198
# after_tax_margin >= 4.39172448, 6959.538808395454
# pre_tax_margin >= 5.07084265, 6248.7139249793045
# return_on_assets >= 0.02939273, 6206.601007894087
# return_on_equity >= 2.67536732, 4179.20454334552
# return_on_invested_capital >= 2.36569341, 6394.299419560129
# revenue_per_employee >= 249023.47826087, 7471.920286016769
# total_revenue >= 8729000000, 2057.6333645159757
# total_shares_outstanding_fundamental >= 218244000, 2065.3309695317225
# Value.Traded >= 57236067.3, 1839.6911010165388

# goodwill >= 99175000, 265.41353737845236

# current_ratio >= 0.64868106, 3.0675845808918596
# debt_to_equity <= 2.67774816, 2.4286228324616133
# enterprise_value_ebitda_ttm <= 33.8957842, 2.5441918254382228
# net_debt <= 535004000000, 2.223098377118563
# price_book_ratio <= 4.29286465, 2.714232215516779
# price_book_fq <= 3.09823, 3.863251908682038
# price_earnings_ttm <= 47.41117607, 3.3061082302219797
# price_free_cash_flow_ttm <= 73.8309, 2.323617668472334
# price_revenue_ttm <= 7.49107214, 14.689362380360796
# price_sales_ratio <= 8.07224328, 17.722364742509857
# quick_ratio >= 0.48312137, 2.52236681350468
# ROC >= 0.49833887, 62.77669709622092
# total_debt <= 588319000000, 2.223098377118563
# total_liabilities_fy <= 3449440000000, 2.223098377118562
# total_liabilities_fq <= 3555171000000, 2.223098377118563
# Volatility.M >= 2.4341937070603548