import pandas as pd

df = pd.read_csv('data/universe_raw.csv')

def sector_sorter(sector_name):
    sector_mask = df['Sector'] == sector_name
    sector_stock = df[sector_mask]
    sector_stock_sorted = sector_stock.sort_values('Market Cap',ascending = False)
    return sector_stock_sorted[['Symbol', 'Name', 'Sector', 'Market Cap']].head(10)

sectors = []
for seci in df['Sector'].dropna():
    if seci not in sectors and seci != 'Miscellaneous':
        sectors.append(seci)

candidates = []
for i in sectors:
    sector_candidates = sector_sorter(i)
    candidate_1 = sector_candidates.iloc[0]
    candidate_2 = sector_candidates.iloc[1]
    candidates.append(candidate_1)
    candidates.append(candidate_2)

candidate_table = pd.DataFrame(candidates)
candidate_table = candidate_table.reset_index(drop=True)

print(candidate_table)