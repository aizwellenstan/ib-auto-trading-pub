import numpy as np

def GetDftRsi(close_prices):
    window = 50
    frac = 0.5
    hp = 0
    dft_rsi_values = []
    for i in range(5, len(close_prices)):
        per = 360 / 40
        alpha1 = (1 - np.sin(np.radians(per))) / np.cos(np.radians(per)) if np.cos(np.radians(per)) != 0 else 0
        
        hp = 0.5 * (1 + alpha1) * (close_prices[i] - close_prices[i - 1]) + alpha1 * hp
        cleaned_data = (hp + 2 * hp + 3 * hp + 3 * hp + 2 * hp + hp) / 12

        cos_part = np.zeros(window)
        sine_part = np.zeros(window)
        pwr = np.zeros(window)
        for period in range(8, window):
            cos_part[period] = 0
            sine_part[period] = 0
            for n in range(window):
                cyc_per = (360 * n) / period
                cos_part[period] += cleaned_data[n] * np.cos(np.radians(cyc_per))
                sine_part[period] += cleaned_data[n] * np.sin(np.radians(cyc_per))
            pwr[period] = cos_part[period] ** 2 + sine_part[period] ** 2

        max_pwr = max(pwr[8:])
        db = [-10 * np.log(0.01 / (1 - 0.99 * pwr_val / max_pwr)) / np.log(10) if max_pwr > 0 and pwr_val > 0 else 0 for pwr_val in pwr]

        num = sum(period * (3 - db_val) for period, db_val in enumerate(db[8:], start=8) if db_val < 3)
        denom = sum(3 - db_val for db_val in db[8:] if db_val < 3)
        dominant_cycle = num / denom if denom != 0 else 0

        abs_change = abs(close_prices[i] - close_prices[i - 1])
        rsi_array = [50 * (net_chg_avg / tot_chg_avg + 1) if tot_chg_avg != 0 else 50 for net_chg_avg, tot_chg_avg in zip(net_chg_avgs, tot_chg_avgs)]
        dft_rsi_values.append(rsi_array[min(int(frac * dominant_cycle), 50)])

    return dft_rsi_values