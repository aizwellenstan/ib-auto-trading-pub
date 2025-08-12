import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.data import GetNpData
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
from modules.ib_data import GetData
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=4)

addBiasLimit = 0.0023589999999999887
addBias30Limit = 0.00076
tpBiasLimit100 = 0.006781268523
tpBiasLimit500 = 0.007888697647

def scanner(symbol, minute):
    data = GetData(symbol)
    close1 = data[-2][3]
    open0 = data[-1][0]
    high = data[-1][1]
    low = data[-1][2]
    close = data[-1][3]
    ema8 = data[-1][4]
    ema30 = data[-1][5]
    ema100 = data[-1][6]
    ema500 = data[-1][7]

    # highBias100 = abs(high-ema100)/ema100
    # lowBias100 = abs(ema100-low)/ema100
    # curTpBias100 = max(highBias100,lowBias100)

    # if curTpBias100 > tpBiasLimit100:
    #     message = "tp GetGreenGetOut"
    #     Alert(message)

    highBias500 = abs(high-ema500)/ema500
    lowBias500 = abs(ema500-low)/ema500
    curTpBias500 = max(highBias500,lowBias500)
    
    if curTpBias500 > tpBiasLimit500:
        message = "tp GetGreenGetOut"
        Alert(message)
        return

    if (
        (close1 < ema30 and close > ema30) or
        (close1 > ema30 and close < ema30) or
        (open0 < ema30 and close > ema30) or
        (open0 > ema30 and close < ema30)
    ):
        message = "Market Order SL First ! cross 30ema"
        Alert(message)

    if (
        (
            (close1 < ema30 and close > ema30) or
            (open0 < ema30 and close > ema30)
        ) and bias30 < addBias30Limit
    ):
        message = "add buy"
        Alert(message)
    elif (
        (
            (close1 > ema30 and close < ema30) or
            (open0 > ema30 and close < ema30)
        ) and bias30 < addBias30Limit
    ):
        message = "add sell"
        Alert(message)

    if (
        open0 <= ema8 and open0 <= ema30 and open0 <= ema500 and
        close >= ema8 and close >= ema30 and close >= ema500
    ):
        message = "add buy"
        Alert(message)
    elif (
        open0 >= ema8 and open0 >= ema30 and open0 >= ema500 and
        close <= ema8 and close <= ema30 and close <= ema500
    ):
        message = "add sell"
        Alert(message)

    bias = abs(close-ema500)/ema500
    if (
        low < ema8 and close > ema8 and 
        bias > addBiasLimit and close < ema500
    ):
        message = "add buy"
        Alert(message)
    elif (
        high > ema8 and close < ema8 and 
        bias > addBiasLimit and close > ema500
    ):
        message = "add sell"
        Alert(message)

    # if minute % 2 == 0:
    #     longTP = ema100 * (1+tpBiasLimit100)
    #     shortTP = ema100 * (1-tpBiasLimit100)

    #     longTP500 = ema500 * (1+tpBiasLimit500)
    #     shortTP500 = ema500 * (1-tpBiasLimit500)

    #     message = f"longTP {min(longTP,longTP500)} shortTP {max(shortTP,shortTP500)} \n"
    #     message += f"longTP {longTP} longTP500 {longTP500} shortTP{shortTP} shortTP500{shortTP500}"
    #     Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def main():
    dayLightSaving = True
    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second
        if sec == 0:
            scanner('QQQ', minute)
            print('tick')
        if dayLightSaving:
            if(hour == 14 and minute == 0 and sec == 0):
                shutDown()
                return
        else:
            if(hour == 15 and minute == 0 and sec == 0):
                shutDown()
                return


if __name__ == '__main__':
    main()