fee = 1.001392062 * 2
wr = 35.8974358974359/100
tpVal = 5.7
base = 0.34
vol = 5
win = (base * tpVal * vol - fee) * wr  
loss = (base * vol + fee) * (1-wr)

print(win)
print(loss)
print(win-loss)

"""
op >100 vol >= 2
op > 50 vol >= 3
op > 10 vol = 5
"""