import pandas as pd

df = pd.read_csv('data/ncaa_ratings.csv')
print('DEF Rating Distribution:')
print(f'Min (best): {df["DEF"].min():.2f}')
print(f'Max (worst): {df["DEF"].max():.2f}')
print(f'Mean: {df["DEF"].mean():.2f}')

print('\nUSC Upstate:')
usc = df[df['Team'].str.contains('USC Upstate', case=False, na=False)]
if not usc.empty:
    print(usc[['Team', 'DEF']].to_string(index=False))
else:
    print('Not found')

print('\nBest 5 defenses (lowest DEF):')
print(df.nsmallest(5, 'DEF')[['Team', 'DEF']].to_string(index=False))

print('\nWorst 5 defenses (highest DEF):')
print(df.nlargest(5, 'DEF')[['Team', 'DEF']].to_string(index=False))
