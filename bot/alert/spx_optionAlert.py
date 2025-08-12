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

biasYLimit = 0.00076
addBiasLimit = 0.0023589999999999887
tpBiasLimit100 = 0.006781268523
tpBiasLimit500 = 0.012299999999999981

def scanner(symbol, minute):
    data = GetData(symbol)
    close1 = data[-2][3]
    open0 = data[-1][0]
    high = data[-1][1]
    low = data[-1][2]
    close = data[-1][3]
    emaX = data[-1][4]
    emaY = data[-1][5]
    ema100 = data[-1][6]
    ema500 = data[-1][7]

    highBias500 = abs(high-ema500)/ema500
    lowBias500 = abs(ema500-low)/ema500
    curTpBias500 = max(highBias500,lowBias500)
    biasY = abs(close-emaY)/emaY

    if curTpBias500 > tpBiasLimit500:
        message = "tp GetGreenGetOut"
        Alert(message)
        return

    if (
        (
            (close1 < emaY and close > emaY) or
            (open0 < emaY and close > emaY)
        )
    ):
        message = "Market Order Close Sell First ! cross 30ema"
        Alert(message)

    if (
        (
            (close1 > emaY and close < emaY) or
            (open0 > emaY and close < emaY)
        )
    ):
        message = "Market Order Close Buy First ! cross 30ema"
        Alert(message)

    if (
        (
            (close1 < emaY and close > emaY) or
            (open0 < emaY and close > emaY)
        ) and biasY < biasYLimit
    ):
        message = "add buy"
        Alert(message)

    if (
        (
            (close1 > emaY and close < emaY) or
            (open0 > emaY and close < emaY)
        ) and biasY < biasYLimit
    ):
        message = "add sell"
        Alert(message)

    bias = abs(close-ema500)/ema500
    if (
        close > emaY and
        low < emaX and close > emaX and 
        bias > addBiasLimit and close < ema500
    ):
        message = "add buy"
        Alert(message)
    elif (
        close < emaY and
        high > emaX and close < emaX and 
        bias > addBiasLimit and close > ema500
    ):
        message = "add sell"
        Alert(message)

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
            scanner('SPX', minute)
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