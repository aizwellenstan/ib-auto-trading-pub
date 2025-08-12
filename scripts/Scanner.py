from modules.aiztradingview import GetPerformance

scanner = GetPerformance()
symbol = 'MOTS'
if symbol in scanner:
    print('TRADE')