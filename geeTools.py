import ee
import math
import numpy as np
from rasterio.warp import transform_bounds

from canty.eeWishart import omnibus

ee.Initialize()


# Calculate monthly changes between two dates
def calculate_monthly_changes(start_date, middle_date, final_date, poly, orbit, file_path, file_prefix='', export=False,
                              export_result=False,
                              sum_values=False):
    print('start: ' + start_date)
    print('middle: ' + middle_date)
    print('final: ' + final_date + '\n')

    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit)) \
        .filterBounds(poly)

    first_month = collection.filterDate(ee.Date(start_date), ee.Date(middle_date)).mean().clip(poly)
    second_month = collection.filterDate(ee.Date(middle_date), ee.Date(final_date)).mean().clip(poly)

    # If there are not enogh images in the month, return zero
    try:
        # Create a new ImageCollection with the two images
        collection = ee.ImageCollection.fromImages([first_month, second_month])
        # Obtain only VV and VH bands
        pcollection = collection.map(get_vvvh)

        # Convert to List
        p_list = pcollection.toList(2)

        first = ee.Dictionary({'imlist': ee.List([]), 'poly': poly, 'enl': ee.Number(4.4)})
        im_list = ee.Dictionary(p_list.iterate(clipList, first)).get('imlist')

        # make omnibus test for change detection
        result = ee.Dictionary(omnibus(im_list, useQ=True))

        result = ee.Image(result.get('cmap')).byte().clip(poly)

        if sum_values:
            value = result.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=poly,
                scale=10,
                maxPixels=1e9
            )
            # get and return the sum of all pixel values in image
            value = value.getInfo()
            value = int(value['VV'])
        else:
            value = 0

        if export_result:
            gdexport = ee.batch.Export.image.toDrive(
                result.toFloat(),
                description='changes_' + file_prefix + '_' + start_date + '_' + final_date,
                folder=file_path,
                maxPixels=1540907088,
                scale=10,
                region=poly
            )
            gdexport.start()

        if export:
            gdexport = ee.batch.Export.image.toDrive(
                first_month.toFloat(),
                description='SAR_' + start_date + '_' + middle_date,
                folder=file_path,
                maxPixels=1540907088,
                scale=10,
                region=poly
            )
            gdexport.start()



        return value



    except:
        print('error')
        return 0


# Calculate monthly changes between two months
def calculate_changes(initial_date, final_date, poly, orbit, file_path, file_prefix='', export=False,
                              export_result=False,
                              sum_values=False):
    print('start: ' + initial_date + '\n')
    print('final: ' + final_date + '\n')

    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filterBounds(poly)

    if orbit != 'both':
        collection = collection.filter(ee.Filter.eq('orbitProperties_pass', orbit))

    collection = collection.filterDate(ee.Date(initial_date), ee.Date(final_date))

    # If there are not enogh images in the month, return zero
    try:
        # Obtain only VV and VH bands
        pcollection = collection.map(get_vvvh)

        # Convert to List
        p_list = pcollection.toList(2)

        first = ee.Dictionary({'imlist': ee.List([]), 'poly': poly, 'enl': ee.Number(4.4)})
        im_list = ee.Dictionary(p_list.iterate(clipList, first)).get('imlist')

        # make omnibus test for change detection
        result = ee.Dictionary(omnibus(im_list, useQ=True))

        result = ee.Image(result.get('cmap')).byte().clip(poly)

        if sum_values:
            value = result.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=poly,
                scale=10,
                maxPixels=1e9
            )
            # get and return the sum of all pixel values in image
            value = value.getInfo()
            value = int(value['VV'])
        else:
            value = 0

        if export_result:
            gdexport = ee.batch.Export.image.toDrive(
                result.toFloat(),
                description='changes_' + file_prefix + '_' + initial_date + '_' + final_date,
                folder=file_path,
                maxPixels=1540907088,
                scale=10,
                region=poly
            )
            gdexport.start()

        return value

    except:
        print('error')
        return 0


def clip_ImageCollection(image, poly):
    return image.clip(poly)


def clipList(current, prev):
    ''' clip a list of images '''
    imlist = ee.List(ee.Dictionary(prev).get('imlist'))
    poly = ee.Dictionary(prev).get('poly')
    enl = ee.Number(ee.Dictionary(prev).get('enl'))
    imlist = imlist.add(ee.Image(current).multiply(enl).clip(poly))
    return ee.Dictionary({'imlist': imlist, 'poly': poly, 'enl': enl})


def get_vvvh(image):
    ''' get 'VV' and 'VH' bands from sentinel-1 imageCollection and restore linear signal from db-values '''
    return image.select('VV', 'VH').multiply(ee.Image.constant(math.log(10.0) / 10.0)).exp()


def pairwise(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b


def readGeoTiffAsRGB(path):
    import rasterio as rio
    # open the georaster and extract it's bands
    with rio.open(path) as geoimage:
        bounds = transform_bounds(geoimage.crs, "epsg:4326", *geoimage.bounds)
        r = geoimage.read(1)
        g = geoimage.read(2)
        b = geoimage.read(3)
    # convert the geo raster to numpy and plot
    image = np.dstack((r, g, b))
    return image, bounds


def cm_to_inch(value):
    return value / 2.54

def sliding_window(image, stepSize, windowSize):
  for y in range(0, image.shape[0], stepSize):
    for x in range(0, image.shape[1], stepSize):
      yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])