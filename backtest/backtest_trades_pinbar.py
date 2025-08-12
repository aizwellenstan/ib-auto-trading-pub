from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import json
import pickle
import pandas_datareader.data as web

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=8)

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

df = pd.read_csv (r'./trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

try:
    fee = 1.001392062 * 2
    tpVal = 20.189
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0
    maxPinBarVal = 0
    tradeHisBarsM5arr = []
    tradeHisBarsQQQarr = []
    saveData = False
    if(saveData):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
            opEndTime = ''
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM5 = ib.reqHistoricalData(
                contract, endDateTime=opEndTime, durationStr='90 D',
                barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

            while(len(hisBarsM5)<6):
                print("timeout")
                hisBarsM5 = ib.reqHistoricalData(
                    contract, endDateTime=opEndTime, durationStr='90 D',
                    barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

            hisBarsM5 = [data for data in hisBarsM5 if data.date >= backtestTime]
            tradeHisBarsM5arr.append(hisBarsM5)

        pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsM5arr.p", "wb"))
        print("pickle dump finished")
    else:
        tradeHisBarsM5arr = pickle.load(open("./pickle/tradeHisBarsM5arr.p", "rb"))
        print(tradeHisBarsM5arr[0][0].date)

    saveQQQ = False
    if(saveQQQ):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
            opEndTime = ''
            contractQQQ = Stock("QQQ", 'SMART', 'USD')

            hisBarsQQQ = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            while(len(hisBarsQQQ)<6):
                print("timeout")
                hisBarsQQQ = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            hisBarsQQQ = hisBarsQQQ[::-1]
            print(backtestTime,hisBarsQQQ[0].date)
            tradeHisBarsQQQarr.append(hisBarsQQQ)
            print("data get")

        pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsQQQarr.p", "wb"))
        print("pickle dump finished")
    else:
        tradeHisBarsQQQarr = pickle.load(open("./pickle/tradeHisBarsQQQarr.p", "rb"))
        print(tradeHisBarsQQQarr[0][0].date)

    end = dt.now()
    start = end - timedelta(days=50)

    tradeSymList = []

    # drop duplicat sym for req data from yahoo
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in tradeSymList:
            tradeSymList.append(symbol)

    tradableList = []
    fetchTradableList = False
    if(fetchTradableList):
        for symbol in tradeSymList:
            dataReader = web.get_quote_yahoo(symbol)
            marketCap = 0
            if('marketCap' in dataReader):
                marketCap = dataReader['marketCap'][0]
            # if(marketCap < 21744275): continue
            if(marketCap < 1): continue
            volDf = web.DataReader(symbol, "yahoo", start, end)
            volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
            # if(volavg < 1987664): continue
            if(volavg < 1): continue
            tradableList.append({
                'symbol': symbol,
                'marketCap': marketCap,
                'volavg': volavg
            })
        print(tradableList)
    else:
        tradableList = [
            {
                "symbol":"DRIO",
                "marketCap":252887872,
                "volavg":227373.33333333334
            },
            {
                "symbol":"AFIB",
                "marketCap":457566112,
                "volavg":278543.3333333333
            },
            {
                "symbol":"BFLY",
                "marketCap":2247645696,
                "volavg":2610820.0
            },
            {
                "symbol":"SUMR",
                "marketCap":27497594,
                "volavg":67036.66666666667
            },
            {
                "symbol":"BCEL",
                "marketCap":332756832,
                "volavg":214113.33333333334
            },
            {
                "symbol":"HOL",
                "marketCap":378750016,
                "volavg":779256.6666666666
            },
            {
                "symbol":"DLPN",
                "marketCap":65102912,
                "volavg":1693600.0
            },
            {
                "symbol":"TUR",
                "marketCap":358854496,
                "volavg":278833.3333333333
            },
            {
                "symbol":"FNKO",
                "marketCap":1309415680,
                "volavg":1225486.6666666667
            },
            {
                "symbol":"PRTA",
                "marketCap":1283835904,
                "volavg":299430.0
            },
            {
                "symbol":"LUMO",
                "marketCap":87321344,
                "volavg":25276.666666666668
            },
            {
                "symbol":"CERT",
                "marketCap":4024877568,
                "volavg":501573.3333333333
            },
            {
                "symbol":"WAFU",
                "marketCap":30973882,
                "volavg":620250.0
            },
            {
                "symbol":"TLS",
                "marketCap":2192277248,
                "volavg":717316.6666666666
            },
            {
                "symbol":"X",
                "marketCap":6992309760,
                "volavg":24911243.333333332
            },
            {
                "symbol":"HGEN",
                "marketCap":1186625024,
                "volavg":1363226.6666666667
            },
            {
                "symbol":"GTH",
                "marketCap":1881413760,
                "volavg":282583.3333333333
            },
            {
                "symbol":"QURE",
                "marketCap":1594964864,
                "volavg":409193.3333333333
            },
            {
                "symbol":"IQ",
                "marketCap":11255203840,
                "volavg":14975030.0
            },
            {
                "symbol":"ORPH",
                "marketCap":202409200,
                "volavg":15406.666666666666
            },
            {
                "symbol":"ING",
                "marketCap":54260740096,
                "volavg":5301096.666666667
            },
            {
                "symbol":"GP",
                "marketCap":345776096,
                "volavg":159440.0
            },
            {
                "symbol":"CAN",
                "marketCap":1328443136,
                "volavg":8109560.0
            },
            {
                "symbol":"ABCL",
                "marketCap":7268944896,
                "volavg":882190.0
            },
            {
                "symbol":"TIGR",
                "marketCap":3239165696,
                "volavg":8075886.666666667
            },
            {
                "symbol":"VLDR",
                "marketCap":1830460160,
                "volavg":3364056.6666666665
            },
            {
                "symbol":"BOWX",
                "marketCap":741404992,
                "volavg":654310.0
            },
            {
                "symbol":"STLA",
                "marketCap":61141372928,
                "volavg":2691123.3333333335
            },
            {
                "symbol":"TME",
                "marketCap":26641051648,
                "volavg":19764970.0
            },
            {
                "symbol":"VIPS",
                "marketCap":15697612800,
                "volavg":13328890.0
            },
            {
                "symbol":"HYLN",
                "marketCap":1805019008,
                "volavg":4331443.333333333
            },
            {
                "symbol":"VERY",
                "marketCap":134767504,
                "volavg":22476.666666666668
            },
            {
                "symbol":"RICE",
                "marketCap":466829504,
                "volavg":237140.0
            },
            {
                "symbol":"FTCV",
                "marketCap":371609440,
                "volavg":614800.0
            },
            {
                "symbol":"ALLT",
                "marketCap":686815296,
                "volavg":169020.0
            },
            {
                "symbol":"KZIA",
                "marketCap":124400312,
                "volavg":58433.333333333336
            },
            {
                "symbol":"AGC",
                "marketCap":736875008,
                "volavg":1416390.0
            },
            {
                "symbol":"GROW",
                "marketCap":93708032,
                "volavg":341450.0
            },
            {
                "symbol":"MUDS",
                "marketCap":539600896,
                "volavg":3507273.3333333335
            },
            {
                "symbol":"EVLO",
                "marketCap":716277760,
                "volavg":157590.0
            },
            {
                "symbol":"AFMD",
                "marketCap":1055113088,
                "volavg":1992766.6666666667
            },
            {
                "symbol":"TIRX",
                "marketCap":80588496,
                "volavg":2574583.3333333335
            },
            {
                "symbol":"MFNC",
                "marketCap":228732672,
                "volavg":95316.66666666667
            },
            {
                "symbol":"INO",
                "marketCap":1572710400,
                "volavg":8469566.666666666
            },
            {
                "symbol":"GSK",
                "marketCap":95853395968,
                "volavg":3992153.3333333335
            },
            {
                "symbol":"INFY",
                "marketCap":81624276992,
                "volavg":5427043.333333333
            },
            {
                "symbol":"CRCT",
                "marketCap":7475529728,
                "volavg":882640.0
            },
            {
                "symbol":"HOG",
                "marketCap":7428076544,
                "volavg":2783890.0
            },
            {
                "symbol":"SBLK",
                "marketCap":1936166528,
                "volavg":2076710.0
            },
            {
                "symbol":"NNDM",
                "marketCap":1766636160,
                "volavg":19362800.0
            },
            {
                "symbol":"SLV",
                "marketCap":8843554816,
                "volavg":24782183.333333332
            },
            {
                "symbol":"SKLZ",
                "marketCap":6726391808,
                "volavg":27060533.333333332
            },
            {
                "symbol":"RHE",
                "marketCap":20343052,
                "volavg":9296726.666666666
            },
            {
                "symbol":"FSLY",
                "marketCap":5458231296,
                "volavg":5295556.666666667
            },
            {
                "symbol":"MVIS",
                "marketCap":2464051200,
                "volavg":41417633.333333336
            },
            {
                "symbol":"M",
                "marketCap":5698168832,
                "volavg":15768986.666666666
            },
            {
                "symbol":"CLF",
                "marketCap":10047968256,
                "volavg":24163103.333333332
            },
            {
                "symbol":"AA",
                "marketCap":7394844160,
                "volavg":6818473.333333333
            },
            {
                "symbol":"VALE",
                "marketCap":110414823424,
                "volavg":32629186.666666668
            },
            {
                "symbol":"CUE",
                "marketCap":437391520,
                "volavg":701630.0
            },
            {
                "symbol":"T",
                "marketCap":210130190336,
                "volavg":55475246.666666664
            },
            {
                "symbol":"PRTY",
                "marketCap":1027012800,
                "volavg":3339010.0
            },
            {
                "symbol":"GOLD",
                "marketCap":42869145600,
                "volavg":16722826.666666666
            },
            {
                "symbol":"ET",
                "marketCap":26764550144,
                "volavg":19754410.0
            },
            {
                "symbol":"GGB",
                "marketCap":9986937856,
                "volavg":23106310.0
            },
            {
                "symbol":"SLB",
                "marketCap":43809677312,
                "volavg":13460740.0
            },
            {
                "symbol":"DVN",
                "marketCap":17978064896,
                "volavg":10530423.333333334
            },
            {
                "symbol":"TLRY",
                "marketCap":5280972800,
                "volavg":24492350.0
            },
            {
                "symbol":"JMIA",
                "marketCap":2877917952,
                "volavg":7100496.666666667
            },
            {
                "symbol":"AMC",
                "marketCap":11761313792,
                "volavg":127067256.66666667
            },
            {
                "symbol":"WFC",
                "marketCap":193473134592,
                "volavg":26819176.666666668
            },
            {
                "symbol":"XLF",
                "marketCap":33562077184,
                "volavg":48929166.666666664
            },
            {
                "symbol":"BAC",
                "marketCap":363253465088,
                "volavg":40778586.666666664
            },
            {
                "symbol":"PLUG",
                "marketCap":18103298048,
                "volavg":39983003.333333336
            },
            {
                "symbol":"F",
                "marketCap":57998528512,
                "volavg":89647013.33333333
            },
            {
                "symbol":"UBER",
                "marketCap":94917910528,
                "volavg":23346823.333333332
            },
            {
                "symbol":"AAL",
                "marketCap":15547122688,
                "volavg":36053233.333333336
            },
            {
                "symbol":"FCEL",
                "marketCap":3166252544,
                "volavg":24049866.666666668
            },
            {
                "symbol":"FSR",
                "marketCap":3903836928,
                "volavg":19316080.0
            },
            {
                "symbol":"LEDS",
                "marketCap":56079072,
                "volavg":11962370.0
            },
            {
                "symbol":"FUBO",
                "marketCap":3336087296,
                "volavg":14403013.333333334
            },
            {
                "symbol":"NIO",
                "marketCap":63279644672,
                "volavg":74499686.66666667
            },
            {
                "symbol":"CLOV",
                "marketCap":3104246528,
                "volavg":25111526.666666668
            },
            {
                "symbol":"UWMC",
                "marketCap":14269962240,
                "volavg":5955783.333333333
            },
            {
                "symbol":"NVVE",
                "marketCap":199138576,
                "volavg":1034080.0
            },
            {
                "symbol":"FF",
                "marketCap":449242688,
                "volavg":431593.3333333333
            },
            {
                "symbol":"SM",
                "marketCap":2344180224,
                "volavg":3626293.3333333335
            },
            {
                "symbol":"MGM",
                "marketCap":21029277696,
                "volavg":8107836.666666667
            },
            {
                "symbol":"PDSB",
                "marketCap":271795264,
                "volavg":2121333.3333333335
            },
            {
                "symbol":"MOXC",
                "marketCap":205655904,
                "volavg":2247053.3333333335
            },
            {
                "symbol":"TAK",
                "marketCap":54037041152,
                "volavg":2147040.0
            },
            {
                "symbol":"REAL",
                "marketCap":1586045312,
                "volavg":3000426.6666666665
            },
            {
                "symbol":"PRVB",
                "marketCap":482281472,
                "volavg":3363710.0
            },
            {
                "symbol":"GTX",
                "marketCap":601210688,
                "volavg":497093.23333333334
            },
            {
                "symbol":"DOYU",
                "marketCap":2562838784,
                "volavg":2541040.0
            },
            {
                "symbol":"HRTX",
                "marketCap":1216521984,
                "volavg":2204240.0
            },
            {
                "symbol":"OCGN",
                "marketCap":1642697856,
                "volavg":103634946.66666667
            },
            {
                "symbol":"ZH",
                "marketCap":5227612160,
                "volavg":1531333.3333333333
            },
            {
                "symbol":"AMWL",
                "marketCap":2993353472,
                "volavg":3958663.3333333335
            },
            {
                "symbol":"BTBT",
                "marketCap":408311584,
                "volavg":1877383.3333333333
            },
            {
                "symbol":"KODK",
                "marketCap":558944960,
                "volavg":2294893.3333333335
            },
            {
                "symbol":"WKEY",
                "marketCap":161405216,
                "volavg":865383.3333333334
            },
            {
                "symbol":"WNW",
                "marketCap":178500000,
                "volavg":529630.0
            },
            {
                "symbol":"AEVA",
                "marketCap":2059779840,
                "volavg":1397393.3333333333
            },
            {
                "symbol":"CLVS",
                "marketCap":536418464,
                "volavg":3986180.0
            },
            {
                "symbol":"BPTH",
                "marketCap":39603084,
                "volavg":185020.0
            },
            {
                "symbol":"AMR",
                "marketCap":365207552,
                "volavg":190040.0
            }
            ]
    # df = pd.read_csv (r'./fillter.csv')
    df = pd.read_csv (r'./fillter_all.csv')
    df.drop
    fillters = json.loads(df.to_json(orient = 'records'))

    marketCapLimitArr = []
    volavgLimitArr = []
    for fillter in fillters:
        if(fillter['marketCap'] != None and fillter['marketCap'] > 0):
            marketCapLimitArr.append(
                int(fillter['marketCap'])
                ) 
        if(fillter['volavg'] != None and fillter['volavg']>0):
            volavgLimitArr.append(int(fillter['volavg']))

    marketCapLimitArr.reverse()
    volavgLimitArr.reverse()

    pinBarVal = 0.001
    while(pinBarVal < 1):
        total = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        a = 0
        for trade in trades:
            a += 1
            symbol = trade['symbol']
            if not list(filter(lambda x:x["symbol"]== symbol,tradableList)): continue
            marketCap = 0
            volavg = 0
            for sym in tradableList:
                if(symbol == sym['symbol']):
                    marketCap = float(sym['marketCap'])
                    volavg = float(sym['volavg'])
                    # tpVal = volavg/175751849.851#1563121.35747
                    # tpVal = marketCap/175751849.851
                    tpVal = marketCap/188785133.098#175751849.851
                    if(tpVal<20.189): tpVal=20.189

            # if(symbol == 'AMC'): continue
            
            marketCapLimit = 178499997
            volavgLimit = 922216
            if(marketCap < marketCapLimit): continue
            if(volavg < volavgLimit): continue

            backtestTime = trade['time']
            op = trade['op']
            if(op>13.60 and op < 50): continue
            sl = trade['sl']
            # tp = trade['tp']
            tp = op+(op-sl)*tpVal
            trade['tp'] = tp
            vol = trade['vol']
            trade['result'] = ''
            trade['total'] = 0
            if(vol<3): continue
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

            opEndTime = ''

            hisBarsQQQ = tradeHisBarsQQQarr[a-1]

            sma25 = sum(map(lambda x: x.close, hisBarsQQQ[2:27]))/25

            if(hisBarsQQQ[1].close/sma25 > 1.021):
                continue
            
            if(
                hisBarsQQQ[1].close < hisBarsQQQ[1].open
                and hisBarsQQQ[0].open > hisBarsQQQ[1].close
                and hisBarsQQQ[0].open < hisBarsQQQ[1].open
            ): continue

            if(hisBarsQQQ[0].open > hisBarsQQQ[1].close * 1.014):
                continue

            if(hisBarsQQQ[1].high-hisBarsQQQ[1].close
                > (hisBarsQQQ[1].high-hisBarsQQQ[1].low)*pinBarVal
            ): continue

            hisBarsM5 = tradeHisBarsM5arr[a-1]

            opendHisBarsM5 = hisBarsM5

            endTime = hisBarsM5[-1].date
            
            trade['status'] = ''
            for i in opendHisBarsM5:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                for i in hisBarsM5:
                    if i.date >= triggeredTime:
                        if i.date == triggeredTime:
                            if i.high >= tp:
                                net = (tp-op)*vol - fee
                                trade['total'] = net
                                if(net > 0):
                                    trade['result'] = 'profit'
                                    totalNetProfit += net
                                    win += 1
                                else:
                                    trade['result'] = 'loss'
                                    totalNetLoss += net
                                    loss += 1
                                total += net
                                break
                        else:
                            if i.low <= sl:
                                net = (sl-op)*vol - fee
                                trade['total'] = net
                                trade['result'] = 'loss'
                                totalNetLoss += net
                                loss += 1
                                total += net
                                break

                            if i.high >= tp:
                                net = (tp-op)*vol - fee
                                trade['total'] = net
                                if(net > 0):
                                    trade['result'] = 'profit'
                                    totalNetProfit += net
                                    win += 1
                                else:
                                    trade['result'] = 'loss'
                                    totalNetLoss += net
                                    loss += 1
                                total += net
                                break
                            
                            # if i.date >= endTime:
                            #     print(symbol," closeAtPre ",i.date)
                            #     if(i.open > op):
                            #         net = (i.open-op)*vol - 2
                            #         trade['total'] = net
                            #         if(net > 0):
                            #             trade['result'] = 'profit closeAtPre'
                            #             totalNetProfit += net
                            #             win += 1
                            #         else:
                            #             trade['result'] = 'loss closeAtPre'
                            #             totalNetLoss += net
                            #             loss += 1
                            #         total += net
                            #     else:
                            #         net = (i.open-op)*vol - 2
                            #         trade['total'] = net
                            #         trade['result'] = 'loss closeAtPre'
                            #         totalNetLoss += net
                            #         loss += 1
                            #         total += net
                            #     break
        winrate = 0
        if(win+loss>0):
            winrate = win/(win+loss)
        profitfactor =0
        if(abs(totalNetLoss)>0):
            profitfactor = totalNetProfit/abs(totalNetLoss)
        elif(totalNetProfit>0):
            profitfactor = 99.99
        print("total",str(total),
                "wr",winrate*100,"%",
                "profitfactor",str(profitfactor))
        if(total > maxProfit): # and winrate>0.067
            maxProfit = total
            maxTpVal = tpVal
            maxMarCapLimit = marketCapLimit
            maxVolavgLimit = volavgLimit
            maxPinBarVal = pinBarVal
        print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
        print('maxMarCapLimit',str(maxMarCapLimit),'maxVolavgLimit',str(maxVolavgLimit))
        print('maxPinBarVal',str(maxPinBarVal))
        pinBarVal += 0.01

    df = pd.DataFrame(trades)
    df.to_csv('./trades_status.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)