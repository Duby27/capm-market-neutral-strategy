import pandas as pd
import yfinance as yf
from main import main
from strategy import make_pair

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
returns = returns.dropna()
rf = pd.read_csv('data/DGS3MO.csv')
rf['observation_date'] = pd.to_datetime(rf['observation_date'])
rf = rf.set_index('observation_date')
rf["DGS3MO"] = rf["DGS3MO"].ffill()
rf['annual'] = rf['DGS3MO']/100
rf['daily'] = (1+rf['annual'])**(1/252) - 1
data = returns.join(rf['daily'], how = 'left')


def backtest(data,rebatime,lookback = 252):
    return_list = []
    for end in range(lookback, len(data), rebatime):
        start = end - lookback
        window_data = data.iloc[start:end]
        window_results = main(window_data)
        window_pfl = make_pair(window_results)
        holding_data = data.iloc[end:end + rebatime]
        long_return = (1 + holding_data[window_pfl["long_what"]]).prod() - 1
        short_return = (1 + holding_data[window_pfl["short_what"]]).prod() - 1
        return_list.append(float((window_pfl['long_w']*long_return + window_pfl['short_w']*short_return)*100))
    return(return_list)

print(backtest(data, 5))