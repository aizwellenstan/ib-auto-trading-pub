import pandas as pd
import sys
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.utils import IndicatorMixin

class AccDistIndexIndicator(IndicatorMixin):
    """Accumulation/Distribution Index (ADI)
    Acting as leading indicator of price movements.
    https://school.stockcharts.com/doku.php?id=technical_indicators:accumulation_distribution_line
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.
    """

    def __init__(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        fillna: bool = False,
    ):
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        clv = ((self._close - self._low) - (self._high - self._close)) / (
            self._high - self._low
        )
        clv = clv.fillna(0.0)  # float division by zero
        adi = clv * self._volume
        self._adi = adi.cumsum()

    def acc_dist_index(self) -> pd.Series:
        """Accumulation/Distribution Index (ADI)
        Returns:
            pandas.Series: New feature generated.
        """
        adi = self._check_fillna(self._adi, value=0)
        return pd.Series(adi, name="adi")

def GetADL(df):
    df = AccDistIndexIndicator(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        volume=df['Volume']
    ).acc_dist_index()
    
    adlArr = df.dropna().values.tolist()
    return adlArr


# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# df = GetADLt(df)

# print(df)