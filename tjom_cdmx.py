from pathlib import Path
import ee
import geeTools as geet

# Begin Params

orbits = ['ASCENDING', 'DESCENDING']
gdrive_folder = 'changes_cdmx_1m'
initial_date = '2021-01-01'
final_date = '2022-01-01'
local_data_dir = 'data/gee_results'
# End Params

# Get the polygon of mexico City
cdmx = table = ee.FeatureCollection("projects/ee-vulnerability-gee4geo/assets/cdmx").first().geometry()

for orbit_ in orbits:
    my_file = Path(local_data_dir + orbit_ + '_' + '.csv')
    sum = geet.calculate_changes(initial_date, final_date, cdmx, orbit_, 'cdmx_2021', file_prefix='cdmx_'+orbit_,
                                 export_result=True)

print('end of file')
