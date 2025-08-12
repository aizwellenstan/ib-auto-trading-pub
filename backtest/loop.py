# @njit
def B(sA, npArr):
    npArr = npArr[-1058:]
    val = 0.01
    mB = 1
    cT = 1
    mR = 0
    mV = 0
    rV = 1
    while cT > 0.1 and rV > 0.01:
        b = 1
        for i in range(1, len(npArr)):
            if npArr[i][0] < npArr[i-1][3]:
                correlation = np.corrcoef(sA[:,3][:i], npArr[:,3][:i])[0, 1]
                if correlation < cT:
                    o = npArr[i][5]
                    if o < 0.01: 
                        mB = 0
                        break
                    t = (npArr[i-1][3] - npArr[i][0]) * rV + npArr[i][5]
                    if t - o < 0.01: continue
                    if t > npArr[i][1]:
                        t = npArr[i][3]
                    g = t / o
                    b *= g
        if b > mB:
            mB = b
            mV = cT
            mR = rV
        rV -= 0.01
        if rV <= 0.01:
            cT -= 0.01
            rV = 1

    res = np.empty(0)
    if mB <= 1:
        mB = 0
    res = np.append(res, mB/len(npArr))
    res = np.append(res, mV)
    res = np.append(res, mR)
    return res