# CAPM-Based Market-Neutral Strategy

## Overview

This project investigates the market exposure of a cross-sector universe of U.S. equities using the Capital Asset Pricing Model (CAPM).

CAPM regressions are used to estimate each stock's alpha, beta, statistical significance, and R-squared. The project then extends the analysis into a long-short strategy: stocks are selected using their estimated alpha t-statistics, while CAPM beta is used to construct hedge ratios designed to reduce market exposure.

The primary objective is to investigate whether a portfolio constructed to be beta-neutral using historical estimates can maintain low realized market exposure out of sample, rather than necessarily generate positive returns(and in fact it didn't).

The strategy is evaluated using a rolling out-of-sample backtest.

## Methodology

### Stock Universe

The initial universe is obtained from the Nasdaq Stock Screener for U.S.-listed securities. Because the raw screener also contains other security types such as warrants and preferred shares, the highest-market-cap candidates are manually checked to ensure that the final universe consists of ordinary equity shares. The two largest stocks from each non-miscellaneous sector are selected, producing a cross-sector universe of 22 U.S. equities.

### Data

Historical daily stock prices and S&P 500 (^GSPC) market data are obtained using Yahoo Finance via the `yfinance` package. Adjusted closing prices are converted into daily percentage returns.

The 3-month U.S. Treasury yield (DGS3MO) is used as a proxy for the risk-free rate. Annual percentage yields are converted into daily rates assuming 252 trading days per year, applying compounding interests. Stock and market excess returns are then calculated by subtracting the daily risk-free rate.

### CAPM Regression

For each stock, the following CAPM regression is estimated using ordinary least squares (OLS):

$$
R_{i,t} - R_{f,t}
=
\alpha_i
+
\beta_i (R_{m,t} - R_{f,t})
+
\epsilon_{i,t}
$$

where \(R_{i,t}\) is the return of stock \(i\), \(R_{m,t}\) is the market return, and \(R_{f,t}\) is the risk-free rate at time \(t\).

The regression estimates each stock's alpha and beta, together with their standard errors, t-statistics, and p-values. R-squared is also recorded to measure the proportion of variation in the stock's excess return explained by the market excess return.

## Strategy Extension

The CAPM analysis is extended into a two-stock long-short strategy. At each rebalancing date, CAPM regressions are estimated over a rolling historical window.

The stock with the highest alpha t-statistic is selected for the long position, while the stock with the lowest alpha t-statistic is selected for the short position. The alpha t-statistic is used rather than raw alpha so that the magnitude of estimated alpha is considered relative to its statistical uncertainty.

CAPM beta is then used to determine the portfolio weights. The long and short weights are chosen to satisfy:

$$
w_L \beta_L + w_S \beta_S = 0
$$

subject to a gross exposure of one:

$$
|w_L| + |w_S| = 1.
$$

For positive stock betas, this gives:

$$
w_L = \frac{\beta_S}{\beta_L+\beta_S},
\qquad
w_S = -\frac{\beta_L}{\beta_L+\beta_S}.
$$

The resulting portfolio is therefore constructed to be beta-neutral with respect to the estimated CAPM betas. Beta is used only for hedging market exposure and not as a return-prediction signal.


## Backtesting
The strategy is evaluated through a rolling out-of-sample backtest covering approximately 2022–2025.

Estimation window: 252 trading days.

Rebalancing interval: 5 trading days.

Portfolio: One long position and one short position.

Holding assumption: Fixed share quantities between rebalancing dates.

At each rebalancing date, CAPM parameters are estimated using the preceding 252 trading days. The estimated betas are used to construct a new long-short portfolio, which is then held for the following five trading days.

To account for changes in portfolio weights during the holding period, daily portfolio values are calculated using cumulative stock returns:

$$
V_t=1+w_L(G_{L,t}-1)+w_S(G_{S,t}-1)
$$

where $G_{L,t}$ and $G_{S,t}$ are the cumulative growth factors of the selected stocks since the most recent rebalance.

Daily portfolio returns are then obtained from changes in portfolio value.

The resulting daily return series is used to calculate performance metrics and estimate the portfolio's overall realized market beta.

## Results

### Performance Metrics

The simplified out-of-sample backtest produced the following results:

The simplified out-of-sample backtest produced the following results:

| Metric | Result |
|---|---:|
| Cumulative Return | -41.34% |
| Annualized Volatility | 21.99% |
| Maximum Drawdown | 47.02% |
| Annualized Sharpe Ratio | -0.69 |
| Realized Market Beta | -0.0542 |
| Beta Standard Error | 0.0390 |

### Performance Interpretation

The strategy generated very negative cumulative returns and experienced substantial drawdowns.

This suggests that selecting stocks based on historical CAPM alpha t-statistics did not produce a profitable trading strategy over the tested period.

However, profitability was not the primary objective of this investigation.(not an excuse)

### Hedge Effectiveness

The main objective was to evaluate whether historical CAPM beta estimates could be used to construct a portfolio with low out-of-sample market exposure.

An OLS regression of daily portfolio returns on market returns produced:

$$
\hat{\beta}_{\mathrm{realized}}=-0.0542
$$

with a standard error of:

$$
SE(\hat{\beta}_{\mathrm{realized}})=0.0390
$$

The corresponding t-statistic for testing $H_0:\beta=0$ is approximately -1.39, with a two-sided p-value of approximately 0.165 under conventional OLS assumptions.

Thus, the realized beta was not statistically significantly different from zero at the 5% significance level.

The relatively small estimated beta is consistent with the strategy's objective of limiting overall linear market exposure. However, failing to reject the zero-beta hypothesis does not prove perfect beta neutrality.

Despite its low overall realized beta, the portfolio experienced substantial losses and volatility. This highlights an important distinction: beta neutrality does not eliminate idiosyncratic risk or exposure to other risk factors.

## Limitations and Further Work

This project is a simplified investigation of beta hedging, rather than a fully realistic trading simulation.

Several limitations remain:

- **Trading assumptions:** Transaction costs, short borrow fees, financing costs, and execution slippage are not fully modeled.
- **Market proxy:** The S&P 500 price index is used alongside dividend-adjusted stock returns, creating a difference in return conventions.
- **Stock selection:** The fixed stock universe may introduce selection and survivorship biases.
- **Time-varying exposure:** A low full-period realized beta does not guarantee beta neutrality throughout the backtest.
- **Statistical assumptions:** Conventional OLS standard errors may be affected by heteroskedasticity and serial dependence.

Possible extensions include comparing hedged and unhedged portfolios, investigating rolling realized beta, and testing alternative estimation windows and rebalancing frequencies.


## Project Structure

```text
capm-market-neutral-strategy/
├── data/
│   ├── universe_raw.csv
│   ├── selected_stocks.csv
│   └── DGS3MO.csv
├── select_stock.py
├── main.py
├── strategy.py
├── backtesting.py
├── pyproject.toml
├── uv.lock
└── README.md

```

- `select_stock.py` constructs the cross-sector stock universe.
- `main.py` prepares the data and estimates the CAPM regressions.
- `strategy.py` selects the long-short pair and calculates beta-neutral portfolio weights.
- `backtesting.py` implements the rolling out-of-sample backtest.

## Running the Project

The project uses `uv` for Python environment and dependency management.

Clone the repository and install the dependencies:

```bash
uv sync
```

Run the CAPM analysis:

```bash
uv run python main.py
```

Run the backtest:

```bash
uv run python backtesting.py
```