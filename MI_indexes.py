import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
# read datasets
changes = pd.read_csv('data/normalized_change_index.csv', index_col=0)['national_weighted_index'].tolist()
indexes = pd.read_csv('data/BIE_BIE20211217163133.csv').loc[289:345]

indexes[changes] = changes
indexes = indexes.iloc[:, 1:].fillna(0)

corrMatrix = indexes.corr()
sn.heatmap(corrMatrix, annot=True)
plt.show()

print('eof')
