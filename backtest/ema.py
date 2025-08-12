rootPath = "../"
import sys
sys.path.append(rootPath)
import os
import pandas as pd
from modules.data import GetNpData
from modules.movingAverage import EmaArr


portfolioPath = f"{rootPath}/data/GurosuLts.csv"

portfolioList = []
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    portfolioList = list(df.Symbol.values)

print(portfolioList)

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
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV',
    'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    'V','CAT','MRNA','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    'VIX',
    'COIN',
]

tradable = []
for option in topOption:
    if option in portfolioList:
        tradable.append(option)

print(tradable)

# symbol = "SPY"

total = 1
# for symbol in portfolioList:
symbol = "V"
npArr = GetNpData(symbol)
# if len(npArr) < 1: continue
closeArr = npArr[:, 3]

ema200 = EmaArr(closeArr, 200)
ema100 = EmaArr(closeArr, 100)
ema50 = EmaArr(closeArr, 50)
ema30 = EmaArr(closeArr, 30)
ema20 = EmaArr(closeArr, 20)
ema10 = EmaArr(closeArr, 10)
ema5 = EmaArr(closeArr, 5)

for i in range(1, len(npArr)):

    if (
        # closeArr[i-1] > ema200[i-1] and
        # closeArr[i-1] < ema100[i-1] and
        # closeArr[i-1] < ema50[i-1] and
        # closeArr[i-1] < ema30[i-1] and
        # closeArr[i-1] < ema20[i-1] and
        closeArr[i-1] < ema10[i-1]
        # closeArr[i-1] < ema5[i-1]
    ):
        if npArr[i][0] == 0: continue
        gain = npArr[i][3] / npArr[i][0]
        total *= gain
print('{0:.10f}'.format(total))

# print(ema200)
