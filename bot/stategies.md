```python
    # combination = GetSPXBullPutCreaditSpread(5)
    combination = GetSPXBullCallCreaditSpread(5)
    # combination = GetSPXCustomBullPutCreaditSpread(5)
    spxPrice = GetSPXPrice()

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        print(comb)
        expir = comb['Expir']
        daysLeft = GetExpir(expir)
        spreadRange = spxPrice - comb['SellStrike']
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft
        ):
            if not npArr[i][6] == weekday: continue
            if npArr[i+daysLeft][3] < npArr[i][0] - spreadRange: capital -= comb['loss']
            else: capital += comb['profit']
        if capital > maxCapital:
            maxCapital = capital
            bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"BullCallCreaditSpread {bestCreaditSpread} \n"
    message += f"maxCapital {maxCapital}"
    Alert(message)

    combination = GetSPXBearPutCreaditSpread(5)
    spxPrice = GetSPXPrice()

    maxCapital = 0
    bestCreaditSpread = {}
    for comb in combination:
        print(comb)
        expir = comb['Expir']
        daysLeft = GetExpir(expir)
        spreadRange = comb['SellStrike'] - spxPrice
        capital = 0
        for i in range(
            1, len(npArr)-daysLeft
        ):
            if not npArr[i][6] == weekday: continue
            if npArr[i+daysLeft][3] > npArr[i][0] + spreadRange:
                capital -= comb['loss']
            else: capital += comb['profit']
        if capital > maxCapital:
            maxCapital = capital
            bestCreaditSpread = comb
    print(f"maxCapital {maxCapital}")
    print(f"bestCreaditSpread {bestCreaditSpread}")

    message = f"BearPutCreditSpread {bestCreaditSpread} \n"
    message += f"maxCapital {maxCapital}"
    Alert(message)
```