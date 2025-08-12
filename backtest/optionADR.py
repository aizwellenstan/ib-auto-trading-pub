rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

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
    'META','ARKK','GDX','GLD','SLV'
]

longAdrDict = {}
shortAdrDict = {}

for option in topOption:
    npArr = GetNpData(option)
    longAdrList = []
    shortAdrList = []
    for i in range(0, len(npArr)):
        if npArr[i][3] > npArr[i][0]:
            longAdrList.append(npArr[i][3]/npArr[i][0])
        else:
            shortAdrList.append(npArr[i][3]/npArr[i][0])
    longAdr = sum(longAdrList)/len(longAdrList)
    shortAdr = sum(shortAdrList)/len(shortAdrList)
    longAdrDict[option] = longAdr
    shortAdrDict[option] = shortAdr

longAdrDict = dict(sorted(longAdrDict.items(), key=lambda item: item[1], reverse=True))
shortAdrDict = dict(sorted(shortAdrDict.items(), key=lambda item: item[1], reverse=False))
print(longAdrDict)
print(shortAdrDict)
