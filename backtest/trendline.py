rootPath = '..'
import sys
sys.path.append(rootPath)
import yfinance as yf
from modules.get_trend_line import find_grad_intercept, findGrandIntercept, GetResistance, GetSupport
from modules.data import GetNpData
import numpy as np


symbol = 'QQQ'
npArr = GetNpData(symbol)
# print(npArr)

# for i in range(1, 1000):
    # -624


# # @njit
def Backtest(npArr):
    resistanceArr = np.empty(0)
    supportArr = np.empty(0)
    for i in range(1, len(npArr)):
        resistance = GetResistance(npArr[0: i])
        support = GetSupport(npArr[0: i])
        resistanceArr = np.append(resistanceArr,resistance)
        supportArr = np.append(supportArr,support)
    
    print(len(npArr),len(resistanceArr))
    npArr = np.c_[npArr,resistanceArr,supportArr]

# Backtest(npArr)

# import sys
# sys.exit(0)

idxs = []
for i in range(len(npArr)):
    idxs.append(i)

npArr = np.c_[npArr,idxs]

maxBalance = 0
maxVal = 0
npArrOrigin = npArr
npArr = npArrOrigin[-624:]
lastResistance = 0
balance = 2700
positions = 0
lastSL = 0
print(len(npArr))
for i in range(len(npArrOrigin)-624, len(npArrOrigin)):
    npArr = npArrOrigin[0: i]
    npArr2 = npArrOrigin[0: i-1]
    resistance = findGrandIntercept(npArr2[:,1])
    if resistance < 0.01: continue
    if positions > 0:
        if lastSL > npArr[-1][2]:
            balance += positions*lastSL
            positions = 0
            lastSL = 0
    if (
        resistance > lastResistance and
        npArr[-1][0] > npArr[-2][3]
    ):
        support = findGrandIntercept(npArr2[:,2])
        if support < 0.01: continue
        if positions < 1:
            op = npArr[-1][0]
            sl = support
            if sl > op: continue
            vol = balance/op
            positions = vol
            balance -= vol * op
            lastSL = sl
        else:
            lastSL = support
    lastResistance = resistance

if positions > 0:
    balance += positions * npArr[-1][0]
print(balance)
if balance > maxBalance:
    maxBalance = balance
print(maxBalance, maxVal)

import sys
sys.exit(0)

df = yf.download('TSLA').reset_index()

# Perform the date filtering to get the plotting df, and the df to get the 
# trend line of
df = (
      df[(df['Date'] > '2020-05-01') & (df['Date'] < '2020-10-01')]
      .reset_index(drop = True)
)
trend_line_df = df[(df['Date'] > '2020-07-13') & (df['Date'] < '2020-08-11')]

# Using the trend-line algorithm, deduce the gradient and intercept terms of
# the straight lines
m_res, c_res = find_grad_intercept(
    'resistance', 
    trend_line_df.index.values, 
    trend_line_df.High.values,
)
m_supp, c_supp = find_grad_intercept(
    'support', 
    trend_line_df.index.values, 
    trend_line_df.Low.values,
)

df = trend_line_df
df = df.assign(ressistance=m_res*trend_line_df.index + c_res)
df = df.assign(support=m_supp*trend_line_df.index + c_supp)
df = df[['ressistance', 'support']]
print(df)
# # Plot the figure with plotly
# layout = go.Layout(
#     title = 'TSLA Stock Price',
#     xaxis = {'title': 'Date'},
#     yaxis = {'title': 'Price'},
# ) 

# fig = go.Figure(
#     layout=layout,
#     data=[
#         go.Candlestick(
#             x = df['Date'],
#             open = df['Open'], 
#             high = df['High'],
#             low = df['Low'],
#             close = df['Close'],
#             name = 'Candlestick chart'
#         ),
#         go.Scatter(
#             x = trend_line_df['Date'],
#             y = m_res*trend_line_df.index + c_res,
#             name = 'Resistance line'
#         ),
#         go.Scatter(
#             x = trend_line_df['Date'],
#             y = m_supp*trend_line_df.index + c_supp,
#             name = 'Support line'
#         ),
#     ]
# )


# fig.update_xaxes(
#         rangeslider_visible = False,
#         rangebreaks = [{'bounds': ['sat', 'mon']}]
#     )
# fig.show()