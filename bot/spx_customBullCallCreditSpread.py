import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.data import GetNpData
from modules.optionChain import GetSPXCustomBullCallCreditSpread
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert

today = dt.datetime.today()
weekday = today.weekday()

def BacktestSpread(npArr, currency='USD'):
    spxPrice, combination = GetSPXCustomBullCallCreditSpread(5)
    print(f"spxPrice {spxPrice}")
    print(combination)

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        print(comb)
        expir = comb['Expir']
        daysLeft = GetExpir(expir)
        spreadRange = comb['BuyStrike'] - spxPrice
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft
        ):
            if not npArr[i][4] == weekday: continue
            if npArr[i+daysLeft][3] < npArr[i][0] + spreadRange:
                if npArr[i+daysLeft][3] < comb['ShortBE']:
                    capital -= comb['loss']
                else:
                    capital += (comb['ShortBE']-npArr[i+daysLeft][3]) * 100
            else: capital += comb['profit']
        if capital > maxCapital:
            maxCapital = capital
            bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"SPX Price {spxPrice} \n CustomBullCallCreditSpread {bestCreaditSpread} \n maxCapital{maxCapital}"
    Alert(message)

def main(currency='USD'):
    symbol = '^GSPC'
    npArr = GetNpData(symbol, currency)
    BacktestSpread(npArr,currency)

main()