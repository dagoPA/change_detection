from os import path
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt

data_path = 'data'

municipios = pd.read_csv(path.join(data_path, 'population_capitals.csv'))
weight = values = municipios['population'] * 10 / municipios['population'].sum()
municipios['weight'] = weight

# List of months for preparing the output
start_date = '2017-01-01'
end_date = '2021-12-01'
frequency = '1M'
dates = pd.date_range(start_date, end_date, freq=frequency) - pd.offsets.MonthBegin(1)
dates = dates.strftime("%Y-%m").values.tolist()[:-2]
data_output = []

headers = []

# Weight and prepare changes
max_value = 0
for i in range(len(municipios)):
    municipio = municipios.iloc[i]

    asc = pd.read_csv(path.join(data_path + '/gee_results', municipio.iloc[0] + '_ASCENDING_.csv')).iloc[:, 1].to_numpy()
    dsc = pd.read_csv(path.join(data_path + '/gee_results', municipio.iloc[0] + '_DESCENDING_.csv')).iloc[:, 1].to_numpy()
    changes = (asc + dsc) / 2
    weighted_changes = (changes * municipio['weight']).tolist()
    data_output.append(weighted_changes)
    headers.append(municipio.iloc[0])

# Convert to numpy and flip over the diagonal
data_output = np.rot90(np.fliplr(np.array(data_output)))

# Normalize data
data_output = normalize(data_output, axis=0)

data_output = pd.DataFrame(data=data_output, index=dates, columns=headers)

# Save as csv
data_output.to_csv(path.join(data_path, 'normalized_change_index.csv'))
print('eof')
