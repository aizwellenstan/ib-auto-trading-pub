from ib_insync import *

class Trading():
    def __init__(self, clientId=1, tickers=[]):
        self.dataStreams = {}
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=clientId)
        self.clientId = clientId
        self.tickers = tickers
    
    def _stream_data(self):
        for ticker in self.tickers:
            stock = Stock(ticker, 'SMART', 'JPY')
            stream = self.ib.reqMktData(stock, '', False, False)
            self.dataStreams[ticker] = stream
            self.ib.sleep(1)

    def start(self):
        self._stream_data()

if __name__ == "__main__":
    strategy = Trading(1, ["9101", "7203"])
    strategy.start()
    print(strategy.dataStreams["9101"].last)
