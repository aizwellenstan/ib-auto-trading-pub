from modules.aiztradingview import GetAttr
import pandas as pd
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=13)

def GetData(symbol):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='6 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        df = pd.DataFrame(data)
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()
    except:
        return []
    
    return npArr

options = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'ARKK','GDX','GLD','SLV',
    # 'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    # 'V','MRNA','CLAR','SE','ZM','DOCU','SPLK',
    # 'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    # 'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    # 'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    # 'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    # 'VIX',
    # 'COIN'
]

marketCapDict = GetAttr("market_cap_basic")
tradeList = []
for symbol, v in marketCapDict.items():
    if v < 142589022538: continue
    if symbol in options:
        tradeList.append(symbol)

print(tradeList)
gapList = []
for symbol in tradeList:
    npArr = GetData(symbol)
    if len(npArr) < 1: continue
    shift = 3
    if npArr[-1-shift][0] < npArr[-2-shift][1]: continue
    if npArr[-1-shift][0] / npArr[-2-shift][3] > 1.038:
        print(symbol,npArr[-1][0],npArr[-2][3])
        gapList.append(symbol)

print(gapList)

for symbol in tradeList:
    npArr = GetData(symbol)
    if len(npArr) < 1: continue
    shift = 3
    if npArr[-1-shift][0] < npArr[-2-shift][1]: continue
    # if npArr[-1-shift][0] / npArr[-2-shift][3] > 1.038:
    if npArr[-1-shift][0] / npArr[-2-shift][3] < 0.962:
        print(symbol,npArr[-1][0],npArr[-2][3])
        gapList.append(symbol)

print(gapList)