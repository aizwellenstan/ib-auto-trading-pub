import time
import asyncio
from ib_insync import *
from datetime import datetime

today = datetime.now().date()
s = '2023-08-10'
s_format = '%Y-%m-%d'
today = datetime.strptime(s, s_format).date()
priceDict = {}
class Trader:
    def __init__(self, ticker):
        self.ticker = ticker

    async def _init(self):
        print('{} started'.format(self.ticker))
        close = await self.op()
        print('{} ended'.format(self.ticker), close)

    async def op(self):
        df = await ib.reqHistoricalDataAsync(
            Stock(self.ticker, 'TSEJ', 'JPY'),
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        op = 0
        if len(df) > 0:
            op = df[-1].open
            print(op)
            print(df[-1])
            if df[-1].date == today:
                priceDict[self.ticker] = op
        return op

async def fetch_tickers():
    return await asyncio.gather(*(asyncio.ensure_future(safe_trader(ticker)) for ticker in ['7203','9101']))

async def safe_trader(ticker):
    async with sem:
        t = Trader(ticker)
        return await t._init()

if __name__ == '__main__':
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)

    start_time = time.time()
    sem = asyncio.Semaphore(1000)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(fetch_tickers())
    print(priceDict)
    print("%.2f execution seconds" % (time.time() - start_time))