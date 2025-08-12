import datetime

def same_week(d1, d2):
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
            and d1.year == d2.year