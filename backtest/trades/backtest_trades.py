import pandas as pd
import json

df = pd.read_csv (r'../csv/trades/0628_gap.csv', index_col=0)
df.drop
gaps = json.loads(df.to_json(orient = 'records'))
gapList   = []
for i in gaps:
    gapList.append(i['symbol'])

df = pd.read_csv (r'../csv/trades/trades_0628.csv')
df.drop
trades = json.loads(df.to_json(orient = 'records'))
tradesList   = []
for i in trades:
    sym = i['symbol'].strip()
    tradesList.append(sym)

finalList = []

for i in tradesList:
    if i in gapList:
        finalList.append(i)

df = pd.read_csv (r'../csv/livetradersSym.csv')
df.drop
syms = json.loads(df.to_json(orient = 'records'))
symList   = []
for i in syms:
    symList.append(i['symbol'])

print(symList)

goodScanList = []

for i in finalList:
    if i not in symList:
        goodScanList.append(i)

gain = ['NTLA', 'AVXL', 'EDIT', 'ALF', 'CRSP', 'CCXI', 'PSFE', 'CCIV', 'RUN', 'RIOT', 'MARA', 'NGCA', 'SPCE', 'SOXL', 'AMC', 'NIO']
print(len(gain))
# gain = ['NTLA', 'AVXL', 'EDIT', 'ALF', 'CRSP', 'CCXI', 'PSFE', 'CCIV', 'RUN', 'ARKG', 'RIOT', 'MARA', 'NGCA', 'ARKK', 'SPCE', 'SOXL', 'AMC', 'NIO', 'CLF', 'VIAC', 'VIPS', 'LI', 'TQQQ', 'NEE', 'X', 'VALE', 'INTC', 'AMD', 'PLTR', 'MU', 'PLUG', 'CLOV', 'MSFT', 'QQQ', 'GOLD', 'AAPL', 'FCX', 'SPY', 'SONY', 'GE', 'UBER', 'GLD']
vol = ['SKM', 'NTLA', 'VWOB', 'PKX', 'SOFI', 'AVXL', 'NGCA', 'EDIT', 'BEKE', 'SONY', 'BEAM', 'CRSP', 'ASHR', 'IWB', 'PSAC', 'SPCE', 'CUK', 'EXEL', 'BZ', 'ARKG', 'ALF', 'HTA', 'UNG', 'IXC', 'CCXI', 'CCL', 'PSFE', 'NVS', 'TTD', 'MOXC', 'PBCT', 'LI',
'LABU', 'VOD', 'PBF', 'WISH', 'DM', 'CCIV', 'TCOM', 'NRG', 'LU', 'GLD', 'NEE', 'JETS', 'RUN', 'ME', 'BP', 'PATH', 'RCL', 'CLVT']
active = ['SOFI', 'SPCE', 'AMC', 'BEKE', 'CCL', 'ALF', 'WISH', 'NTLA', 'F', 'AAPL',
'CLOV', 'AVXL', 'PLTR', 'LI', 'ASHR', 'SPY', 'WFC', 'XLF', 'NIO', 'BAC', 'FCX', 'CCIV', 'AAL', 'SKM', 'EDIT', 'IWM', 'PSFE', 'BB', 'VIAC', 'QQQ', 'MU', 'BP', 'CLF', 'BZ', 'NCLH', 'MSFT', 'PBR', 'TQQQ', 'AMD', 'BA', 'ARKG', 'GE', 'CRSP', 'GLD', 'PLUG', 'X', 'OXY', 'MARA', 'NGCA', 'VIPS']
scanner = gain+vol+active

badList = []
for i in tradesList:
    if i not in symList:
        if i not in gapList:
            if i not in symList:
                if i not in gain:
                    badList.append(i)
# print(badList)

symList = ['AAP', 'AAPL', 'AERI', 'AIG', 'AMGN', 'ATVI', 'BABA', 'BILI', 'BYND', 'CAH', 'CRWD', 'CVS', 'DDD', 'DLTR', 'ETSY', 'FSLY', 'GILD', 'GM', 'HAS', 'INTC', 'MRK',
'MRNA', 'NIO', 'NTAP', 'PLAY', 'PM', 'PTON', 'QCOM', 'SNAP', 'SPOT', 'SYF', 'SYNA', 'T', 'TDOC', 'TRIP', 'TSN', 'URBN',
'V', 'WMB', 'WMT', 'WSM', 'XLNX']

gainTLst = []
for i in tradesList:
    if i not in symList:
        gainTLst.append(i)

print(gainTLst)
