import pandas as pd
import yfinance as yf
import statsmodels.api as sm

start_date = "2020-12-31"
end_date = "2026-01-01"

stocks = pd.read_csv('data/selected_stocks.csv')

tickers = stocks["Symbol"].tolist()
market_ticker = '^GSPC'

prices = yf.download(
    tickers + [market_ticker],
    start=start_date,
    end=end_date,
    auto_adjust=True,
)

close_prices = prices["Close"]
returns = close_prices.pct_change()
#print(returns.isna().sum()) #result 1 1 1 1 1 1 1 1 1 1 1
#print(returns[returns.isna().any(axis=1)]) #result 2020-12-31   NaN   NaN  NaN NaN  NaN  NaN   NaN   NaN   NaN  NaN    NaN
returns = returns.dropna()



rf = pd.read_csv('data/DGS3MO.csv')

rf['observation_date'] = pd.to_datetime(rf['observation_date'])
rf = rf.set_index('observation_date')
# print(rf['DGS3MO'].isna().sum())
# print(rf[rf['DGS3MO'].isna()])
rf["DGS3MO"] = rf["DGS3MO"].ffill()
rf['annual'] = rf['DGS3MO']/100
rf['daily'] = (1+rf['annual'])**(1/252) - 1

data = returns.join(rf['daily'], how = 'left')
# print(data['daily'].isna().sum())

def main(data):
    stocks_excess = data[tickers].sub(data['daily'], axis = 0)
    market_excess = data['^GSPC'].sub(data['daily'], axis = 0)
    market_excess.name = "market_excess"
    results_list = []
    X = market_excess
    X = sm.add_constant(X)
    for ticker in tickers:
        Y = stocks_excess[ticker]
        model = sm.OLS(Y, X)
        results = model.fit()
        results_list.append({
            'ticker':ticker,
            'alpha': results.params['const'],
            'alpha_se': results.bse['const'],
            'alpha_t': results.tvalues['const'],
            'beta': results.params['market_excess'],
            'beta_se': results.bse['market_excess'],
            'beta_t': results.tvalues['market_excess'],
            'R_squared': results.rsquared,
            'alpha_p': results.pvalues['const'],
            'beta_p': results.pvalues['market_excess'],
        
        })
    results_df = pd.DataFrame(results_list)
    return(results_df)




