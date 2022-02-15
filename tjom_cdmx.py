from pathlib import Path
import ee
import geeTools as geet
import pandas as pd
# Begin Params

orbits = ['ASCENDING', 'DESCENDING', 'both']
gdrive_folder = 'cdmx_2021'
initial_date = '2020-01-01'
final_date = '2022-01-01'
local_data_dir = 'data/gee_results'
frequency = 14
# End Params

# Get the polygon of mexico City
cdmx = ee.FeatureCollection("projects/ee-vulnerability-gee4geo/assets/cdmx").first().geometry()

geet.calculate_changes(initial_date, final_date, orbits[0], frequency, cdmx, gdrive_folder, file_prefix='changes_cdmx', export_result=False, export=True)

print('end of file')
