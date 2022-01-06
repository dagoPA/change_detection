from os import path
import numpy as np
import pandas as pd
import impyute as impy
from matplotlib import pyplot as plt
plt.close("all")
data_path = 'data'

# read geographic information for capitals
municipios = pd.read_csv(path.join(data_path, 'population_capitals.csv'))

# population density
municipios['density'] = municipios['population'] / municipios['area']

# List of months for preparing the output
start_date = '2017-01-01'
end_date = '2022-03-01'
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

data_output = pd.DataFrame(data=data_output, index=dates, columns=headers)

# Multiply monthly values by density
change_index = []
for index, row in data_output.iterrows():
    monthly_total = 0
    for i, v in row.iteritems():
        monthly_total = monthly_total + (v * float(municipios[municipios['capital'] == i]['density']))
    monthly_total = monthly_total/len(row)
    change_index.append(monthly_total)

# Save as csv
data_output['change_index'] = change_index
data_output['change_index'].to_csv(path.join(data_path, 'change_index.csv'))

capitals = data_output.drop('change_index', 1)
# plot
plt.plot(capitals)
plt.xticks(rotation=80, ha='right')
plt.show()


print('eof')
