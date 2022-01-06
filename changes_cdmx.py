from pathlib import Path
import pandas as pd
import ee
import geeTools as geet

# Begin Params

orbits = ['ASCENDING', 'DESCENDING']
gdrive_folder = 'changes_cdmx_1m'
start_date = '2017-01-01'
end_date = '2022-03-01'
frequency = '1M'
local_data_dir = 'data/gee_results'
# End Params

# Get list of dates
dates = pd.date_range(start_date, end_date, freq=frequency) - pd.offsets.MonthBegin(1)
dates = dates.strftime("%Y-%m-%d").values.tolist()

# Get the list of municipios
cdmx = table = ee.FeatureCollection("projects/ee-vulnerability-gee4geo/assets/cdmx").first().geometry()

for orbit_ in orbits:
    my_file = Path(local_data_dir + orbit_ + '_' + '.csv')

    changes = []
    # Calculate changes, comparing each month against the next one
    for i in range(2, len(dates)):
        sum = geet.calculate_monthly_changes(dates[i - 2], dates[i - 1], dates[i], cdmx, orbit_, 'test_SAR',
                                             file_prefix='cdmx',
                                             export=False, sum_values=True)
        changes.append(sum)

    dict = {'cdmx' + '_' + orbit_: changes}
    df = pd.DataFrame(dict)
    df.to_csv(local_data_dir + '/' + 'cdmx' + '_' + orbit_ + '_' + '.csv')


print('end of file')
