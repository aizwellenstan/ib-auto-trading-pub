rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose
import yfinance as yf
import pandas as pd
from modules.dict import take

def getNpData(symbol):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
    
        df = stockInfo.history(period="12d")
        df = df[['Open','High','Low','Close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def DumpResCsv(resPath, resList):
    df = pd.DataFrame(resList, columns = ['Symbol'])
    df.to_csv(resPath)

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
    'RIVN','LI','GM','WBA','CCJ','NCLH','LCID','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR','BBBY',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV'
]

closeDict = GetClose()

picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDictAll.p"
# pickle.dump(dataDict, open(picklePath, "wb"))
# print("pickle dump finished")

update = False
dataDict = {}
if not update:
    import pickle, gc
    output = open(picklePath, "rb")
    gc.disable()
    dataDict = pickle.load(output)
    output.close()
    gc.enable()
else:
    for symbol, v in closeDict.items():
        npArr = GetNpData(symbol)
        if len(npArr) < 10: continue
        dataDict[symbol] = npArr

period = 1
momentumDict = {}
for symbol, npArr in dataDict.items():
    if symbol not in topOption: continue
    momentum = npArr[-1][3]/npArr[-1-period][3]
    momentumDict[symbol] = momentum

momentumDict = dict(sorted(momentumDict.items(), key=lambda item: item[1]))

print(take(10,momentumDict.items()))
reverseList = momentumDict.keys()
resPath = f'{rootPath}/data/ReverseOption.csv'
DumpResCsv(resPath, reverseList)