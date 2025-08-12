import numpy as np

def rciArr(close: np.ndarray,
        timeperiod: int = 9) -> np.ndarray:
    rank_target = [np.roll(close, i, axis=-1) for i in range(timeperiod)]
    rank_target = np.vstack(rank_target)[:, timeperiod - 1:]
    price_rank = np.argsort(np.argsort(rank_target[::-1], axis=0), axis=0) + 1
    time_rank = np.arange(1, timeperiod + 1).reshape(timeperiod, -1)
    aa = np.sum((time_rank - price_rank)**2, axis=0, dtype=float) * 6
    bb = float(timeperiod * (timeperiod**2 - 1))
    cc = np.divide(aa, bb, out=np.zeros_like(aa), where=bb != 0)
    rci = (1 - cc) * 100
    rci = np.concatenate([np.full(timeperiod - 1, np.nan), rci], axis=0)
    return rci