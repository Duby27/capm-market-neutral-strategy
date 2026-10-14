import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
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
    return_daily_list = []
    for end in range(lookback, len(data), rebatime):
        start = end - lookback
        window_data = data.iloc[start:end]
        window_results = main(window_data)
        window_pfl = make_pair(window_results)
        holding_data = data.iloc[end:end + rebatime]
        long_return = (1 + holding_data[window_pfl["long_what"]]).prod() - 1
        short_return = (1 + holding_data[window_pfl["short_what"]]).prod() - 1
        return_list.append(float((window_pfl['long_w']*long_return + window_pfl['short_w']*short_return)*100))

        long_growth = (
            1 + holding_data[window_pfl["long_what"]]
        ).cumprod()

        short_growth = (
            1 + holding_data[window_pfl["short_what"]]
        ).cumprod()

        holding_value = (
            1 + window_pfl['long_w'] * (long_growth - 1)+ window_pfl['short_w'] * (short_growth - 1)
            #try to simulate the value of my pfl. Because if I want to keep w constant in rebatime I would have to rebalance every day.
            #which is a contradiction. 
            #I actually find this tricky. Not sure it's the best way to calculate daily pfl return
        )

        daily_return = holding_value.pct_change()
        daily_return.iloc[0] = holding_value.iloc[0] - 1 #manually update the first day return. or it would be NaN
        for day in holding_data.index:
            return_daily_list.append({
                'date' : day,
                'return' : float(daily_return.loc[day]),
            })
    
    return(return_list, return_daily_list)

return_list, return_daily_list, = backtest(data, 5)
results_daily = pd.DataFrame(return_daily_list)
results_daily['equity'] = (1 + results_daily['return']).cumprod()


daily_volatility = results_daily["return"].std()
annual_volatility = daily_volatility * np.sqrt(252)
cumulative_return = results_daily["equity"].iloc[-1] - 1
print(f"Cumulative Return: {cumulative_return:.2%}")
print(f"Annualized Volatility: {annual_volatility:.2%}")


results_daily['max_so_far'] = results_daily['equity'].cummax()
results_daily['drawdown'] = 1 - results_daily['equity']/results_daily['max_so_far']
print(f"Maximum Drawdown: {max(results_daily['drawdown']):.2%}")


results_daily = results_daily.set_index('date')
results_daily['excess_return'] = (results_daily['return'] - data['daily'])
annual_sharpe = (
    results_daily['excess_return'].mean()/ results_daily['excess_return'].std()* np.sqrt(252)
)
print(f"Annualized Sharpe Ratio: {annual_sharpe:.2f}") #should not actually invest money in it.

final_regression_data = pd.DataFrame({
    "portfolio": results_daily["return"],
    "market": data["^GSPC"]
}).dropna()
X = sm.add_constant(final_regression_data['market'])
Y = final_regression_data['portfolio']
model = sm.OLS(Y, X)
final_results = model.fit()
print(f"Realized Beta: {final_results.params["market"]:.4f}")
print(f"Beta Standard Error: {final_results.bse["market"]:.4f}")


plt.plot(results_daily.index, results_daily["equity"])
plt.title("CAPM Beta-Neutral Portfolio")
plt.xlabel("Date")
plt.ylabel("Equity")
plt.grid(True)
plt.show()