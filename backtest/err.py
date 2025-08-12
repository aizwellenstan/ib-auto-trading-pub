import sys
trades = [{'op': 1}]

try:
    tradeHisBarsM5arr =[{'vol': 1}]
    i = 0
    for i, trade in enumerate(trades, 0):
        j = 0
        hisBarsM5 = tradeHisBarsM5arr[i]

        opendHisBarsM5 = hisBarsM5

        for i in opendHisBarsM5:
            print(i)

except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)