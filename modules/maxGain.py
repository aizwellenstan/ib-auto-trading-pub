def max_result(arr):
    max_growth, cur_min, cur_min_idx = float('-inf'), float('inf'), -1
    res_l = res_h = float('-inf')
    for i, val in enumerate(arr):
        if val / cur_min > max_growth:
            max_growth = val / cur_min
            res_l, res_h = cur_min_idx, i
        if val < cur_min:
            cur_min, cur_min_idx = val, i
    return res_l + 1, res_h + 1, round(max_growth, 2)
