import yfinance as yf

symbol = "QQQ"
stockInfo = yf.Ticker(symbol)
df = stockInfo.history(period="60d", interval = "1m")
print(df)