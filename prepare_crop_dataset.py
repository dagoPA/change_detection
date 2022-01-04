import geeTools
import matplotlib.pyplot as plt

data_path = '/home/dagopa/data/SAR/'

im = geeTools.readGeoTiffAsRGB(data_path + 'SAR_2019-07-01_2019-08-01.tif')
plt.imshow(im[0])
plt.show()

print('eof')
