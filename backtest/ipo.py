rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr
from modules.data import GetDf
from modules.businessday import GetBusinessDays
from datetime import datetime
from modules.dividendCalendar import GetExDividendWithPayment, GetExDividendByDate
import pickle
from modules.dividend import GetDividend
import numpy as np
from datetime import datetime, timedelta
from modules.dict import take


picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDictAll.p"

dataDict = {}
import pickle
output = open(picklePath, "rb")
dataDict = pickle.load(output)
output.close()


def Backtest():
    maxGainPerDay = 1
    maxDur = 1
    days = 2
    while days < 60:
        gainPerDayList = np.empty(0)
        for symbol, npArr in dataDict.items():
            if len(npArr) > 1058: continue
            maxDur = 0
            maxDur = 0
            # for i in range(0, len(npArr)):
            op = npArr[1][0]
            if len(npArr) < days + 2: continue
            close = npArr[days+1][3]
                # gainPerDay = close/op/(i+1)
                # if gainPerDay > maxGainPerDay:
                #     maxGainPerDay = gainPerDay
                #     maxDur = i
            # durationList.append(maxDur)
            gainPerDayList = np.append(gainPerDayList, close/op)
        gainPerDay = sum(gainPerDayList)/len(gainPerDayList)
        if gainPerDay > maxGainPerDay:
            maxGainPerDay = gainPerDay
            maxDur = days
            print(maxGainPerDay,maxDur)
        days += 1
Backtest()
import sys
sys.exit(0)
# from modules.dividendCalendar import GetExDividend
# import pandas as pd
# import os
# startDate = '2020-03-18'
# endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
# dates = GetBusinessDays(startDate, endDate)
# npArr = GetExDividendWithPayment(dates[-1])
# for i in npArr:
#     if npArr[i][1] > datetime.now():
#         print('SKIP')

def CleanDividendCalandarDict(dividendCalendarDict):
    now = datetime.now().date()
    newDividendCalandarDict = {}
    for exDate, exList in dividendCalendarDict.items():
        append = True
        for exData in exList:
            if exData[1] > now:
                append = False
                break
        if append:
            newDividendCalandarDict[exDate] = exList
    dividendCalendarDict = newDividendCalandarDict
    return dividendCalendarDict

def GetDividendCalanderDict(update=False):
    picklePath = "./pickle/pro/compressed/dividendCalendar2.p"
    dividendCalendarDict = {}
    if update:
        startDate = '2020-03-18'
        endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
        dates = GetBusinessDays(startDate, endDate)
        for date in dates:
            print(date)
            exDivList = GetExDividendWithPayment(date)
            if len(exDivList) < 1: continue
            dateStr = datetime.strftime(date,'%Y-%m-%d')
            dividendCalendarDict[dateStr] = exDivList
            print(dateStr,exDivList)
        pickle.dump(dividendCalendarDict, open(picklePath, "wb"))
    else:
        output = open(picklePath, "rb")
        dividendCalendarDict = pickle.load(output)
    return CleanDividendCalandarDict(dividendCalendarDict)

def GetDividendCalandarSymbols(dividendCalendarDict):
    symbolList = []
    for exDate, exList in dividendCalendarDict.items():
        for i in exList:
            if i[0] not in symbolList:
                symbolList.append(i[0])
    return symbolList

def GetData(symbol):
    df = GetDf(symbol)
    if len(df) < 1: return[]
    df = df.assign(Date=df.index.date)
    df = df[['Open','Close','Dividends','Date']]
    npArr = df.to_numpy()
    return npArr

def GetDataDict(symbolList, update=False):
    dataDict = {}
    picklePath = "./pickle/pro/compressed/dataDictDividends2.p"
    if update:
        for symbol in symbolList:
            npArr = GetData(symbol)
            if len(npArr) < 1: continue
            dataDict[symbol] = npArr
            print(symbol)
        pickle.dump(dataDict, open(picklePath, "wb"))
    else:
        output = open(picklePath, "rb")
        dataDict = pickle.load(output)
    return dataDict

def Backtest(dividendCalendarDict, oriDividendCalandarList, dataDict, shift=1):
    
    ignoreList = ['INFR', 'OSW', 'AEO', 'TX', 'AMTD', 'DCOM', 'PHG', 'CLAR', 'ETN', 'AEG', 'FG', 'HGLB', 'BAM', 'AVAL', 'RVSB', 'EIC', 'ARCO', 'EBR', 'CFO',
'IBTK', 'BSCS', 'MUFG', 'MFG', 'NMR', 'PKX', 'TAK', 'TM', 'AAN', 'HR', 'RCI', 'TQQQ', 'CAJ', 'KB', 'GF',
'NYC', 'GLP', 'TAC', 'RBC', 'BIPC', 'AUDC', 'KEN', 'BAP', 'SONY', 'AKO.A', 'AKO.B', 'CNI', 'CM', 'VSMV',
'PANL', 'VALE', 'DOOO', 'BKCC', 'PBR.A', 'BBU', 'BEP', 'CRT', 'BNS', 'BKSC', 'AMC', 'WPM', 'SCD', 'MCO',
'PBA', 'DOX', 'ICL']
    divToPriceList = [0.005810277824243339, 0.007977475785238618, 0.008445390731994396, 0.010016742257092981, 0.010126700509234048, 0.01019940485817442, 0.010225251576685362, 0.01048594871213348,
0.010821277054030819, 0.010939080194998473, 0.011005785720415414, 0.011295028497254514, 0.011564578629801127, 0.01161170059539126, 0.011662186643013968, 0.011879896976708076,
0.012051352199503613, 0.012308899426367382, 0.012586709582306597, 0.012734891401620554, 0.013729506528218891, 0.014483745429121463, 0.014793967491156109, 0.01531725642248308,
0.015604182337191288, 0.015864270102430588, 0.016159930166587653, 0.016587518018201686, 0.016918331677030076, 0.01693320956127333, 0.01780091012937964, 0.0178834692647852, 0.01864492411536341, 0.019007195615735283, 0.01911040234715774, 0.019296391426310712, 0.01953860649254554, 0.019543396044482336, 0.02076191798599665, 0.021035605194364516, 0.021269792139801947, 0.021318872784341667, 0.021535427275746873, 0.02158802083457747, 0.021664684558575998, 0.021797424272148404, 0.02181546981256164, 0.021950276264457624, 0.02220683494263898, 0.022296816091159556, 0.022544741454927113, 0.022590056000434584, 0.022918357626242093, 0.02329794010473774, 0.02354031338696084, 0.023700573915960088, 0.023839439065227223, 0.02419153366928035, 0.024312538246523328, 0.02442613431584866, 0.024547212011043304, 0.02460151740033871, 0.02475351202157064, 0.02524696880309022, 0.025763861865513653, 0.025766024915241284, 0.025847803891212516, 0.025964999416475745, 0.026133970294676984, 0.026331820578061618, 0.0263486706781773, 0.02654114761595195, 0.026547189647557024, 0.02656434024548479, 0.026617856743717437, 0.026718932845675177, 0.026840167752969008, 0.02692664823301601, 0.026963199233309042, 0.027083848005560296, 0.02712241897501389, 0.027757869387843703, 0.027985626610559484, 0.028172553382837116, 0.028792374498995636, 0.028798820748098242, 0.02885535613599833, 0.02896921974835039, 0.029183790488023425, 0.029254745170128323, 0.02969306414544711, 0.029983184402176524, 0.03012050398419306, 0.030277498692068288, 0.030951773385744293, 0.03140568982855622, 0.03184891783034145, 0.03203524932848591, 0.03214764113093264, 0.0324799498428312, 0.03305202616810518, 0.033242583092355026, 0.03334049303477106, 0.03343992034935526, 0.03376201744637331, 0.03394157472186516, 0.03401619498861184, 0.03401651763632618, 0.034570123501933184, 0.03460567091940853, 0.0353170283403658, 0.03535813645639447, 0.03567354191849452, 0.035684229852581455, 0.0357278160451736, 0.03573168364240652, 0.03631151191432387, 0.036365184843110895, 0.036520351793385225, 0.03653837229838099, 0.03682305758621561, 0.036949916559389416, 0.03715060847304608, 0.03764612028588617, 0.03874431464419101, 0.03892436932213561, 0.039687708929360646, 0.04002848929676921, 0.04029435120033596, 0.04058631377891877, 0.04102714924331316, 0.04106705685544602, 0.04169566158035688, 0.042278010687255875, 0.04262414554774504, 0.04297277289459077, 0.043165812057066835, 0.0435519204032746, 0.04377790399881714, 0.04392411233437651, 0.04483875290066545, 0.04542335738736979, 0.04615464070802001, 0.046265772408099086, 0.046507940421864666, 0.04832720985006219, 0.049498617798486286, 0.049970723215059104, 0.05015443085936292, 0.05053050383335904, 0.051333873839118804, 0.05150469450591114, 0.05182826385866475, 0.05228613803290265, 0.05262534753621402, 0.05396030775068083, 0.05451730392646847, 0.05518630125107273, 0.05536811137975945, 0.05540572066173971, 0.056308628464275486, 0.05644518750912648, 0.057111652438418196, 0.057971098616748214, 0.059055827730812804, 0.06042158465343589, 0.06180133235741626, 0.06194960754560846, 0.06468202339292002, 0.06508775942645804, 0.06612248448483685, 0.06667478347231072, 0.06737954839119548, 0.0683378209765364, 0.06837541933904781, 0.06966561970807529, 0.07087093273281314, 0.07261543788575238,
0.0744663479102059, 0.07492771444070331, 0.07693418529447812, 0.07745309898541632, 0.07762671277894814, 0.08146779098539961, 0.08220840512898231, 0.0851079118490304, 0.08550127898406111, 0.0906531561154676, 0.09111173162676446, 0.09164921872235773, 0.09251244435580272, 0.09339263685003507, 0.09402435438793146, 0.09464481950475351, 0.09478097200531173, 0.09491573187022896, 0.09671422031848759, 0.09748034930751356, 0.10059350559556782, 0.10415155211431786, 0.11181798764384798, 0.11791541419961275, 0.1210377562270333, 0.1395580313176782, 0.1519405989199543, 0.15662829615527393, 0.1578210331651795, 0.19029438221622935, 0.2236963072610733, 0.28678078363620685, 0.31112080200062825, 0.34323396706600307, 0.9833085074441068]

#     divToPriceList = [0.008445390731994396, 0.010016742257092981, 0.010126700509234048, 0.01019940485817442, 0.010225251576685362, 0.01048594871213348,
# 0.010821277054030819, 0.010939080194998473, 0.011005785720415414, 0.011295028497254514, 0.011564578629801127, 0.01161170059539126, 0.011662186643013968, 0.011879896976708076,
# 0.012051352199503613, 0.012308899426367382, 0.012586709582306597, 0.012734891401620554, 0.013729506528218891, 0.014483745429121463, 0.014793967491156109, 0.01531725642248308,
# 0.015604182337191288, 0.015864270102430588, 0.016159930166587653, 0.016587518018201686, 0.016918331677030076, 0.01693320956127333, 0.01780091012937964, 0.0178834692647852, 0.01864492411536341, 0.019007195615735283, 0.01911040234715774, 0.019296391426310712, 0.01953860649254554, 0.019543396044482336, 0.02076191798599665, 0.021035605194364516, 0.021269792139801947, 0.021318872784341667, 0.021535427275746873, 0.02158802083457747, 0.021664684558575998, 0.021797424272148404, 0.02181546981256164, 0.021950276264457624, 0.02220683494263898, 0.022296816091159556, 0.022544741454927113, 0.022590056000434584, 0.022918357626242093, 0.02329794010473774, 0.02354031338696084, 0.023700573915960088, 0.023839439065227223, 0.02419153366928035, 0.024312538246523328, 0.02442613431584866, 0.024547212011043304, 0.02460151740033871, 0.02475351202157064, 0.02524696880309022, 0.025763861865513653, 0.025766024915241284, 0.025847803891212516, 0.025964999416475745, 0.026133970294676984, 0.026331820578061618, 0.0263486706781773, 0.02654114761595195, 0.026547189647557024, 0.02656434024548479, 0.026617856743717437, 0.026718932845675177, 0.026840167752969008, 0.02692664823301601, 0.026963199233309042, 0.027083848005560296, 0.02712241897501389, 0.027757869387843703, 0.027985626610559484, 0.028172553382837116, 0.028792374498995636, 0.028798820748098242, 0.02885535613599833, 0.02896921974835039, 0.029183790488023425, 0.029254745170128323, 0.02969306414544711, 0.029983184402176524, 0.03012050398419306, 0.030277498692068288, 0.030951773385744293, 0.03140568982855622, 0.03184891783034145, 0.03203524932848591, 0.03214764113093264, 0.0324799498428312, 0.03305202616810518, 0.033242583092355026, 0.03334049303477106, 0.03343992034935526, 0.03376201744637331, 0.03394157472186516, 0.03401619498861184, 0.03401651763632618, 0.034570123501933184, 0.03460567091940853, 0.0353170283403658, 0.03535813645639447, 0.03567354191849452, 0.035684229852581455, 0.0357278160451736, 0.03573168364240652, 0.03631151191432387, 0.036365184843110895, 0.036520351793385225, 0.03653837229838099, 0.03682305758621561, 0.036949916559389416, 0.03715060847304608, 0.03764612028588617, 0.03874431464419101, 0.03892436932213561, 0.039687708929360646, 0.04002848929676921, 0.04029435120033596, 0.04058631377891877, 0.04102714924331316, 0.04106705685544602, 0.04169566158035688, 0.042278010687255875, 0.04262414554774504, 0.04297277289459077, 0.043165812057066835, 0.0435519204032746, 0.04377790399881714, 0.04392411233437651, 0.04483875290066545, 0.04542335738736979, 0.04615464070802001, 0.046265772408099086, 0.046507940421864666, 0.04832720985006219, 0.049498617798486286, 0.049970723215059104, 0.05015443085936292, 0.05053050383335904, 0.051333873839118804, 0.05150469450591114, 0.05182826385866475, 0.05228613803290265, 0.05262534753621402, 0.05396030775068083, 0.05451730392646847, 0.05518630125107273, 0.05536811137975945, 0.05540572066173971, 0.056308628464275486, 0.05644518750912648, 0.057111652438418196, 0.057971098616748214, 0.059055827730812804, 0.06042158465343589, 0.06180133235741626, 0.06194960754560846, 0.06468202339292002, 0.06508775942645804, 0.06612248448483685, 0.06667478347231072, 0.06737954839119548, 0.0683378209765364, 0.06837541933904781, 0.06966561970807529, 0.07087093273281314, 0.07261543788575238,
# 0.0744663479102059, 0.07492771444070331, 0.07693418529447812, 0.07745309898541632, 0.07762671277894814, 0.08146779098539961, 0.08220840512898231, 0.0851079118490304, 0.08550127898406111, 0.0906531561154676, 0.09111173162676446, 0.09164921872235773, 0.09251244435580272, 0.09339263685003507, 0.09402435438793146, 0.09464481950475351, 0.09478097200531173, 0.09491573187022896, 0.09671422031848759, 0.09748034930751356, 0.10059350559556782, 0.10415155211431786, 0.11181798764384798, 0.11791541419961275, 0.1210377562270333, 0.1395580313176782, 0.1519405989199543, 0.15662829615527393, 0.1578210331651795, 0.19029438221622935, 0.2236963072610733, 0.28678078363620685, 0.31112080200062825, 0.34323396706600307, 0.9833085074441068]
    
    
    maxBalance = 1
    maxDivToPriceTradeLimit = 0
    maxShift = 1
    while shift < 360:
        for divToPriceTradeLimit in divToPriceList:
            dividendCalendarList = oriDividendCalandarList
            balance = 1
            positions = []
            for date in dates:
                if len(positions) > 0:
                    newPositions = []
                    for position in positions:
                        if position[1] <= date:
                            balance += position[0]
                            continue
                        else:
                            newPositions.append(position)
                    positions = newPositions
                buyDate = date + timedelta(days=shift)
                for exDivDate in dividendCalendarList:
                    if exDivDate < date:
                        # dividendCalendarList.remove(exDivDate)
                        continue
                    elif exDivDate == buyDate:
                        # dividendCalendarList.remove(exDivDate)
                        exDivList = dividendCalendarDict[exDivDate]
                        divToPriceLimit = 0
                        tradeVol = 0
                        opPrice = 0
                        closePrice = 0
                        payDiv = 0
                        for i in exDivList:
                            symbol = i[0]
                            if symbol in ignoreList: continue
                            if symbol not in dataDict: continue
                            npArr = dataDict[symbol]
                            op = 0
                            close = 0
                            div = 0
                            for j in range(0, len(npArr)):
                                if npArr[j][3] < buyDate:
                                    op = npArr[j][0] # close
                                elif npArr[j][3] == buyDate:
                                    close = npArr[j][0]
                                    div = npArr[j][2]
                                    break
                            if op == 0:
                                if symbol not in ignoreList:
                                    ignoreList.append(symbol)
                                else:
                                    print('DUPLICATED', symbol)
                                continue
                            if div == 0:
                                if symbol not in ignoreList:
                                    ignoreList.append(symbol)
                                else:
                                    print('DUPLICATED', symbol)
                                continue
                            divToPrice = div/op
                            if divToPrice < divToPriceTradeLimit: continue
                            if divToPrice > divToPriceLimit:
                                divToPriceLimit = divToPrice
                                tradeVol = balance/op
                                opPrice = op
                                payDiv = div
                                closePrice = close
                                payDate = i[1]
                        if tradeVol == 0: continue
                        balance -= tradeVol * opPrice
                        positions.append(
                            [tradeVol*(closePrice+payDiv),payDate]
                        )
                    break
            if balance > maxBalance:
                maxBalance = balance
                maxDivToPriceTradeLimit = divToPriceTradeLimit
                maxShift = shift
                print(maxBalance, maxDivToPriceTradeLimit, maxShift)
        shift += 1
        # print(positions)
        # print(balance)
        # print(ignoreList)
        # divToPriceList.sort()
        # print(divToPriceList)
    return balance

dividendCalendarDict = GetDividendCalanderDict()
symbolList = GetDividendCalandarSymbols(dividendCalendarDict)
dataDict = GetDataDict(symbolList)

startDate = '2020-03-18'
endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
dates = GetBusinessDays(startDate, endDate)
dateTimeList = []


oriDividendCalandarList = list(dividendCalendarDict.keys())

shift = 1
dividendCalendarList = oriDividendCalandarList
balance = Backtest(dividendCalendarDict, dividendCalendarList, dataDict, shift)

