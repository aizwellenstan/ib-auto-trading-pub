import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
from modules.ib_data import GetData
import os
import pandas as pd
import numpy as np
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=7)

bar = 9
highRangeAll = 0
lowRangeAll = 0
checkPreRange = True

def CheckSignal(npArr):
    signal = 0
    if (
        (npArr[-2][3] - npArr[-2][2]) /
        (npArr[-2][1] - npArr[-2][2]) >= 0.5 and
        (npArr[-1][3] - npArr[-1][2]) /
        (npArr[-1][1] - npArr[-1][2]) >= 0.5
    ):
        signal = 1
    elif (
        (npArr[-2][3] - npArr[-2][2]) /
        (npArr[-2][1] - npArr[-2][2]) < 0.5 and
        (npArr[-1][3] - npArr[-1][2]) /
        (npArr[-1][1] - npArr[-1][2]) < 0.5
    ):
        signal = -1
    return signal

def scanner(symbol, hour, minute, dayLightSaving):
    global checkPreRange
    npArr = GetData(symbol)

    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14
    if (
        hour == hourLimit and minute < 33
    ):
        signal = CheckSignal(npArr)
        if signal > 0:
            Alert(symbol+' M 1OTM C')
        elif signal < 0:
            Alert(symbol+' M 1OTM P')

def init():
    message = "Only Trade Discord Alert!!"
    Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def main():
    dayLightSaving = True
    symbolList = ['IWM','QQQ','SPY']
    init()
    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second
        if sec == 0:
            for symbol in symbolList:
                scanner(symbol, hour, minute, dayLightSaving)
            print('tick')
        if dayLightSaving:
            if(hour == 13 and minute == 56 and sec == 0):
                shutDown()
        else:
            if(hour == 14 and minute == 56 and sec == 0):
                shutDown()

if __name__ == '__main__':
    main()