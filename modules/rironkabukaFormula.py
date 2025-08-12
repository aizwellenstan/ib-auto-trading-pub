import math

def GetRironkabuka(bps, s, eps, price):
    s /= 100
    s = round(s, 3)
    discount_rate = 0.0
    if s >= 0.8:
        discount_rate = 0.8
    elif s >= 0.67:
        discount_rate = 0.75
    elif s >= 0.5:
        discount_rate = 0.7
    elif s >= 0.33:
        discount_rate = 0.65
    elif s >= 0.1:
        discount_rate = 0.6
    else:
        discount_rate = 0.5

    shisannkachi = bps * discount_rate

    pbr = price / bps
    # print("PBR", pbr)

    per = price / eps
    # print("PER", per)

    roa = eps / bps * s
    # print("ROA", roa)

    roe = round(eps / bps, 3)
    # print("ROE", roe)

    saimuLeverge = 1 / s
    adjusted_leverage = 1
    if saimuLeverge <= 1.53:
        adjusted_leverage = 1
    elif saimuLeverge <= 2:
        adjusted_leverage = 1.2
    elif saimuLeverge <= 2.5:
        adjusted_leverage = 1.36
    else:
        adjusted_leverage = 1.5

    jigyoukachi = int(eps * roa * 150 * adjusted_leverage)
    if eps <= 0: jigyoukachi = 0

    discountRate = 1
    if 0.41 <= pbr <= 0.49:
        discountRate = 0.8
    elif 0.34 <= pbr <= 0.40:
        discountRate = 0.67
    elif 0.25 <= pbr <= 0.33:
        discountRate = 0.5
    elif 0.21 <= pbr <= 0.25:
        discountRate = 0.34
    elif 0.076 <= pbr <= 0.20:
        discountRate = 1 - (min(max(((pbr / 5 * 50) + 50), 95), 85)) / 100
    elif 0.05 <= pbr < 0.076:
        discountRate = 1 - (min(max(((pbr - 1) * 10 + 5), 99.5), 95)) / 100
    elif 0.00 <= pbr < 0.05:
        discountRate = 1 - (min(max(((pbr - 1) * 10 + 5), 99.5), 97.5)) / 100

    shisannkachi = int(shisannkachi * discountRate)
    jigyoukachi = int(jigyoukachi * discountRate)

    rironkabuka = shisannkachi + jigyoukachi
    return [rironkabuka, shisannkachi, jigyoukachi]

if __name__ == "__main__":
    bps = 2000
    # 自己資本比率
    s = 1
    eps = 200
    price = 151
    rironkabuka = GetRironkabuka(bps, s, eps, price)
    print(rironkabuka)