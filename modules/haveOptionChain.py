import yfinance as yf

def haveOptionChain(symbol):
    haveOptionChain = False
    try:
        stockInfo = yf.Ticker(symbol)
        optionChain=list(stockInfo.options)
        if len(optionChain) > 0:
            haveOptionChain = True
    except:
        return haveOptionChain
    return haveOptionChain