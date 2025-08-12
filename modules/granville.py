def judge_ma_rule1(t, price, days_average, down_length=2, horizontal_length=3, scale=0.0005, scale0=0.00094, period=75):
    label = 0  # Initial label signal is not clear
    count_down = 0
    count_horizontal = 0
   
    while t >= period:
        tmp = (days_average[t] - days_average[t - 1]) / days_average[t]
        if abs(tmp) < scale:
            count_horizontal += 1
            t -= 1
        else: break

    while t >= period:
        tmp = (days_average[t] - days_average[t - 1]) / days_average[t]
        if tmp < -scale0:
            count_down += 1
            t -= 1
        else: break

    t = t + count_down + count_horizontal

    if count_down >= down_length and count_horizontal >= horizontal_length:
        if price[t] > days_average[t] and price[t - 1] <= days_average[t - 1]:
            label = 1
    return label

def judge_ma_rule2(t, price, days_average, low_length=3, up_length=20, scale=0.04, period=75):
    label = 0
    count_low = 0
    count_up = 0

    while t >= period:
        if price[t] > days_average[t] * (1 - scale) and price[t] < days_average[t]:
            count_low += 1
            t -= 1
        else: break

    while t >= period:
        if price[t] >= days_average[t] * (1 + scale):
            count_up += 1
            t -= 1
        else: break

    t = t + count_up + count_low
    if 1 <= count_low <= low_length and count_up >= up_length:
        if days_average[t] > days_average[t - 1] and days_average[t - 1] > days_average[t - 2]:
            label = 1

    return label

def judge_ma_rule3(t, price, days_average, down_length=2, scale=0.09, period=75):
    label = 0
    count_down = 0

    if price[t] > price[t - 1] and price[t - 1] > days_average[t - 1]:
        t -= 1
        while t >= period:
            if price[t] < price[t - 1]:
                count_down += 1
            else: break
            t -= 1

        if 1 <= count_down <= down_length and price[t] > days_average[t] * (1 + scale):
            label = 1

    return label

def judge_ma_rule4(t, price, days_average, down_length=3, scale=0.015, period=75):
    label = 0
    count_down = 0

    if price[t] > price[t - 1]:
        t -= 1
        while t >= period:
            if price[t] < price[t - 1] * (1 - scale) and days_average[t] < days_average[t - 1]:
                count_down += 1
            else: break
            t -= 1

    if count_down >= down_length and price[t] > days_average[t]:
        label = 1

    return label

def judge_ma_rule5(t, price, days_average, down_length=3, horizontal_length=6, scale=0.0005, scale0=0.0025, period=75):
    label = 0
    count_down = 0
    count_horizontal = 0

    while t >= period:
        tmp = (days_average[t] - days_average[t - 1]) / days_average[t]
        if tmp < -scale0:
            count_down += 1
            t -= 1
        else: break

    while t >= period:
        tmp = (days_average[t] - days_average[t - 1]) / days_average[t]
        if tmp > -scale:
            count_horizontal += 1
            t -= 1
        else: break

    t = t + count_down + count_horizontal

    if count_down >= down_length and count_horizontal >= horizontal_length:
        if price[t] < days_average[t]:
            label = -1

    return label

def judge_ma_rule6(t, price, days_average, down_length=3, up_length=3, period=75):
    label = 0
    count_down = 0
    count_up = 0

    while t >= period:
        if price[t] < price[t - 1]:
            count_down += 1
            t -= 1
        else: break

    while t >= period:
        if price[t] > price[t - 1]:
            count_up += 1
            t -= 1
        else: break

    t = t + count_up + count_down

    if price[t - count_down] > days_average[t - count_down] and price[t] < days_average[t]:
        if days_average[t - 1] > days_average[t]:
            if count_down >= down_length and count_up >= up_length:
                label = -1

    return label

def judge_ma_rule7(t, price, days_average, down_length=4, up_length=5, period=75):
    label = 0
    count_down = 0
    count_up = 0

    while t >= period:
        if price[t] < price[t - 1]:
            count_down += 1
            t -= 1
        else: break

    while t >= period:
        if price[t] > price[t - 1]:
            count_up += 1
            t -= 1
        else: break

    t = t + count_up + count_down

    if price[t - count_down] < days_average[t - count_down]:
        if count_down >= down_length and count_up >= up_length:
            label = -1

    return label

def judge_ma_rule8(t, price, days_average, up_length=5, scale=0.02, scale0=0.08, period=75):
    label = 0
    count_up = 0

    if price[t] > price[t - 1]:
        t -= 1
        while t >= period:
            if price[t] > price[t - 1] * (1 + scale) and (price[t] / days_average[t]) > (price[t - 1] / days_average[t - 1]):
                count_up += 1
            else: break
            t -= 1

    if count_up >= up_length and (price[t + count_up] / days_average[t + count_up]) > (1 + scale0):
        label = -1

    return label