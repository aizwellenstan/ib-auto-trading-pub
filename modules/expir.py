import datetime as dt
from modules.same_week import same_week

def GetExpir(expir):
    today = dt.datetime.today()
    date_format = "%Y%m%d"
    expirTime = dt.datetime.strptime(expir, date_format)
    daysLeft = (expirTime - today).days + 1
    if  daysLeft > 7:
        daysLeft -= int(daysLeft/7+1)*2
    elif not same_week(today,expirTime):
        daysLeft -= 2
    print(f"daysLeft {daysLeft}")
    return daysLeft