from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=5)

maxLoss = -10

def GetPrice(contract):
    contracts = [contract]
    contracts = ib.qualifyContracts(*contracts)
    ticker = ib.reqTickers(*contracts)[0]
    return ticker.bid

def GetPostion():
    portfolio = ib.portfolio()
    for sPortfolio in portfolio:
        print(sPortfolio.contract)

def main():
    GetPostion()

if __name__ == '__main__':
    main()