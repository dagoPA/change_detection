import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# read datasets
changes = pd.read_csv('data/change_index.csv', index_col=0)['change_index'].tolist()
indexes = pd.read_csv('data/BIE_BIE20211217163133.csv', index_col=0)

indexes[changes] = changes
indexes = indexes.iloc[:, : 42].fillna(0)



indexes['idx'] = changes
corr = indexes.corr()
sns.heatmap(corr)
plt.savefig('indicators.png')

print('eof')
