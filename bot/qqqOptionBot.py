from datetime import datetime
from ib_insync import *
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.strategy.ema import Signal
from modules.discord import Alert

class RiskyOptionsBot:
    """
    Risky Options Bot (Python, Interactive Brokers)
    Buy 2 DTE SPY Contracts on 3 consecutive 5-min higher closes and profit target on next bar
    """
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
        # Create SPY Contract
        self.underlying = Stock('QQQ', 'SMART', 'USD')
        self.ib.qualifyContracts(self.underlying)
        print("Backfilling data to catchup ...")
        # Request Streaming bars
        self.data = self.ib.reqHistoricalData(self.underlying,
            endDateTime='',
            durationStr='2 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=False,
            keepUpToDate=True,)

        self.in_trade = 0
        self.vol = 2

        #Get current options chains
        self.chains = self.ib.reqSecDefOptParams(self.underlying.symbol, '', self.underlying.secType, self.underlying.conId)
        #Update Chains every hour - can't update chains in event loop causes asyncio issues
        update_chain_scheduler = BackgroundScheduler(job_defaults={'max_instances': 2})
        update_chain_scheduler.add_job(func=self.update_options_chains,trigger='cron', hour='*')
        update_chain_scheduler.start()
        print("Running Live")
        # Set callback function for streaming bars
        self.data.updateEvent += self.on_bar_update
        self.ib.execDetailsEvent += self.exec_status
        #Run forever
        self.ib.run()
        
    #Update options chains
    def update_options_chains(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print("Updating options chains")
             #Get current options chains
            self.chains = self.ib.reqSecDefOptParams(self.underlying.symbol, '', self.underlying.secType, self.underlying.conId)
            print(self.chains)
        except Exception as e:
            print(str(e))

    #On Bar Update, when we get new data
    def on_bar_update(self, bars: BarDataList, has_new_bar: bool):
        try:
            if has_new_bar:
                #Convert BarDataList to pandas Dataframe
                df = util.df(bars)
                signal = Signal(df, self.in_trade)
                print(f"signal {signal}")
                # Check if we are in a trade
                if self.in_trade == 0:
                    print("Last Close : " + str(df.close.iloc[-1]))
                    if signal == 1:
                        #Found 3 consecutive higher closes get call contract that's $5 higher than underlying
                        for optionschain in self.chains:
                            for strike in optionschain.strikes:
                                if strike > df.close.iloc[-1] + 1 : #Make sure the strike is $5 away so it's cheaper
                                    print("Buy")
                                    self.options_contract = Option(self.underlying.symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=self.underlying.symbol)
                                    # We are not in a trade - Let's enter a trade
                                    options_order = MarketOrder('BUY', self.vol,account=self.ib.wrapper.accounts[-1])
                                    trade = self.ib.placeOrder(self.options_contract, options_order)
                                    self.lastEstimatedFillPrice = df.close.iloc[-1]
                                    self.in_trade = 1
                                    message = f"Option Bot Buy {self.options_contract}"
                                    Alert(message)
                                    return # important so it doesn't keep looping
                    elif signal == -1:
                        #Found 3 consecutive higher closes get call contract that's $5 higher than underlying
                        for optionschain in self.chains:
                            for strike in optionschain.strikes:
                                if strike < df.close.iloc[-1] - 1 : #Make sure the strike is $5 away so it's cheaper
                                    print("Sell")
                                    self.options_contract = Option(self.underlying.symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=self.underlying.symbol)
                                    # We are not in a trade - Let's enter a trade
                                    options_order = MarketOrder('SELL', self.vol,account=self.ib.wrapper.accounts[-1])
                                    trade = self.ib.placeOrder(self.options_contract, options_order)
                                    self.lastEstimatedFillPrice = df.close.iloc[-1]
                                    self.in_trade = -1
                                    message = f"Option Bot Sell {self.options_contract}"
                                    Alert(message)
                                    return # important so it doesn't keep looping
                else: #We are in a trade
                    if signal == -2 or signal == 2:
                        #Sell for profit scalping
                        print("Get Out")
                        if self.in_trade == 1:
                            options_order = MarketOrder('SELL', self.vol,account=self.ib.wrapper.accounts[-1])
                        else:
                            options_order = MarketOrder('BUY', self.vol,account=self.ib.wrapper.accounts[-1])
                        trade = self.ib.placeOrder(self.options_contract, options_order)
                        self.in_trade = 0
                        message = f"Option Bot {options_order} {self.options_contract}"
                        Alert(message)
        except Exception as e:
            print(str(e))
    #Order Status
    def exec_status(self,trade: Trade,fill: Fill):
        print("Filled")

#Instantiate Class to get things rolling
RiskyOptionsBot()