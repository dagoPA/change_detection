from pathlib import Path
import ee
import geeTools as geet
import pandas as pd
import os

data_path = '/data/cdmx_SAR'
imsar_path = 'cdmx_BOTH'

im_list = sorted(os.listdir(os.path.join(data_path, imsar_path)))

cmd = 'docker exec -it ac0c91124f2c python scripts/sar_seqQ.py -s 0.0001'
for im_a, im_b in geet.pairwise(im_list):
    cmd = cmd + os.path.join(' myimagery', imsar_path, im_a)
    cmd = cmd + os.path.join(' myimagery', imsar_path, im_b)
    cmd = cmd + ' result/change' + (im_a[7:17] + '_' + im_b[18:28]).replace('-', '_') + '.tif'
    print(cmd)
    os.system(cmd)

print('process completed')
