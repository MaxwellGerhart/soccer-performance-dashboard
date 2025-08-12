import pandas as pd

df = pd.read_csv('data/d1_player_stats.csv')

print('CSV columns:')
print(list(df.columns))

print(f'\nTop 5 players:')
print(df.head()[['Name', 'Team', 'Position', 'MAX']].to_string(index=False))

print(f'\nTotal players: {len(df)}')
print(f'Rating range: {df["MAX"].min()}-{df["MAX"].max()}')

print(f'\nElijah Jackson check:')
elijah = df[df['Name'] == 'Elijah Jackson']
if not elijah.empty:
    print(f'   {elijah.iloc[0]["Name"]} ({elijah.iloc[0]["Team"]}) - Rating: {elijah.iloc[0]["MAX"]}')
