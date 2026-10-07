###
#Ideas of this toy strategy
#Stocks with relatively stronger  alpha evidence might outperform stocks with relatively weaker alpha evidence in the future.
#Use beta to find hedging factor to minimize the exposure to market
###
import pandas as pd

def make_pair(resdf):
    i = resdf['alpha_t'].idxmax()
    j = resdf['alpha_t'].idxmin()
    return({
        'long_what' : resdf['ticker'].loc[i],
        'short_what' : resdf['ticker'].loc[j],
        'long_w' : resdf['beta'].loc[j]/(resdf['beta'].loc[j]+resdf['beta'].loc[i]),
        'short_w' : -resdf['beta'].loc[i]/(resdf['beta'].loc[j]+resdf['beta'].loc[i]),
    })
