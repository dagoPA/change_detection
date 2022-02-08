from pathlib import Path
import ee
import geeTools as geet

# Begin Params

orbits = ['ASCENDING', 'DESCENDING']
gdrive_folder = 'cdmx_2021'
initial_date = '2021-01-01'
final_date = '2022-01-01'
local_data_dir = 'data/gee_results'
# End Params

# Get the polygon of mexico City
cdmx = ee.FeatureCollection("projects/ee-vulnerability-gee4geo/assets/cdmx").first().geometry()

sum = geet.calculate_changes(initial_date, final_date, cdmx, 'both', gdrive_folder, file_prefix='cdmx',
                                 export_result=True)

print('end of file')
