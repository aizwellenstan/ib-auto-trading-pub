def risk1(pr, win, cap):
    qp = (1 - win) / win
    return pow(qp, cap)

def risk2(pr, win, cap):
    qp = (1 - win) / win
    return pow(pow(0.25 + qp, 0.5) - 0.5, cap)

def riskN(pr, win, cap):
    a_o = 1 - win #initialization of newton method for numerical computation
    a_k = a_o; #a_k is the kth iteration for a in the newton computation
    error = 10

    finished = False

    while (not finished):
        a_k = a_k + ((1 - win) + win * pow(a_k, (pr + 1)) - a_k) / (1 - win * (pr + 1) * pow(a_k, pr))
        error = abs(a_k - ((1 - win) + win * pow(a_k, (pr + 1))))

        finished = error < 0.0001

    return pow(a_k, cap)

def calcRisk(pr, ac, eq):
    cap = 100 / eq

    risk = 0.0
    if (pr == 1):
        risk = risk1(pr, ac, cap)
    elif (pr == 2):
        risk = risk2(pr, ac, cap)
    else:
        risk = riskN(pr, ac, cap)

    return risk


# calcRisk(pr, ac, eq)
# print(calcRisk(3, 0.3, 10))