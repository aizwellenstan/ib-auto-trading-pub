from ib_insync import *
import datetime

downloadFolder = 'C:\\Users\\YOURNAME\\Documents\\data\\' 
contracts = [['MES','MESH0','202006','2020-03-20','2019-12-14'],['MES','MESZ9','201912','2019-12-20','2019-09-14']]

##### Don't edit below unless you know what you're doing ;^)  ######

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=7)

def getData(contracts):
    for contract in contracts:
        symbol = contract[0]
        fileName = contract[1]
        contractMonth = contract[2]
        end = datetime.datetime.strptime(contract[3], '%Y-%m-%d')
        start = datetime.datetime.strptime(contract[4], '%Y-%m-%d')

        print('Contract: '+ fileName + ' ' + contractMonth)
        print('Downloading...')

        barsList = []

        contract = Contract(secType='FUT',symbol=symbol, lastTradeDateOrContractMonth=contractMonth, exchange='GLOBEX', currency='USD', includeExpired=True)

        dt = end
        while dt > start:
            bars = ib.reqHistoricalData(contract, endDateTime=dt, durationStr='10 D', barSizeSetting='1 min', whatToShow='TRADES', useRTH=False) #,timeout=0
            barsList.append(bars)
            print(fileName + ' ' + dt.strftime('%m/%d/%Y') + ' Done.')
            dt = bars[0].date

        allBars = [b for bars in reversed(barsList) for b in bars]
        df = util.df(allBars)
        gfg_csv_data = df.to_csv('test.csv', index = True) 

        print('Done.')
    print('All contracts downloaded :^)')

getData(contracts)