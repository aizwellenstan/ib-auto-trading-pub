j = 0
while j < len(marketCapLimitArr)-1:
    marketCapLimitArrIdx = j
    marketCapLimit = marketCapLimitArr[marketCapLimitArrIdx] + 1
    j += 1
    k = 0
    while k < len(volavgLimitArr)-1:
        volavgLimitArrIdx = k
        volavgLimit = volavgLimitArr[volavgLimitArrIdx] + 1
        k += 1

opLimitFloor = 13.60#13.598
while(opLimitFloor<50):
    opLimitCeil = 50
    while(opLimitCeil>13.598 and opLimitCeil>opLimitFloor):