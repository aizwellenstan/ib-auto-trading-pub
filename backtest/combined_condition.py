num = [1,2]
ohlc = ['close','high','low','open']
gs = ['>','<']
curentCombined = 1
conditionCombined = 2

con1 = ''
conohlc1 = ''
congs = ''
con2 = ''
conohlc2 = ''
strExcute = ''

while curentCombined <= conditionCombined:
    if conditionCombined == 1:
        for i in num:
            con1 = 'd1[%i]'%(i)
            for j in ohlc:
                conohlc1 = '.'+j
                for k in gs:
                    congs = k
                    for l in num:
                        if l < i: continue
                        con2 = 'd1[%i]'%(l)
                        for m in ohlc:
                            if i == l:
                                if j != 'close': continue
                                if m != 'open': continue
                            conohlc2 = '.'+m
                            strExcute = con1+conohlc1+congs+con2+conohlc2
                            print(strExcute)
    else:
        lastStrExcute = strExcute
        for i in num:
            con1 = 'd1[%i]'%(i)
            for j in ohlc:
                conohlc1 = '.'+j
                for k in gs:
                    congs = k
                    for l in num:
                        if l < i: continue
                        con2 = 'd1[%i]'%(l)
                        for m in ohlc:
                            if i == l:
                                if j != 'close': continue
                                if m != 'open': continue
                            conohlc2 = '.'+m
                            if strExcute == lastStrExcute: continue
                            strExcute = lastStrExcute+con1+conohlc1+congs+con2+conohlc2+' and '
                            print(strExcute)
    curentCombined += 1