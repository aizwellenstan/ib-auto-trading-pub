from ib_insync import *
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.discord import Alert

class RiskyOptionsBot:
    #Initialize variables
    def __init__(self):
        print("Options Bot Running, connecting to IB ...")
        #Connect to IB
        try:
            self.ib = IB()
            self.ib.connect('127.0.0.1',7497,clientId=6)
            print("Successfully connected to IB")
        except Exception as e:
            print(str(e))
        print("Running Live")
        self.ib.execDetailsEvent += self.exec_status
        self.queue = 0
        while(self.ib.sleep(1)):
            print("sleep")
            self.checkLoss()

    #Order Status
    def exec_status(self,trade: Trade,fill: Fill):
        print("Filled")
        self.queue = 0

    maxLoss = -10
    keepOpenList = ['XLY']
    # keepOpenList = ['QQQ','DIA','APTS','SRLN','SPY','XLY']
    def checkLoss(self):
        portfolio = self.ib.portfolio()
        if self.queue > 0: return 0
        for sPortfolio in portfolio:
            symbol = sPortfolio.contract.symbol
            if symbol in self.keepOpenList: continue
            pnl = sPortfolio.unrealizedPNL
            position = sPortfolio.position
            basePnl = pnl/position
            action = 'SELL'
            if position < 0:
                position = -position
                action = 'BUY'

            if basePnl < self.maxLoss:
                message = f"{symbol} {pnl} maxLoss Hit Get Out!"
                Alert(message)
                self.options_contract = Contract(conId = sPortfolio.contract.conId)
                self.ib.qualifyContracts(self.options_contract)
                options_order = MarketOrder(action, position, account=self.ib.wrapper.accounts[-1])
                trade = self.ib.placeOrder(self.options_contract, options_order)
                self.queue += 1
            else:
                print(f"{symbol} {pnl}")
                
#Instantiate Class to get things rolling
RiskyOptionsBot()