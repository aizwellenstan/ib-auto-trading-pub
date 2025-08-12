def ExecTrail(op, sl, tp):
    print(op, sl, tp)

def GetExtreamOp(signal, vol, op, sl, tick_val=5):
    extreamOp = op
    for i in range(1, vol + 1):
        if signal == 1:
            if op <= sl: 
                sl = op - tick_val
        else:
            if op >= sl: 
                sl = op + tick_val
        extreamOp = op
        if signal == 1:
            op -= tick_val
            sl += tick_val
        else:
            op += tick_val
            sl -= tick_val
    return extreamOp

vol = 9
op = 38515
sl = 38560
tp = 37960
signal = -1
tick_val = 5
extreamOp = GetExtreamOp(signal, vol, op, sl, tick_val)
for i in range(1, vol + 1):
    if signal == 1:
        if sl >= extreamOp: 
            sl = extreamOp - tick_val
    else:
        if op <= extreamOp: 
            sl = extreamOp + tick_val
    ExecTrail(op, sl, tp)
    if signal == 1:
        op -= 5
        sl += 5
        tp += 100
    else:
        op += 5
        sl -= 5
        tp -= 100