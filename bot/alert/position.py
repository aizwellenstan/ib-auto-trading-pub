import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.discord import Alert
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

keepOpenList = ['XLY']
# keepOpenList = ['QQQ','DIA','APTS','SRLN','SPY','XLY']
   
def checkLoss():
    portfolio = ib.portfolio()
    for sPortfolio in portfolio:
        symbol = sPortfolio.contract.symbol
        if symbol in keepOpenList: continue
        pnl = sPortfolio.unrealizedPNL
        position = sPortfolio.position
        basePnl = pnl/position

        if basePnl < maxLoss:
            message = f"{symbol} {pnl} maxLoss Hit Get Out!"
            Alert(message)
        else:
            print(f"{symbol} {pnl}")

def main():
    while(ib.sleep(1)):
        checkLoss()

if __name__ == '__main__':
    main()