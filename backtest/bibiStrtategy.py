rootPath = "..";import sys;sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.irbank import GetPl

plPath = f"{rootPath}/backtest/pickle/pro/compressed/plbscfdividend.p"
plDict = LoadPickle(plPath)
print(len(plDict.keys()))

print(len(plDict["7686"]))

cleanPlDict = {}
for symbol in plDict.keys():
    for i in plDict[symbol]:
        if len(i) < 1: continue
    cleanPlDict[symbol] = plDict[symbol]
print(len(cleanPlDict))

# from modules.aiztradingview import GetCloseLargeJP

dailyGainnerList = ['7686', '6526', '3561', '3561', '3561', '3561', '9107', '8136', '3496', '4487', '7014', '4487', '4570', '4487', '6526', '7388', '4570', '3083', '4176', '3697', '7369', '7369', '7369',
'7369', '3561', '6027', '4570', '7369', '8750', '4487', '6526', '4739', '7369', '7687', '4570', '4570', '2222', '4046', '4570', '7214', '7214', '7014', '6526', '4570', '7369', '4570', '3561', '3399']


# for symbol in dailyGainnerList:
#     pl = GetPl(symbol)
#     print(pl)
# sys.exit()
# print(len(bibi))

# res = [
#             uriage,eigyourieki,keijyourieki,toukijunnrieki,
#             soushisan,junnshisan,
#             kabunushishihonn,riekijouyokin,
#             cash]

uriageChangeList = []
for symbol in dailyGainnerList:
    plbs = plDict[symbol]
    pl = plbs[0][-2]
    print(symbol,len(pl))
    # uriageIdx = 1
    # eigyouriekiIdx = 2
    keijyouriekiIdx = 3
    junnriekiIdx = 4
    hokatsuriekiIdx = 5
    epsIdx = 6
    roeIdx = 7
    roaIdx = 8

    eigyouriekiritsuIdx = 9
    gennkaritsuIdx = 10
    hankannhiritsuIdx = 11
    
    plLength = len(pl)
    if plLength == 11:
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiritsuIdx = 8
        gennkaritsuIdx = 9
        hankannhiritsuIdx = 10
    elif plLength == 8:
        keijyouriekiIdx = 2
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
    elif plLength == 9:
        print(symbol)
        sys.exit()
        junnriekiIdx = 3
        hokatsuriekiIdx = 4
        epsIdx = 5
        roeIdx = 6
        roaIdx = 7
        eigyouriekiritsuIdx = 8

    # if plLength > 8:
    #     eigyouriekiritsu = pl[eigyouriekiritsuIdx]
    #     uriageChangeList.append(eigyouriekiritsu)
    # if plLength > 10:
    #     hankannhiritsu = pl[hankannhiritsuIdx]
    #     uriageChangeList.append(hankannhiritsu)

    keijyourieki = pl[keijyouriekiIdx]
    if keijyourieki == "-": continue
    keijyourieki = int(keijyourieki)
    junnrieki = pl[junnriekiIdx]
    hokatsurieki = pl[hokatsuriekiIdx]
    eps = pl[epsIdx]
    roe = pl[roeIdx]
    roa = pl[roaIdx]
    

    
    bs = plbs[1][-1]
    bs2 = plbs[1][-2]
    bsLength = len(bs)
    # soushisanIdx = 1
    junnshisanIdx = 2
    kabunushishihonnIdx = 3
    jikoushihonhiritsuIdx = 4
    riekijouyokinIdx = 5
    yuurishifusaiIdx = 6
    bpsIdx = 8
    if bsLength == 7:
        bpsIdx = 6
    # soushisan = bs[soushisanIdx]
    junnshisan = bs[junnshisanIdx]
    junnshisan2 = bs2[junnshisanIdx]
    kabunushishihonn = bs[kabunushishihonnIdx]
    jikoushihonhiritsu = bs[jikoushihonhiritsuIdx]
    riekijouyokin = bs[riekijouyokinIdx]
    yuurishifusai = bs[yuurishifusaiIdx]
    bps = bs[bpsIdx]
    
    


    cf = plbs[2][-1]
    cf2 = plbs[2][-2]
    cfLength = len(cf)
    eigyoucf = cf[1]
    toushicf = cf[2]
    saimucf = cf[3]
    freecf = cf[4]
    setsubitoushi = cf[5]
    gennkin = cf[6]
    gennkin2 = cf2[6]
    eigyoucfmargin = cf[7]

    dividend = plbs[3][-1]
    dividendLength = len(dividend)
    kabunushisourimawariIdx = 9
    shihyourimawariIdx = 9
    if dividendLength == 3:
        kabunushisourimawariIdx = 1
        shihyourimawariIdx = 2
    elif dividendLength == 6:
        kabunushisourimawariIdx = 4
        shihyourimawariIdx = 5
    elif dividendLength == 7:
        kabunushisourimawariIdx = 5
        shihyourimawariIdx = 6
    
    # if dividendLength in [3, 6, 7, 10]:
    #     print(symbol, dividendLength)
    #     kabunushisourimawari = dividend[kabunushisourimawariIdx]
    #     shihyourimawari = dividend[shihyourimawariIdx]
    #     if shihyourimawari != "-":
    #         uriageChangeList.append(kabunushisourimawari)
    # if dividendLength in [4, 10]:
    #     junnshisanhaitouritsuIdx = 4
    #     if dividendLength == 4:
    #         junnshisanhaitouritsuIdx = 3

    #     haitouseikouIdx = 2
    #     haitouseikou = dividend[haitouseikouIdx]

    #     junnshisanhaitouritsu = dividend[junnshisanhaitouritsuIdx]
    #     if junnshisanhaitouritsu != "-":
    #         uriageChangeList.append(junnshisanhaitouritsu)
    
    # if dividendLength in [5, 6, 7, 10]:
    #     jishakabukaiIdx = 5
    #     if dividendLength == 5:
    #         jishakabukaiIdx = 2
    #     elif dividendLength == 6:
    #         jishakabukaiIdx = 1
    #     elif dividendLength == 7:
    #         jishakabukaiIdx = 2

    #     jishakabukai = dividend[jishakabukaiIdx]

    if dividendLength == 10:
        jouyokinnhaitouIdx = 3

        jouyokinnhaitou = dividend[jouyokinnhaitouIdx]
        if jouyokinnhaitou != "-":
            uriageChangeList.append(jouyokinnhaitou)

        # if haitouseikou != "-":
        #     uriageChangeList.append(haitouseikou)
    # break
    # if dividendLength == 3:
    #     kabunushisourimawariIdx = 2
    #     shihyourimawariIdx = 3
    # if dividendLength == 4:
    #     print(symbol)
    #     sys.exit()
    # if dividendLength in [5, 6, 7, 10]:
    #     soukanngengakuIdx = 6
    #     soukanngenseikouIdx = 7
    #     if dividendLength == 5:
    #         soukanngengakuIdx = 3
    #         soukanngenseikouIdx = 4
    #     elif dividendLength == 6:
    #         soukanngengakuIdx = 2
    #         soukanngenseikouIdx = 3
    #     elif dividendLength == 7:
    #         soukanngengakuIdx = 3
    #         soukanngenseikouIdx = 4
    #     soukanngengaku = dividend[soukanngengakuIdx]
    #     soukanngenseikou = dividend[soukanngenseikouIdx]
    #     if soukanngengaku != "-":
    #         uriageChangeList.append(soukanngengaku)
uriageChangeList.sort()
print(uriageChangeList)

# symbolList = list(GetCloseLargeJP().keys())[:4000]
# print(len(symbolList))
# for symbol in bibi:
#     if symbol not in symbolList:
#         print("ERR", symbol)