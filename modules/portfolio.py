import pandas as pd
SCANNER_URL = "https://www.portfoliovisualizer.com/backtest-portfolio?s=y&timePeriod=4&startYear=1985&firstMonth=1&endYear=2023&lastMonth=12&calendarAligned=true&includeYTD=false&initialAmount=10000&annualOperation=0&annualAdjustment=0&inflationAdjusted=true&annualPercentage=0.0&frequency=4&rebalanceType=1&absoluteDeviation=5.0&relativeDeviation=25.0&leverageType=0&leverageRatio=0.0&debtAmount=0&debtInterest=0.0&maintenanceMargin=25.0&leveragedBenchmark=false&reinvestDividends=true&showYield=false&showFactors=false&factorModel=3&benchmark=-1&benchmarkSymbol="

def GetSharpeSortino(benchmark, symbol):
    try:
        url = SCANNER_URL+f"{benchmark}&portfolioNames=false&portfolioName1=Portfolio+1&portfolioName2=Portfolio+2&portfolioName3=Portfolio+3&symbol1={symbol}&allocation1_1=100"
        tables = pd.read_html(url)
        df = tables[1]
        # Portfolio,Initial Balance,Final Balance,CAGR,Stdev,Best Year,Worst Year,Max. Drawdown,Sharpe Ratio,Sortino Ratio,Market Correlation
        df = df.assign(mdd=df['Max. Drawdown'].str[:-1].astype(float))
        df = df.assign(cagr=df['CAGR'].str[:-1].astype(float))
        df = df[['Sharpe Ratio','Sortino Ratio','mdd','cagr']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def GetData(symbol):
    try:
        url = f"https://www.portfoliovisualizer.com/backtest-portfolio?s=y&timePeriod=4&startYear=1985&firstMonth=1&endYear=2023&lastMonth=12&calendarAligned=true&includeYTD=false&initialAmount=10000&annualOperation=0&annualAdjustment=0&inflationAdjusted=true&annualPercentage=0.0&frequency=4&rebalanceType=1&absoluteDeviation=5.0&relativeDeviation=25.0&leverageType=0&leverageRatio=0.0&debtAmount=0&debtInterest=0.0&maintenanceMargin=25.0&leveragedBenchmark=false&reinvestDividends=true&showYield=false&showFactors=true&factorModel=5&benchmarkSymbol=SPY&portfolioNames=false&portfolioName1=Portfolio+1&portfolioName2=Portfolio+2&portfolioName3=Portfolio+3&symbol1={symbol}&allocation1_1=100"
        tables = pd.read_html(url)
        df = tables[1]
        # Portfolio,Initial Balance,Final Balance,CAGR,Stdev,Best Year,Worst Year,Max. Drawdown,Sharpe Ratio,Sortino Ratio,Market Correlation
        df = df.assign(mdd=df['Max. Drawdown'].str[:-1].astype(float))
        df = df.assign(cagr=df['CAGR'].str[:-1].astype(float))
        df = df[['Sharpe Ratio','Sortino Ratio','mdd','cagr']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def GetDataShort(symbol):
    try:
        url = f"https://www.portfoliovisualizer.com/backtest-portfolio?s=y&timePeriod=2&startYear=2021&firstMonth=3&endYear=2023&lastMonth=12&calendarAligned=true&includeYTD=false&initialAmount=10000&annualOperation=0&annualAdjustment=0&inflationAdjusted=true&annualPercentage=0.0&frequency=4&rebalanceType=1&absoluteDeviation=5.0&relativeDeviation=25.0&leverageType=0&leverageRatio=0.0&debtAmount=0&debtInterest=0.0&maintenanceMargin=25.0&leveragedBenchmark=false&reinvestDividends=true&showYield=false&showFactors=true&factorModel=5&benchmarkSymbol=SPY&portfolioNames=false&portfolioName1=Portfolio+1&portfolioName2=Portfolio+2&portfolioName3=Portfolio+3&symbol1={symbol}&allocation1_1=100"
        tables = pd.read_html(url)
        df = tables[1]
        # Portfolio,Initial Balance,Final Balance,CAGR,Stdev,Best Year,Worst Year,Max. Drawdown,Sharpe Ratio,Sortino Ratio,Market Correlation
        df = df.assign(mdd=df['Max. Drawdown'].str[:-1].astype(float))
        df = df.assign(cagr=df['CAGR'].str[:-1].astype(float))
        df = df[['Sharpe Ratio','Sortino Ratio','mdd','cagr']]
        npArr = df.to_numpy()
        return npArr[0]
    except: return []

def GetSharpe50(benchmark, symbol1, symbol2):
    try:
        url = SCANNER_URL+f"{benchmark}&portfolioNames=false&portfolioName1=Portfolio+1&portfolioName2=Portfolio+2&portfolioName3=Portfolio+3&symbol1={symbol1}&allocation1_1=50&symbol2={symbol2}&allocation2_1=50"
        tables = pd.read_html(url)
        df = tables[1]
        # Portfolio,Initial Balance,Final Balance,CAGR,Stdev,Best Year,Worst Year,Max. Drawdown,Sharpe Ratio,Sortino Ratio,Market Correlation
        df = df.assign(mdd=df['Max. Drawdown'].str[:-1].astype(float))
        df = df.assign(cagr=df['CAGR'].str[:-1].astype(float))
        df = df[['Sharpe Ratio','Sortino Ratio','mdd','cagr']]
        npArr = df.to_numpy()
        return npArr
    except: return []

if __name__ == '__main__':
    GetCagr("BME")