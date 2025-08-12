from datetime import datetime
from ib_insync import *
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

SL_RANGE = 0.19

ibs = IB()
ibs.connect('10.1.1.89',7497,clientId=6)

class RiskyOptionsBot:
    """
    Risky Options Bot (Python, Interactive Brokers)
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
        self.data = ibs.reqHistoricalData(self.underlying,
            endDateTime='',
            durationStr='2 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=False,
            keepUpToDate=True,)

        #Local vars
        self.in_trade = False

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
    
    def closeTrade():
        options_order = MarketOrder('SELL', 1,account=self.ib.wrapper.accounts[-1])
        trade = self.ib.placeOrder(self.options_contract, options_order)

    #On Bar Update, when we get new data
    def on_bar_update(self, bars: BarDataList, has_new_bar: bool):
        try:
            if has_new_bar:
                #Convert BarDataList to pandas Dataframe
                df = util.df(bars)
                # Check if we are in a trade
                if not self.in_trade:
                    print("Last Close : " + str(df.close.iloc[-1]))
                    # signal = checkSignal(df)
                    if df.close.iloc[-1] > df.close.iloc[-2] and df.close.iloc[-2] > df.close.iloc[-3]:
                        for optionschain in self.chains:
                            for strike in optionschain.strikes:
                                if strike < df.close.iloc[-1]:
                                    print("entering long trade.")
                                    self.options_contract = Option(self.underlying.symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=self.underlying.symbol)
                                    # We are not in a trade - Let's enter a trade
                                    options_order = MarketOrder('BUY', 1,account=self.ib.wrapper.accounts[-1])
                                    trade = self.ib.placeOrder(self.options_contract, options_order)
                                    self.lastEstimatedFillPrice = df.close.iloc[-1]
                                    self.direction = 1
                                    self.sl = df.close.iloc[-1] - SL_RANGE
                                    self.in_trade = not self.in_trade
                                    return # important so it doesn't keep looping
                    elif df.close.iloc[-1] < df.close.iloc[-2] and df.close.iloc[-2] < df.close.iloc[-3]:
                        for optionschain in self.chains:
                            for strike in optionschain.strikes:
                                if strike > df.close.iloc[-1]:
                                    print("entering short trade.")
                                    self.options_contract = Option(self.underlying.symbol, optionschain.expirations[1], strike, 'P', 'SMART', tradingClass=self.underlying.symbol)
                                    # We are not in a trade - Let's enter a trade
                                    options_order = MarketOrder('BUY', 1,account=self.ib.wrapper.accounts[-1])
                                    trade = self.ib.placeOrder(self.options_contract, options_order)
                                    self.lastEstimatedFillPrice = df.close.iloc[-1]
                                    self.direction = -1
                                    self.sl = df.close.iloc[-1] + SL_RANGE
                                    self.in_trade = not self.in_trade
                                    return # important so it doesn't keep looping
                else: #We are in a trade
                    if self.direction == 1:
                        if df.close.iloc[-1] <= self.sl:
                            self.closeTrade()
                            self.in_trade = not self.in_trade
                        else: 
                            self.sl = df.high.iloc[-1] - SL_RANGE
                    else:
                        if df.close.iloc[-1] >= self.sl:
                            self.closeTrade()
                            self.in_trade = not self.in_trade
                        else: 
                            self.sl = df.low.iloc[-1] + SL_RANGE
        except Exception as e:
            print(str(e))
    #Order Status
    def exec_status(self,trade: Trade,fill: Fill):
        print("Filled")

#Instantiate Class to get things rolling
RiskyOptionsBot()