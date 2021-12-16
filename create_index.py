from os import path
import numpy as np
import pandas as pd
from sklearn.preprocessing import normalize
import impyute as impy

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
    data_output.append(changes)
    headers.append(municipio.iloc[0])

# Convert to numpy and flip over the diagonal
data_output = np.rot90(np.fliplr(np.array(data_output)))

# Impute zeros
data_output[data_output == 0] = 'Nan'
data_output = impy.em(data_output)

# Normalize data
data_output = np.abs(normalize(data_output, axis=0))

data_output = pd.DataFrame(data=data_output, index=dates, columns=headers)

# Create national weighted index
nwci = []
for index, row in data_output.iterrows():
    monthly_total = 0
    for i, v in row.iteritems():
        monthly_total = monthly_total + (v * float(municipios[municipios['capital'] == i]['weight']))

    nwci.append(monthly_total)

# Save as csv
data_output['national_weighted_index'] = nwci
data_output.to_csv(path.join(data_path, 'normalized_change_index.csv'))
print('eof')
