def DSRI(df):
  return (df["receivables"] / df["sales"]) / (df["receivables_t2"] / df["sales_t2"])

def GMI(df):
  return (df["sales_t2"] - df["cogs_t2"]) / (df["sales"] - df["cogs"])

def AQI(df):
  AQI_t1 = (1 - (df["ppe"] + df["current_assets"]) / df["total_assets"])
  AQI_t2 = (1 - (df["ppe_t2"] + df["current_assets_t2"]) / df["total_assets_t2"])
  return AQI_t1 / AQI_t2

def SGI(df):
  return (df["sales"] / df["sales_t2"])

def DEPI(df):
  DEPI_t1 = (df["depreciation"] / (df["depreciation"] + df["ppe"]))
  DEPI_t2 = (df["depreciation_t2"] / (df["depreciation_t2"] + df["ppe_t2"]))
  return DEPI_t1 / DEPI_t2

def SGAI(df):
  return (df["sga"] / df["sales"]) / (df["sga_t2"] / df["sales_t2"])

def LVGI(df):
  return (df["debt"] / df["total_assets"]) / (df["debt_t2"] / df["total_assets_t2"])

def TATA(df):
  return (df["inc"] - df["ncf"]) / df["total_assets"]

def get_m_score(df):
  df["m-score"] = -4.84 + 0.92 * DSRI(df) + \
                  0.528 * GMI(df) + \
                  0.404 * AQI(df) + \
                  0.892 * SGI(df) + \
                  0.115 * DEPI(df) + \
                  -0.172 * SGAI(df) + \
                  4.679 * TATA(df) + \
                  -0.327 * LVGI(df)

def get_z_score(df):
  df["z-score"] = 1.2 * df['working_capital_to_assets'] + \
                  1.4 * df['retained_to_assets'] + \
                  3.3 * df['ebit_to_assets'] + \
                  0.6 * df['market_cap_to_liabilities'] + \
                  1.0 * df['asset_turnover']

import eikon as ek 
import pandas as pd 
import sys
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly as pyo

app_key = '5fb91f99d734474788e7862bd1f3b2afe0b15012'
ek.set_app_key(app_key)
chain = '0#.SPX'
dates = pd.date_range('1993', '2022', freq = 'YS')
fields = [
    'TR.TotalReturn52Wk',  # 52 Week Returns
    "TR.GICSSector"        # GICS Sector
]

beneish_fields = [
    "TR.F.LoansRcvblTot",            # Receivables
    "TR.F.TotRevBizActiv",           # Sales
    "TR.F.COGSTot",                  # Costs of goods sold
    "TR.F.PPEGrossTot",              # Property plant and equipment
    "TR.F.TotCurrAssets",            # Current assets
    "TR.F.TotAssets",                # Total assets
    "TR.F.DeprTot",                  # Depreciation
    "TR.F.SGATot",                   # Sales General and Administrative Expenses 
    "TR.F.IncBefDiscOpsExordItems",  # Income before discontinued operations and extraordinary items
    "TR.F.NetCashFlowOp",            # Net cash flow from operating activities
    "TR.F.DebtTot"                   # Total debt
]

altman_fields = [
    "TR.F.WkgCaptoTotAssets",        # Working capital to total assets
    "TR.F.RetainedEarntoTotAssets",  # Retained earnings to total assets
    "TR.F.EBITToTotAssets",          # EBIT to total assets
    "TR.F.MktCapToTotLiab",          # Market value of equity to liabilities
    "TR.F.AssetTurnover"             # Asset turnover
]

model_fields = beneish_fields + altman_fields

score_columns = ["z-score", "m-score"]

long_quantiles = {date:{column:{} for column in score_columns} for date in dates}
short_quantiles = {date:{column:{} for column in score_columns} for date in dates}

columns = {
  'Loans & Receivables - Total': "receivables",
  'Revenue from Business Activities - Total': "sales",
  'Cost of Revenues - Total': "cogs",
  'Property Plant & Equipment - Gross - Total': "ppe",
  'Total Current Assets': 'current_assets',
  'Total Assets': "total_assets",
  'Depreciation - Total': "depreciation",
  'Selling General & Administrative Expenses - Total': 'sga',
  'Income before Discontinued Operations & Extraordinary Items': 'inc',
  'Net Cash Flow from Operating Activities': 'ncf',
  'Debt - Total': 'debt',
  'Working Capital to Total Assets': 'working_capital_to_assets',
  'Retained Earnings - Total to Total Assets': 'retained_to_assets',
  'Earnings before Interest & Taxes (EBIT) to Total Assets': 'ebit_to_assets',
  'Market Capitalization to Total Liabilities': 'market_cap_to_liabilities',
  'Asset Turnover': 'asset_turnover'
}

columns_t2 = {x: f"{y}_t2" for x, y in columns.items()}

full_df = pd.DataFrame()

for i, date in enumerate(dates[2:-1],2):
  
  # Dates conversion to obtain the data from eikon
  
  date_0 = date.to_period('D')
  date_1 = dates[i-1].to_period('D')
  date_2 = dates[i-2].to_period('D')
  date_end = dates[i+1].to_period('D')
  
  # Creation of parameters to get data for selected years from eikon
  
  parameters_t2 = {'SDate': f"{date_2}", 'EDate': f"{date_1}", 'FRQ': 'FY'}
  parameters_t1 = {'SDate': f"{date_1}", 'EDate': f"{date_0}", 'FRQ': 'FY'}
  parameters_last = {'SDate': f"{date_end}"}
  
  # Here we obtain the data and store it in dataframes, get_data returns a tuple containing (dataframe, errores)
  # we are only interested in the dataframe so we ignore the errors
  
  df_t2 = ek.get_data(f"{chain}({date_0})", model_fields, parameters_t2)[0]
  df_t1 = ek.get_data(f"{chain}({date_0})", model_fields, parameters_t1)[0]
  rets = ek.get_data(f"{chain}({date_0})", fields, parameters_last)[0]
  
  # We drop the instruments with missing rows, rename the columns and set the index to that instrument
  
  df_t1 = df_t1.dropna().rename(columns = columns).set_index('Instrument')
  df_t2 = df_t2.dropna().rename(columns = columns_t2).set_index('Instrument')
  rets = rets.dropna().rename(columns = {
      '52 Week Total Return': 'returns',
      'GICS Sector Name': 'sector'
  }).set_index('Instrument')
  
  # We join the dataframes and store the year as a column
  
  df = rets.join(df_t1, how = "inner").join(df_t2, how = "inner") 
  df["date"] = date.to_period('Y')
  
  # We compute the z-score, the m-score and drop the strange values
  
  get_z_score(df)
  get_m_score(df)
  df = df.replace([np.inf, -np.inf, ""], np.nan).dropna()

  # We fill our dictionaries with the data of the first and the fifth quintile
  
  for column in score_columns:
      for sector in df["sector"].unique(): 
          long_quantiles[date][column][sector] = df[df["sector"] == sector][column].quantile(0.8)
          short_quantiles[date][column][sector] = df[df["sector"] == sector][column].quantile(0.2)    
  
  # Finally we store the data in our previously created dataframe and print the date to view the progress
  
  full_df = full_df.append(df, ignore_index = True)
  print(date)

def to_z_range(num):
  upper = 15
  lower = -10
  if num > upper: return upper
  elif num < lower: return lower
  else: return num

def to_m_range(num):
  upper = 0
  lower = -5
  if num > upper: return upper
  elif num < lower: return lower
  else: return num    

# We define a function with two parameters to plot the m-score or the z-score and across sectors or dates
    
def plot_score(m_score = True, sectors = True, title = ""):
  # We create some variables to make the neccesary changes depending on the selected parameters
  
  col = "m-score" if m_score else "z-score"
  fun = to_m_range if m_score else to_z_range
  title = "M-Score" if m_score else "Z-Score"
  across = "sector" if sectors else "date"
  height = 1000 if sectors else 1500

  # We define a boxplot, set the colors to the sector and plot the m-score in the y-axis 

  fig = px.box(
      color = full_df[across] if sectors else None,
      y = None if sectors else full_df[across].astype(str),
      x = full_df[col].apply(fun), 
      template = "plotly_white",
      orientation = 'h',
      width = 1000, 
      height= height
  )

  # We style the titles and fonts for our plot

  fig.update_layout(
      title = title,
      xaxis_title = title,
      yaxis_title = across.capitalize(),
      legend_title = across.capitalize(),
      legend_traceorder = "reversed",
      font = dict(size = 18),
  )

  # We dont want to plot all the extreme values as only one point

  fig.update_traces(jitter = 1)

  # Finally we show the plot

  fig.show()