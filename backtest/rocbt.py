import backtrader as bt
import yfinance as yf
import numpy as np
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import datetime

class HiddenMarkovModel(bt.Indicator):
    lines = ('prob_positive', 'prob_negative')
    params = (('window_size', 150), ('n_components', 3))

    def __init__(self):
        self.model = None
        self.scaler = None
        self.addminperiod(self.p.window_size)

    def next(self):
        if len(self.data) < self.p.window_size:
            return
        
        # Calculate ROC
        roc = self.data.close.pct_change(periods=1)
        roc = roc[-self.p.window_size:].values.reshape(-1, 1)

        if self.model is None:
            self.model = hmm.GaussianHMM(n_components=self.p.n_components, n_iter=100, random_state=100)
            self.scaler = StandardScaler()
            scaled_roc = self.scaler.fit_transform(roc)
            self.model.fit(scaled_roc)
        else:
            scaled_roc = self.scaler.transform(roc)
            probs = self.model.predict_proba(scaled_roc[-1].reshape(1, -1))
            self.lines.prob_positive[0] = probs[0][2]
            self.lines.prob_negative[0] = probs[0][0]

class HMMStrategy(bt.Strategy):
    params = (
        ('window_size', 150),
        ('n_components', 3),
        ('buy_weight', 0.1),
        ('sell_weight', -0.1),
    )

    def __init__(self):
        self.roc_indicators = {}
        for data in self.datas:
            # Initialize the HiddenMarkovModel indicator with the data close prices
            self.roc_indicators[data] = HiddenMarkovModel(data=data.close, window_size=self.p.window_size, n_components=self.p.n_components)

    def next(self):
        for data in self.datas:
            roc_indicator = self.roc_indicators[data]
            if roc_indicator.lines.prob_positive[0] > roc_indicator.lines.prob_negative[0]:
                self.order_target_percent(data, self.p.buy_weight)
            else:
                self.order_target_percent(data, self.p.sell_weight)

def fetch_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date, interval='5m')
        df.reset_index(inplace=True)
        df.set_index('Datetime', inplace=True)
        data[ticker] = bt.feeds.PandasData(dataname=df)
    return data

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Define the list of top 10 tickers (you can change these)
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'UNH', 'V']

    # Fetch historical data
    data = fetch_data(tickers, '2024-08-01', '2024-09-07')

    # Add data to cerebro
    for ticker in tickers:
        cerebro.adddata(data[ticker], name=ticker)

    # Add strategy to cerebro
    cerebro.addstrategy(HMMStrategy)

    # Set initial cash and run backtest
    cerebro.broker.set_cash(100000)
    cerebro.run()

    # Plot results
    cerebro.plot()
