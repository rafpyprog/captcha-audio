import pandas as pd

log = 'log.txt'

def top_performance(logfile=log, n=10):
    names = ['duration', 'threshold', 'performance']
    df = pd.read_csv(logfile, sep=';', names=names)
    df = df.sort_values(by='performance', ascending=False).reset_index(drop=True)
    return df.head(n)

df = top_performance(n=10)
df


df['duration'].min()
df['duration'].max()
df['duration'].mean()
