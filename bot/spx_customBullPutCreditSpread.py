import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.data import GetNpData
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
from modules.optionChain import GetSPXCustomBullPutCreaditSpread

today = dt.datetime.today()
weekday = today.weekday()

def BacktestSpread(npArr, currency='USD'):
    spxPrice, combination = GetSPXCustomBullPutCreaditSpread(5)
    print(f"spxPrice {spxPrice}")
    print(combination)

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        print(comb)
        expir = comb['Expir']
        daysLeft = GetExpir(expir)
        spreadRange = spxPrice - comb['SellStrike']
        customSpreadRange = spxPrice - comb['ShortBE']
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft
        ):
            shortBE = npArr[i][0] - customSpreadRange
            if not npArr[i][4] == weekday: continue
            if npArr[i+daysLeft][3] < npArr[i][0] - spreadRange:
                if npArr[i+daysLeft][3] > shortBE:
                    capital -= comb['loss']
                else:
                    capital += (shortBE - npArr[i+daysLeft][3]) * 100
            else: capital += comb['profit']
        if capital > maxCapital:
            maxCapital = capital
            bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"SPX Price {spxPrice} \n CustomBullPutCreditSpread {bestCreaditSpread} \n maxCapital{maxCapital}"
    Alert(message)

def main(currency='USD'):
    symbol = '^GSPC'
    npArr = GetNpData(symbol, currency)
    BacktestSpread(npArr,currency)

main()