from normalizeFloat import NormalizeFloat

def MathSign(n):
    if (n > 0): return(1)
    elif (n < 0): return (-1)
    else: return(0)

def MathFix(n, d):
    return(round(n*math.pow(10,d)+0.000000000001*MathSign(n))/math.pow(10,d))

def MathFixCeil(n, d):
    return(math.ceil(n*math.pow(10,d)+0.000000000001*MathSign(n))/math.pow(10,d))

def GetClosestPrice(price, arr, isBuy, isSell):
    curr = arr[0]
    arrSize = len(arr)
    # if(isBuy): price += (Ask - Bid)*2
    # if(isSell): price -= (Ask - Bid)*2
    idx = 0
    while idx <= arrSize-1:
        if (isBuy):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]>price):
                curr = arr[idx]
        if (isSell):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]<price):
                curr = arr[idx]
        idx += 1

    return curr

def GetLevel(price, buy, sell):
    mult = 0.0
    prc = 0.0
    lv0 = 0.0
    # lv25 = 0.0
    lv50 = 0.0
    # lv75 = 0.0
    digits = 0
    prc = MathFix(price, digits)
    mult = MathFixCeil(0.00001, digits)
    if (buy):
        lv0 = NormalizeFloat(prc+mult,price)
        # lv25 = NormalizeFloat(prc+0.25*mult,price)
        lv50 = NormalizeFloat(prc+0.5*mult,price)
        # lv75 = NormalizeFloat(prc+0.75*mult,price)
    if (sell):
        lv0 = NormalizeFloat(prc-mult,price)
        # lv25 = NormalizeFloat(prc-0.25*mult,price)
        lv50 = NormalizeFloat(prc-0.5*mult,price)
        # lv75 = NormalizeFloat(prc-0.75*mult,price)
    # arr = [lv0,lv25,lv50,lv75]
    arr = [lv0, lv50]
    # if (lv0>0 and lv25>0 and lv50>0 and lv75>0):
    if (lv0 > 0 and lv50 > 0):
        if (buy):
            return GetClosestPrice(price,arr,True,False)
        
        if (sell):
            return GetClosestPrice(price,arr,False,True)
    
    return price